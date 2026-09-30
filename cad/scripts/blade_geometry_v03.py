"""
blade_geometry_v03.py -- BA-OF-01 v03 blade geometry: RADIUS-PRESERVING CYLINDRICAL SWEEP.

NEW FILE. `blade_geometry.py` (v02) is NOT modified and remains the historical baseline.

WHAT CHANGED FROM v02, AND WHY  (see 02_cad/verification/SWEEP_MODEL_ENGINEERING_AUDIT.md)
-------------------------------------------------------------------------------------------
ED-015 defines sweep as an ANGLE:  Lambda(r) = arccos(M_cap / M_hel(r)),  M_cap = 0.78.
v02's generator realized that angle as a CARTESIAN tangential offset, y_sweep = INT tan(Lam) dr,
while holding x = r. That implementation:
  * realized only 22.45 deg of the designed 44.19 deg sweep at the tip (error -21.74 deg),
  * grew true radius sqrt(x^2+y^2) to 1.8789 m, +7.37 % beyond the design R = 1.75 m,
  * therefore VIOLATED the very M_n <= 0.78 cap that generated Lambda (M_n -> 0.818),
  * and inflated swept disk area +15.3 %, invalidating C_T, C_P, J, eta.

Because INT tan(Lam) dr is dimensionally an ARC LENGTH, the faithful cylindrical form is

        dtheta/dr = tan(Lambda(r)) / r        =>      theta(r) = INT_r_root^r tan(Lam)/r' dr'

This REUSES ED-015's Lambda(r) EXACTLY. No new sweep distribution is introduced. Chord, twist,
thickness, airfoil family, radial stations, blade count (B = 16, ED-014) and pitch (22.5 deg) are
all unchanged and are read from the same frozen design table as v02.

DESIGN COORDINATE SYSTEM  (unchanged from v02)
    global +Z : rotor axis, downstream        global +X : radial reference
    global +Y : tangential (direction of rotation)

SECTION PLACEMENT (v03)
    u = xc cos(beta) - yc sin(beta)     # tangential offset from the stacking point
    w = xc sin(beta) + yc cos(beta)     # axial
    X = r cos(theta) - u sin(theta)
    Y = r sin(theta) + u cos(theta)
    Z = w
Twist beta is applied in the LOCAL tangential/axial frame BEFORE the azimuthal rotation, so the
azimuthal placement cannot contaminate pitch or twist.

CAD CONSTRUCTION NOTE
    v02 built each section as a PLANAR sketch on a constant-X plane offset from the Right Plane.
    That is no longer geometrically possible: with radius-preserving sweep each section lies at a
    different azimuth theta(r), so its plane normal is the local radial direction r_hat(theta),
    not global X. v03 therefore builds each section as a 3-D SKETCH carrying true global
    coordinates, which removes the local->global mapping step entirely -- and with it the entire
    class of mapping defect that produced v02's failure. The resulting orientation is still
    VERIFIED against these equations by gate G1' rather than assumed (sketch placement is only
    trusted after coordinate readback).
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).parent
DESIGN = HERE.parent / "01_design"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(DESIGN))

from blade_geometry import (load_design_table, section_area_coefficient,   # noqa: E402
                            R_START, R_END, N_CAD_SECTIONS, N_SECTION_PTS, N_SKETCH_PTS)
from openfan_design import naca4_section                                    # noqa: E402


class BladeGeometryV03:
    """v03 blade: identical design inputs to v02, radius-preserving cylindrical sweep."""

    def __init__(self, table: dict, summary: dict):
        self.t, self.s = table, summary
        self.R = summary["operating_point"]["R_m"]
        self.B = summary["blade_count_selected"]
        self._build()

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
        self.sweep = np.radians(self._interp("sweep_deg", self.xi))   # ED-015 Lambda(r), UNCHANGED

        # --- v03 SWEEP: angular law derived from the SAME ED-015 Lambda(r) -------------
        # dtheta/dr = tan(Lambda)/r   (arc-length interpretation of INT tan(Lam) dr)
        integ = np.tan(self.sweep) / self.r
        self.theta = np.concatenate([[0.0], np.cumsum(
            0.5 * (integ[1:] + integ[:-1]) * np.diff(self.r))])        # [rad], theta(root) = 0

        # v02's Cartesian offset, retained ONLY for reporting/comparison -- never used to build
        tanL = np.tan(self.sweep)
        self.y_sweep_v02 = np.concatenate([[0.0], np.cumsum(
            0.5 * (tanL[1:] + tanL[:-1]) * np.diff(self.r))])

        # independent analytical volume (identical basis to v02 -- sections are unchanged)
        area_coef = np.array([section_area_coefficient(m, p, t)
                              for m, p, t in zip(self.camber_m, self.camber_p, self.toc)])
        self.section_area = area_coef * self.chord ** 2
        self.volume_one_blade = float(np.trapezoid(self.section_area, self.r))
        self.volume_all_blades = self.volume_one_blade * self.B

    # -- 3-D section curves in TRUE GLOBAL DESIGN COORDINATES ------------------------
    def section_points(self, i: int, n_pts: int = N_SECTION_PTS) -> np.ndarray:
        pts = naca4_section(float(self.camber_m[i]), float(self.camber_p[i]),
                            float(self.toc[i]), n_pts=n_pts)
        c, b, r, th = (float(self.chord[i]), float(self.beta[i]),
                       float(self.r[i]), float(self.theta[i]))
        xc = (pts[:, 0] - 0.5) * c          # stack about 50 % chord [DESIGN DECISION, from v02]
        yc = pts[:, 1] * c
        u = xc * np.cos(b) - yc * np.sin(b)     # tangential offset from stacking point
        w = xc * np.sin(b) + yc * np.cos(b)     # axial
        X = r * np.cos(th) - u * np.sin(th)
        Y = r * np.sin(th) + u * np.cos(th)
        Z = w
        return np.column_stack([X, Y, Z])

    def section_points_sketch(self, i: int, n: int = N_SKETCH_PTS) -> np.ndarray:
        """
        Section i resampled UNIFORMLY IN ARC LENGTH to n points, closed exactly.
        Same 48-point rule as v02 (diag_point_threshold.json): guarantees no sub-tolerance
        segment, the documented cause of the original loft failures.
        Returns TRUE 3-D GLOBAL coordinates (N,3) for a 3-D sketch -- no local (a,b) mapping.
        """
        p3 = self.section_points(i)
        d = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(p3, axis=0), axis=1))]
        s = np.linspace(0.0, d[-1], n, endpoint=False)
        out = np.column_stack([np.interp(s, d, p3[:, k]) for k in range(3)])
        return np.vstack([out, out[0]])

    # -- realized-geometry diagnostics (used by gate G1') ----------------------------
    def stacking_line(self) -> np.ndarray:
        return np.column_stack([self.r * np.cos(self.theta),
                                self.r * np.sin(self.theta),
                                np.zeros_like(self.r)])

    def realized_sweep_deg(self) -> np.ndarray:
        """tan(Lam_realized) = R * dtheta/dr / (dR/dr); for v03 this must equal Lambda(r)."""
        P = self.stacking_line()
        R = np.hypot(P[:, 0], P[:, 1])
        th = np.unwrap(np.arctan2(P[:, 1], P[:, 0]))
        return np.degrees(np.arctan2(R * np.gradient(th, self.r), np.gradient(R, self.r)))

    def report(self) -> dict:
        P = self.stacking_line()
        return {
            "version": "v03",
            "sweep_model": "radius-preserving cylindrical: dtheta/dr = tan(Lambda)/r",
            "sweep_source": "ED-015 Lambda(r) = arccos(M_cap/M_hel), M_cap=0.78 -- REUSED UNCHANGED",
            "blade_count_B": int(self.B),
            "pitch_deg": 360.0 / int(self.B),
            "blade_count_provenance": "ED-014 independent project trade study -- NOT derived from "
                                       "any external concept. CFM RISE comparison is architectural/"
                                       "observational only and did not influence B.",
            "R_nominal_m": self.R,
            "cad_span_r_over_R": [R_START, R_END],
            "r_root_m": float(self.r[0]), "r_tip_m": float(self.r[-1]),
            "theta_tip_deg": float(np.degrees(self.theta[-1])),
            "true_radius_tip_m": float(np.hypot(P[-1, 0], P[-1, 1])),
            "analytical_volume_one_blade_m3": self.volume_one_blade,
            "v02_cartesian_y_sweep_tip_m_FOR_COMPARISON_ONLY": float(self.y_sweep_v02[-1]),
        }


def load():
    tbl = load_design_table(DESIGN / "results" / "design_table.csv")
    summ = json.load(open(DESIGN / "results" / "design_summary.json", encoding="utf-8"))
    return BladeGeometryV03(tbl, summ)


if __name__ == "__main__":
    bg = load()
    print(json.dumps(bg.report(), indent=2))
    A = np.vstack([bg.section_points(i) for i in range(N_CAD_SECTIONS)])
    Rt = np.hypot(A[:, 0], A[:, 1])
    print(f"\nsurface X {A[:,0].min():+.4f}..{A[:,0].max():+.4f}  "
          f"Y {A[:,1].min():+.4f}..{A[:,1].max():+.4f}  Z {A[:,2].min():+.4f}..{A[:,2].max():+.4f}")
    print(f"true radius {Rt.min():.4f}..{Rt.max():.4f} m (nominal R={bg.R})")
    print(f"realized sweep vs ED-015 max err = "
          f"{np.abs(bg.realized_sweep_deg() - np.degrees(bg.sweep)).max():.6f} deg")
