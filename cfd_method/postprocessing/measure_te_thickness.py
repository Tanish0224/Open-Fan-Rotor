"""
measure_te_thickness.py -- measure the ACTUAL trailing-edge thickness that Fluent
meshed, from the exported blade-surface node cloud.

WHY THIS EXISTS
---------------
The mesh size floor is 7.24 m/1000. At 0.75R the v06 chord is 0.3865 m, so a 0.020 c
trailing edge is 7.73 mm -- 1.07 cells across, right AT the floor. A 0.012 c trailing
edge is 4.64 mm, only 0.64 cells across. The mesher may therefore COLLAPSE the
trailing edge rather than resolve it, in which case the geometry actually solved is not
the geometry that was designed, and any drag reduction would be a meshing artefact
rather than a measured base-drag effect.

So the TE thickness is MEASURED here, not assumed from the CAD.

METHOD
------
At each radial station, take the nodes in a thin annular band, rotate them into the
section frame using the design twist beta(r), and find the chordwise extremes. The
trailing edge is the high-x end. Its thickness is the spread of the section-normal
coordinate among nodes within the last 2% of chord.

This measures the MESHED surface, which is what the solver saw.

BAND WIDTH IS CRITICAL -- CALIBRATED, NOT GUESSED
-------------------------------------------------
The blade is swept (Lambda reaches 43 deg) and twisted, so a radial sampling band
smears the section along the chord and INFLATES the apparent trailing-edge thickness.
Measured on v06e, whose intended TE is known to be 0.020 c:

    band +/-  4 mm  ->  outboard mean TE/c = 0.0200   <-- matches design exactly
    band +/- 10 mm  ->  0.0374  (+87 %)
    band +/- 20 mm  ->  0.0507  (+154 %)

BAND is therefore fixed at 4 mm. The v06e agreement at that setting is what validates
the method; the same setting must be used for every version so the comparison is fair.

USAGE
    python measure_te_thickness.py <blade_surface_TAG.csv> <design_table.csv> [te_frac]
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
STATIONS = [0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
R = 1.75
NB = 16               # blade count -- the annular band cuts all of them
BAND = 0.004          # m, half-width of the annular sampling band
TE_WINDOW = 0.02      # last 2% of chord counts as "the trailing edge"


def load_nodes(path):
    xyz = []
    with open(path) as f:
        rd = csv.reader(f)
        next(rd)
        for row in rd:
            if len(row) < 4:
                continue
            try:
                xyz.append((float(row[1]), float(row[2]), float(row[3])))
            except ValueError:
                continue
    return np.array(xyz)


def design_cols(path):
    rows = list(csv.DictReader(open(path)))
    x = np.array([float(r["r_over_R"]) for r in rows])
    return (x,
            np.array([float(r["chord_m"]) for r in rows]),
            np.array([float(r["beta_deg"]) for r in rows]))


def main(surf, table, te_frac=None):
    P = load_nodes(surf)
    xd, cd, bd = design_cols(table)
    r = np.hypot(P[:, 0], P[:, 1])
    th = np.arctan2(P[:, 1], P[:, 0])
    print("nodes: %d   radial extent %.4f .. %.4f m" % (len(P), r.min(), r.max()))
    print("\n r/R   chord[m]  intended TE      MEASURED TE     cells   ratio")
    print("       %s" % ("-" * 58))
    out = []
    for xr in STATIONS:
        rr = xr * R
        m = np.abs(r - rr) < BAND
        if m.sum() < 50:
            print("%5.2f   -- only %d nodes in band, skipped" % (xr, m.sum()))
            continue
        c = float(np.interp(xr, xd, cd))
        beta = math.radians(float(np.interp(xr, xd, bd)))
        # ---- isolate ONE blade -------------------------------------------------
        # The annular band cuts all 16 blades. Fold theta modulo the blade pitch so
        # the 16 identical sections superimpose, then centre on the resulting cluster.
        # Without this the "section" is a smear across the whole disc and the measured
        # thickness is meaningless (it came out as 444 mm on a 386 mm chord).
        pitch = 2.0 * math.pi / NB
        tf = np.mod(th[m], pitch)
        # centre via the circular mean on the folded angle
        ang = tf * (2 * math.pi / pitch)
        cen = math.atan2(np.sin(ang).mean(), np.cos(ang).mean()) * pitch / (2 * math.pi)
        tf = np.mod(tf - cen + pitch / 2.0, pitch) - pitch / 2.0
        u = rr * tf                                   # arc length about the blade
        w = P[m, 2]
        # chordwise axis is rotated by beta from the rotation plane
        xc = u * math.cos(beta) + w * math.sin(beta)
        yc = -u * math.sin(beta) + w * math.cos(beta)
        span = xc.max() - xc.min()
        # trailing edge = the end with the LARGER local thickness
        lo = yc[xc < xc.min() + TE_WINDOW * span]
        hi = yc[xc > xc.max() - TE_WINDOW * span]
        t_lo = float(lo.max() - lo.min()) if len(lo) > 2 else 0.0
        t_hi = float(hi.max() - hi.min()) if len(hi) > 2 else 0.0
        t = max(t_lo, t_hi)
        intended = (te_frac * c) if te_frac else float("nan")
        print("%5.2f   %6.4f   %7.2f mm      %7.2f mm     %5.2f   %s"
              % (xr, c, intended * 1e3, t * 1e3, t / 0.00724,
                 ("%.2f" % (t / intended)) if te_frac else "n/a"))
        out.append({"r_over_R": xr, "chord_m": c, "measured_te_m": t,
                    "measured_te_over_c": t / c,
                    "intended_te_m": intended if te_frac else None,
                    "cells_across": t / 0.00724})
    if out:
        outboard = [o for o in out if o["r_over_R"] >= 0.70]
        mean_toc = sum(o["measured_te_over_c"] for o in outboard) / len(outboard)
        print("\n  outboard (r/R >= 0.70) mean measured TE/c = %.4f" % mean_toc)
        if te_frac:
            err = abs(mean_toc - te_frac) / te_frac
            print("  intended %.4f  ->  %s (gate: within 25%%)"
                  % (te_frac, "PASS" if err <= 0.25 else "FAIL, error %.0f%%" % (100*err)))
        j = pathlib.Path(surf).with_suffix("").name.replace("blade_surface_", "")
        p = HERE / ("te_thickness_%s.json" % j)
        json.dump({"source": str(surf), "intended_te_frac": te_frac,
                   "outboard_mean_te_over_c": mean_toc, "stations": out,
                   "mesh_size_floor_m": 0.00724}, open(p, "w"), indent=1)
        print("  wrote %s" % p.name)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    tf = float(sys.argv[3]) if len(sys.argv) > 3 else None
    sys.exit(main(sys.argv[1], sys.argv[2], tf))
