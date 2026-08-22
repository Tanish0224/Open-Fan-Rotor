"""
blade_geometry.py -- BA-OF-01 3-D blade geometry generator.

Converts the Phase 1 radial design table into 3-D section curves ready for
SolidWorks, and computes an INDEPENDENT analytical volume that the CAD is later
verified against.

NO DIMENSION IS TYPED BY HAND. Every number here is read from
01_design/results/design_table.csv, which is itself produced by the BEM design.

COORDINATE SYSTEM  [DESIGN DECISION, fixed here and used everywhere downstream]
------------------------------------------------------------------------------
    global +Z  : rotor axis, pointing DOWNSTREAM (thrust acts in -Z on the fluid)
    global +X  : radial, the reference blade lies along +X
    global +Y  : tangential at the reference blade (direction of rotation)

    A section at radius r lies in the local (tangential, axial) = (Y, Z) plane.
    Blade angle beta is measured from the ROTOR PLANE (the tangential direction)
    toward the axial direction -- the standard propeller convention.

    Sections are stacked about the 50 % chord point [DESIGN DECISION], the usual
    propfan stacking choice.

    Sweep is applied as a TANGENTIAL offset of the stacking point:
        y_sweep(r) = Integral_{r_root}^{r} tan(Lambda(r')) dr'
    i.e. the blade sweeps back opposite to the direction of rotation.

ROOT AND TIP TREATMENT  [DESIGN DECISION -- a documented deviation from pure BEM]
--------------------------------------------------------------------------------
Adkins-Liebeck drives chord to ZERO at both the hub and the tip, because the
Prandtl loss factor F -> 0 at both ends. A real blade cannot have zero chord at
its root (it has to attach) nor a zero-thickness knife tip.

Therefore the AERODYNAMIC blade is built between r/R = R_START and R_END, and the
load carried outside that band is quantified and reported. It is not silently
discarded.
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).parent
DESIGN = HERE.parent / "01_design"
sys.path.insert(0, str(DESIGN))
from openfan_design import naca4_section  # noqa: E402

OUT = HERE / "geometry"
OUT.mkdir(parents=True, exist_ok=True)

# --- blade extent [DESIGN DECISION] ---------------------------------------------
R_START = 0.32     # r/R where the aerodynamic blade begins (inside this: shank/spinner)
R_END = 0.985      # r/R where the aerodynamic blade ends (outside this: rounded tip)
N_CAD_SECTIONS = 21   # sections lofted through
N_SECTION_PTS = 101   # points per section before resampling
N_SKETCH_PTS = 48     # points per SolidWorks sketch contour after arc-length
                      # resampling. DIAGNOSED LIMIT: 48 lofts cleanly through all
                      # 21 profiles; 64 fails. Many short, nearly-collinear
                      # segments inside a sketch whose extent is ~0.7 m (the sweep
                      # offset) defeat SolidWorks' contour detection. See
                      # diag_point_threshold.json.


def load_design_table(path: pathlib.Path) -> dict:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def section_area_coefficient(m: float, p: float, t: float) -> float:
    """Enclosed area of a unit-chord NACA 4-digit section. [DERIVED] exact numeric."""
    pts = naca4_section(m, p, t, n_pts=601)
    x, y = pts[:, 0], pts[:, 1]
    # shoelace on the closed polygon
    return 0.5 * abs(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


class BladeGeometry:
    def __init__(self, table: dict, summary: dict):
        self.t = table
        self.s = summary
        self.R = summary["operating_point"]["R_m"]
        self.B = summary["blade_count_selected"]
        self._build()

    # -- interpolate the design onto the CAD stations -----------------------------
    def _interp(self, key, xi):
        return np.interp(xi, self.t["r_over_R"], self.t[key])

    def _build(self):
        self.xi = np.linspace(R_START, R_END, N_CAD_SECTIONS)
        self.r = self.xi * self.R
        self.chord = self._interp("chord_m", self.xi)
        self.beta = np.radians(self._interp("beta_deg", self.xi))
        self.toc = self._interp("toc", self.xi)
        self.camber_m = self._interp("camber_m", self.xi)
        self.camber_p = self._interp("camber_p", self.xi)
        self.sweep = np.radians(self._interp("sweep_deg", self.xi))

        # sweep offset: cumulative integral of tan(Lambda) dr  [DERIVED]
        tanL = np.tan(self.sweep)
        self.y_sweep = np.concatenate([[0.0], np.cumsum(
            0.5 * (tanL[1:] + tanL[:-1]) * np.diff(self.r))])

        # independent analytical blade volume  [DERIVED] -- the CAD verification target
        area_coef = np.array([section_area_coefficient(m, p, t)
                              for m, p, t in zip(self.camber_m, self.camber_p, self.toc)])
        self.section_area = area_coef * self.chord ** 2          # m^2
        self.volume_one_blade = float(np.trapezoid(self.section_area, self.r))
        self.volume_all_blades = self.volume_one_blade * self.B

        # load carried outside the CAD blade extent  [DERIVED] -- honesty check
        xi_full, dTdr = self.t["r_over_R"], self.t["dT_dr_Npm"]
        r_full = xi_full * self.R
        T_full = float(np.trapezoid(dTdr, r_full))
        mask = (xi_full >= R_START) & (xi_full <= R_END)
        T_kept = float(np.trapezoid(dTdr[mask], r_full[mask]))
        self.thrust_full_span_N = T_full
        self.thrust_cad_span_N = T_kept
        self.thrust_excluded_pct = 100.0 * (T_full - T_kept) / T_full

    # -- 3-D section curves -------------------------------------------------------
    def section_points(self, i: int) -> np.ndarray:
        """(N,3) points of section i in GLOBAL coordinates, metres."""
        pts = naca4_section(float(self.camber_m[i]), float(self.camber_p[i]),
                            float(self.toc[i]), n_pts=N_SECTION_PTS)
        c = float(self.chord[i])
        # stack about 50 % chord [DESIGN DECISION]
        xc = (pts[:, 0] - 0.5) * c
        yc = pts[:, 1] * c
        b = float(self.beta[i])
        # chord line lies at angle beta from the rotor (tangential) plane
        y = xc * np.cos(b) - yc * np.sin(b) + float(self.y_sweep[i])
        z = xc * np.sin(b) + yc * np.cos(b)
        x = np.full_like(y, float(self.r[i]))
        return np.column_stack([x, y, z])

    def section_points_sketch(self, i: int, n: int = N_SKETCH_PTS) -> np.ndarray:
        """
        Section i resampled UNIFORMLY IN ARC LENGTH to n points, closed exactly.
        This is what the SolidWorks sketches are built from -- uniform arc-length
        spacing guarantees no sub-tolerance segment, which was the documented
        cause of the loft failures.
        """
        p3 = self.section_points(i)
        ab = p3[:, 1:3]
        d = np.r_[0.0, np.cumsum(np.hypot(*np.diff(ab, axis=0).T))]
        s = np.linspace(0.0, d[-1], n, endpoint=False)
        out = np.column_stack([np.interp(s, d, ab[:, 0]), np.interp(s, d, ab[:, 1])])
        return np.vstack([out, out[0]])

    def write_sldcrv(self, outdir: pathlib.Path, scale: float = 1000.0) -> list[pathlib.Path]:
        """
        SolidWorks 'Curve Through XYZ Points' files.

        A .sldcrv file is interpreted in the DOCUMENT's length units, so the scale
        must match the part template. Default scale is 1000 (metres -> millimetres)
        for an MMGS template. The CAD script does NOT assume this is correct: it
        verifies the resulting bounding box against the analytically-known blade
        dimensions, so a unit error is detected rather than propagated.
        """
        outdir.mkdir(parents=True, exist_ok=True)
        paths = []
        for i in range(N_CAD_SECTIONS):
            p = outdir / f"sec_{i:02d}.sldcrv"
            pts = self.section_points(i) * scale
            with open(p, "w", encoding="ascii", newline="\r\n") as f:
                for x, y, z in pts:
                    f.write(f"{x:.6f}\t{y:.6f}\t{z:.6f}\n")
            paths.append(p)
        return paths

    def spinner_profile(self, n: int = 60) -> np.ndarray:
        """
        Spinner/hub half-profile in the (z, radius) plane. [DESIGN DECISION]
        An ogive nose closing onto the hub cylinder at the blade root.
        """
        r_hub = self.s["operating_point"]["R_hub_m"]
        L_nose = 1.6 * r_hub        # [DESIGN DECISION] ogive fineness
        L_aft = 1.2 * r_hub         # [DESIGN DECISION] cylindrical run aft of the blades
        z_nose = np.linspace(-L_nose, 0.0, n)
        rad = r_hub * np.sqrt(np.clip(1.0 - (z_nose / L_nose) ** 2, 0.0, None))
        z = np.concatenate([z_nose, [L_aft]])
        rad = np.concatenate([rad, [r_hub]])
        rad[0] = 1.0e-4             # avoid an exactly-degenerate apex
        return np.column_stack([z, rad])

    def report(self) -> dict:
        return {
            "coordinate_system": {
                "axis": "+Z downstream", "radial_reference_blade": "+X",
                "tangential": "+Y", "units": "metres",
                "beta_convention": "from rotor plane (tangential) toward axial",
                "stacking": "50 % chord",
            },
            "blade_extent": {
                "r_over_R_start": R_START, "r_over_R_end": R_END,
                "n_cad_sections": N_CAD_SECTIONS, "n_points_per_section": N_SECTION_PTS,
                "NOTE": "Adkins-Liebeck drives chord to zero at hub and tip; the "
                        "aerodynamic blade is built between these limits and the "
                        "excluded load is quantified below.",
            },
            "geometry": {
                "n_blades": self.B, "R_m": self.R,
                "R_hub_m": self.s["operating_point"]["R_hub_m"],
                "chord_root_cad_m": float(self.chord[0]),
                "chord_max_m": float(np.max(self.chord)),
                "chord_tip_cad_m": float(self.chord[-1]),
                "beta_root_cad_deg": float(np.degrees(self.beta[0])),
                "beta_tip_cad_deg": float(np.degrees(self.beta[-1])),
                "sweep_tip_deg": float(np.degrees(self.sweep[-1])),
                "tangential_sweep_offset_tip_m": float(self.y_sweep[-1]),
            },
            "INDEPENDENT_VOLUME_TARGET": {
                "one_blade_m3": self.volume_one_blade,
                "all_blades_m3": self.volume_all_blades,
                "method": "numerical integration of exact NACA 4-digit section areas "
                          "along the span -- computed WITHOUT SolidWorks, and used as "
                          "the independent target for CAD verification (gate G1)",
                "CAVEAT": "this target neglects the small volume change caused by "
                          "section rotation and sweep along a curved stacking line; a "
                          "few-percent CAD-vs-analytical difference is expected and the "
                          "acceptance band is set accordingly",
            },
            "load_excluded_by_cad_truncation": {
                "thrust_full_span_N": self.thrust_full_span_N,
                "thrust_cad_span_N": self.thrust_cad_span_N,
                "excluded_pct": self.thrust_excluded_pct,
            },
        }


def main():
    tbl = load_design_table(DESIGN / "results" / "design_table.csv")
    summ = json.load(open(DESIGN / "results" / "design_summary.json", encoding="utf-8"))
    bg = BladeGeometry(tbl, summ)
    paths = bg.write_sldcrv(OUT / "curves")
    rep = bg.report()
    with open(OUT / "blade_geometry.json", "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)

    # a single combined point cloud, useful for a quick visual check
    allpts = np.vstack([bg.section_points(i) for i in range(N_CAD_SECTIONS)])
    np.savetxt(OUT / "blade_pointcloud.csv", allpts, delimiter=",",
               header="x_m,y_m,z_m", comments="")
    np.savetxt(OUT / "spinner_profile.csv", bg.spinner_profile(), delimiter=",",
               header="z_m,radius_m", comments="")

    print("BA-OF-01  blade geometry")
    print(f"  blades                       : {rep['geometry']['n_blades']}")
    print(f"  CAD span                     : r/R {R_START} -> {R_END}")
    print(f"  sections written             : {len(paths)}")
    print(f"  chord (root/max/tip) [m]     : {rep['geometry']['chord_root_cad_m']:.4f} / "
          f"{rep['geometry']['chord_max_m']:.4f} / {rep['geometry']['chord_tip_cad_m']:.4f}")
    print(f"  beta  (root -> tip) [deg]    : {rep['geometry']['beta_root_cad_deg']:.2f} -> "
          f"{rep['geometry']['beta_tip_cad_deg']:.2f}")
    print(f"  tip sweep [deg]              : {rep['geometry']['sweep_tip_deg']:.2f}")
    print(f"  tangential sweep offset [m]  : {rep['geometry']['tangential_sweep_offset_tip_m']:.4f}")
    print(f"  INDEPENDENT volume target    : {bg.volume_one_blade*1e6:.2f} cm^3 per blade, "
          f"{bg.volume_all_blades*1e6:.2f} cm^3 total")
    print(f"  thrust excluded by truncation: {bg.thrust_excluded_pct:.3f} %")
    print(f"  curves -> {OUT/'curves'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
