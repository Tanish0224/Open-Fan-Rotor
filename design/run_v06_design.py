"""
run_v06_design.py -- generate the v06 BEM design: the two remaining POSITIVE levers.

WHY (Stage 36, after the v05 result)
------------------------------------
v05 re-sectioned the blade and measured eta_p = 0.5006 in Fluent, up 38.9 % on v04.
Every remaining design lever was then tested (stage document section 4e):

    more sweep, corrected law   GEOMETRICALLY IMPOSSIBLE -- 318 % of a blade pitch
    lower rotational tip Mach   WORSE
    higher hub-tip ratio        WORSE -- concentrates loading, raises the Mach excess
    more blades                 flat
    LOWER DESIGN Cl (chord up)  +0.01..+0.03, the mechanism real          <- POSITIVE
    THINNER ROOT                +0.03                                     <- POSITIVE

Only two levers point the right way, and BOTH act on the SAME mechanism: peak suction
scales with Cl and with t/c, so reducing either raises the section's critical Mach. They
are applied together here because their attribution has already been separated by the
model (Cl alone +0.025/+0.030, t/c alone +0.019/+0.021, together +0.037/+0.039 --
sub-additive, as coupled levers on one mechanism should be), and because running them as
two more six-hour CFD pipelines would buy an attribution the model has already supplied.

WHAT CHANGES, AND THE JUSTIFICATION FOR EACH
--------------------------------------------
  cl_root  0.70 -> 0.45     Lower design lift, with the BEM raising CHORD to hold the
  cl_tip   0.40 -> 0.26     same thrust. This is what high-solidity transonic propfans
                            do, and for exactly this reason. Solidity at 0.75R goes
                            0.478 -> 0.749, kept BELOW the ~0.80 point where the blades
                            begin to crowd; chord/R 0.140 -> 0.220.

  toc_root 0.20 -> 0.12     The original was "[DESIGN DECISION] thick root for
                            structure, LOW LOCAL MACH". Stage 36 measured the second
                            half of that justification to be FALSE: the root runs at
                            M_rel 0.78-0.89. 0.12 is chosen rather than the model's
                            slightly better 0.10 because the structural case has NOT
                            been re-run and a thick root still carries the centrifugal
                            and bending load -- this is the aerodynamically-motivated
                            part of the change only, and it is deliberately conservative.

NOT CHANGED: diameter, flight Mach, altitude, rotational tip Mach, tau, blade count,
hub-tip ratio, camber position, tip thickness, the sweep law, and the v05 section family.

PRE-REGISTERED PREDICTION (results/v06_candidates.json, written before the geometry)
-----------------------------------------------------------------------------------
Thrust-weighted Mach excess +0.163 -> +0.112, a 31 % reduction. Model eta bracket
0.422-0.517 -> 0.459-0.556, i.e. a gain of +0.037..+0.039 applied to the MEASURED v05
value of 0.5006:

    eta_p(v06) predicted ~ 0.53-0.55
    FALSIFIED IF the Fluent run returns eta_p <= 0.50 (no improvement on v05)

This run also TESTS the stage's own ceiling claim. The "~0.55 ceiling within this
configuration" is currently a model assertion anchored to one measured point. If v06
lands near 0.54 the ceiling is confirmed with Fluent data; if it exceeds it, the model
was wrong and the ceiling moves.

OUTPUTS  results/design_table_v06.csv, results/design_summary_v06.json
         (the v03-v05 design table is NOT touched)
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys
from dataclasses import asdict

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from openfan_design import DesignSpec, OpenFanRotorDesign          # noqa: E402

OUT_TBL = HERE / "results" / "design_table_v06.csv"
OUT_SUM = HERE / "results" / "design_summary_v06.json"

CHANGES = dict(cl_root=0.45, cl_tip=0.26, toc_root=0.12)


def jsonable(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, dict):
        return {k: jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return o


def main():
    base = DesignSpec(n_blades=16)
    spec = DesignSpec(**{**asdict(base), **CHANGES})
    print("  CHANGES vs the v03-v05 design:")
    for k, v in CHANGES.items():
        print("     %-10s %s -> %s" % (k, getattr(base, k), v))
    print("  held fixed: diameter, mach_flight, altitude, mach_tip_rot, tau, n_blades,")
    print("              hub_tip_ratio, camber_pos, toc_tip, toc_decay, mn_limit")

    d = OpenFanRotorDesign(spec)
    d.solve()
    if not d.converged:
        raise SystemExit("BEM did not converge -- refusing to write a design table")
    t = d.radial_table()
    s = d.summary()

    ch = d.closure_checks() if hasattr(d, "closure_checks") else {}
    if ch:
        allp = ch.get("ALL_PASS")
        print("  BEM closure checks: %s" % ("ALL PASS" if allp else "FAILURES PRESENT"))
        if not allp:
            for k, v in ch.items():
                if isinstance(v, dict) and not v.get("pass", True):
                    print("     FAIL %s: %s" % (k, v))
            raise SystemExit("closure checks failed -- refusing to write a design table")

    keys = list(t.keys())
    with open(OUT_TBL, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(keys)
        for i in range(len(t["r_over_R"])):
            w.writerow(["%.10g" % float(t[k][i]) for k in keys])
    # `OpenFanRotorDesign.summary()` does not carry the keys that
    # run_phase1_design.py adds afterwards, and blade_geometry_v03 needs
    # `blade_count_selected`. They are supplied here from the spec itself and from
    # this design's own radial table -- not copied from the v03-v05 summary, which
    # describes a DIFFERENT design.
    s["blade_count_selected"] = int(spec.n_blades)
    s["radial_table"] = jsonable(t)
    s["gate_G0"] = jsonable(ch) if ch else {"NOTE": "closure checks not exposed"}
    s["_provenance"] = ("v06 design: cl_root 0.45, cl_tip 0.26, toc_root 0.12 against "
                        "the v03-v05 0.70 / 0.40 / 0.20. Everything else identical. "
                        "Generated by run_v06_design.py; results/design_table.csv and "
                        "results/design_summary.json are NOT touched.")
    json.dump(jsonable(s), open(OUT_SUM, "w"), indent=1)

    i = int(np.argmin(abs(t["r_over_R"] - 0.75)))
    print()
    print("  v06 DESIGN")
    print("     thrust      %10.1f N     (v03-v05 design: 14451.5 N)" % d.thrust_N)
    print("     torque      %10.1f N.m   (v03-v05 design: 29372.3 N.m)" % d.torque_Nm)
    print("     eta_bem     %10.4f       (v03-v05 design: 0.8072) -- NO wave drag, an ESTIMATE"
          % d.eta_bem)
    print("     solidity@0.75R %7.3f       (v03-v05: 0.478)   chord/R %.3f (was 0.140)"
          % (t["solidity"][i], t["chord_over_R"][i]))
    print("     Cl@0.75R    %10.3f       (was 0.526)" % t["Cl_design"][i])
    print("     t/c root    %10.3f       (was 0.200)" % t["toc"][0])
    print()
    print("  wrote %s" % OUT_TBL.name)
    print("  wrote %s" % OUT_SUM.name)
    print("  (results/design_table.csv -- the v03-v05 design -- is UNTOUCHED)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
