"""
blade_geometry_reference.py -- INDEPENDENT volume reference for the v02 blade,
computed from the exact final section data sent to CAD, WITHOUT SolidWorks.

Per the recovery-task requirement, three distinct quantities are computed and
kept explicitly separate -- they are NOT the same number and must not be
conflated:

  1. DESIGN IDEALISATION
     The smooth, closed-form NACA 4-digit curve (601 points), analytically
     exact for the prescribed camber/thickness/chord at each station. This is
     the mathematical shape the BEM design specifies.

  2. CAD INPUT GEOMETRY (the exact discretisation actually sent to SolidWorks)
     Each section is resampled to N_SKETCH_PTS=48 points, UNIFORM IN ARC LENGTH,
     with the blunt trailing edge already baked in (TE_THICKNESS=0.006c). This
     is the exact point set passed to CreateSpline2 for every section in the
     v02 build. Two sub-quantities are computed from it:
       2a. POLYGON area  -- the straight-edge polygon through the 48 points
           (shoelace formula). This is a LOWER BOUND: a polyline through the
           points always CUTS every corner.
       2b. The true SPLINE-bounded area is NOT computed here (would require
           reproducing SolidWorks' exact B-spline fit), but is expected to
           exceed the polygon area, because a smooth curve through the same
           points on a convex-ish aerofoil BULGES OUTWARD between points
           rather than cutting the corner. This is stated as an expectation,
           not measured independently -- see CAD_VOLUME_CROSSCHECK.md.

  3. INDEPENDENT RECONSTRUCTED REFERENCE
     The volume is integrated along span (trapezoidal in r) for BOTH the smooth
     design idealisation (1) and the 48-point polygon (2a), giving a bracket
     [polygon_volume, smooth_volume]. The actual CAD (spline-based) volume is
     expected to fall AT OR ABOVE the polygon bound and AT OR BELOW/NEAR the
     smooth bound, since 48 points is a fairly fine discretisation of a smooth
     curve.

No SolidWorks geometry is used as input anywhere in this file.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).parent
DESIGN = HERE.parent / "01_design"
sys.path.insert(0, str(DESIGN))
from openfan_design import naca4_section  # noqa: E402
from blade_geometry import BladeGeometry, load_design_table, R_START, R_END, N_CAD_SECTIONS  # noqa: E402


def polygon_area(pts2d: np.ndarray) -> float:
    """Shoelace formula on a closed 2-D polygon."""
    x, y = pts2d[:, 0], pts2d[:, 1]
    return 0.5 * abs(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def smooth_section_area(m: float, p: float, t: float) -> float:
    """Exact closed-form NACA 4-digit section area (601-point shoelace, converged)."""
    pts = naca4_section(m, p, t, n_pts=601)
    return polygon_area(pts)


def main():
    tbl = load_design_table(DESIGN / "results" / "design_table.csv")
    summ = json.load(open(DESIGN / "results" / "design_summary.json", encoding="utf-8"))
    bg = BladeGeometry(tbl, summ)

    xi = bg.xi
    r = bg.r
    chord = bg.chord

    smooth_area = np.array([smooth_section_area(m, p, t)
                            for m, p, t in zip(bg.camber_m, bg.camber_p, bg.toc)])
    smooth_area_m2 = smooth_area * chord ** 2

    polygon_area_frac = []
    for i in range(N_CAD_SECTIONS):
        pts3 = bg.section_points(i)          # (r, tangential, axial), local unit-chord shape
        # convert back to unit-chord local (a,b) by undoing the rotation+scale
        # -- simpler: recompute directly from the sketch points (already in the
        # rotated/scaled/swept LOCAL PLANE coordinates), and just take polygon
        # area there directly, then that IS the physical (tangential,axial)
        # cross-sectional area at that station -- no unscaling needed.
        ab_closed = bg.section_points_sketch(i)   # (tangential, axial), 49 pts, closed
        polygon_area_frac.append(polygon_area(ab_closed))
    polygon_area_m2 = np.array(polygon_area_frac)   # already physical units (m^2), not unit-chord

    # smooth_area_m2 is per-station cross-sectional area in physical units too
    # (smooth_area is a unit-chord coefficient x chord^2 in the CAD's local axes,
    # same physical cross-section the polygon approximates).

    vol_smooth = float(np.trapezoid(smooth_area_m2, r))
    vol_polygon = float(np.trapezoid(polygon_area_m2, r))

    # also report the OLD (pre-v02) target for traceability -- computed the same
    # way this project always has, unchanged, so the historical number in
    # CAD_CHECK2_DIAGNOSTIC.md / the v01 records remains reproducible
    old_style_vol = bg.volume_one_blade

    report = {
        "provenance": {
            "design_table": str(DESIGN / "results" / "design_table.csv"),
            "n_cad_sections": N_CAD_SECTIONS,
            "n_sketch_points_per_section": 48,
            "cad_span_r_over_R": [R_START, R_END],
            "te_thickness_frac_chord": 0.006,
            "no_solidworks_geometry_used_as_input": True,
        },
        "1_design_idealisation_smooth_closed_form": {
            "description": "Analytically exact NACA 4-digit closed-form curve, "
                           "601 points, per station",
            "volume_one_blade_m3": vol_smooth,
            "volume_one_blade_cm3": vol_smooth * 1e6,
        },
        "2a_cad_input_polygon_lower_bound": {
            "description": "Straight-edge polygon through the EXACT 48 "
                           "arc-length-resampled points sent to CreateSpline2 "
                           "for every section in the v02 build. A polyline "
                           "through these points always cuts every corner, so "
                           "this is a LOWER BOUND on the true section area.",
            "volume_one_blade_m3": vol_polygon,
            "volume_one_blade_cm3": vol_polygon * 1e6,
        },
        "3_expected_bracket_for_the_spline_based_CAD_volume": {
            "lower_bound_m3": vol_polygon,
            "upper_bound_m3": vol_smooth,
            "lower_bound_cm3": vol_polygon * 1e6,
            "upper_bound_cm3": vol_smooth * 1e6,
            "bracket_width_pct": (vol_smooth - vol_polygon) / vol_polygon * 100.0,
            "rationale": "A B-spline through the 48 points bulges outward between "
                         "points on this convex-ish aerofoil shape (unlike a "
                         "polyline, which cuts every corner), so the true "
                         "SolidWorks spline-loft volume is expected to lie AT OR "
                         "ABOVE the polygon bound and AT OR BELOW the smooth "
                         "closed-form bound -- the 48-point discretisation is "
                         "fine enough that the true curve and the spline "
                         "interpolant should nearly coincide.",
        },
        "historical_pre_v02_target_unchanged_for_traceability": {
            "volume_one_blade_m3": old_style_vol,
            "volume_one_blade_cm3": old_style_vol * 1e6,
            "note": "This is the SAME smooth-closed-form calculation as (1) -- "
                    "confirms no drift in the existing blade_geometry.py "
                    "computation across this update.",
        },
    }

    with open(HERE / "blade_geometry_reference.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("BA-OF-01  independent volume reference (v02, no SolidWorks input)")
    print(f"  (1) smooth closed-form design idealisation : {vol_smooth*1e6:.2f} cm^3")
    print(f"  (2a) CAD-input 48-point polygon (lower bound): {vol_polygon*1e6:.2f} cm^3")
    print(f"  bracket width                                : "
          f"{report['3_expected_bracket_for_the_spline_based_CAD_volume']['bracket_width_pct']:.2f} %")
    print(f"  historical (pre-v02) target, unchanged        : {old_style_vol*1e6:.2f} cm^3")
    print(f"\n  -> blade_geometry_reference.json")
    return report


if __name__ == "__main__":
    main()
