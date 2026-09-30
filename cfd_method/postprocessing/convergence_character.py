"""
convergence_character.py -- WHAT KIND of non-convergence is it?

THIS DOES NOT REPLACE THE PROJECT'S CONVERGENCE GATE.
------------------------------------------------------
The gate is, and remains: **peak-to-peak variation of T and Q over the second-order
window must be below 1 %**. `compute_performance.py` applies it and its verdict is the
one that counts. Nothing here relaxes, reinterprets or substitutes for that, because
replacing a failed criterion with one that passes is exactly the failure mode
this analysis must avoid.

What this adds is a distinction the peak-to-peak number cannot make on its own:

    DRIFTING   the solution is still moving toward something. The last value is not
               the answer, the window mean is not the answer, and running longer would
               change both. v04's second-order window did this -- 4153 -> 4178 -> 4210,
               monotone increasing, every step the same sign.

    STATIONARY the solution is oscillating about a fixed mean with no trend. The mean
               is meaningful and running longer narrows its standard error but does not
               move it. The peak-to-peak can still exceed 1 % while this is true.

Both FAIL the gate. They do not mean the same thing, and an honest report should say
which one it is rather than leaving the reader to assume the worse or the better.

THE TEST
--------
Ordinary least squares of the quantity against checkpoint index, over the second-order
window only. Reported: slope per checkpoint, its standard error, the t statistic, and
the fraction of the mean the slope represents over the whole window. A |t| below about
2 with a small total excursion is consistent with stationarity; it does not prove it,
and with 5-9 points the power is low. That limitation is printed with the result.

USAGE   python convergence_character.py <transcript.trn> [label]
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys

import numpy as np

V0 = 222.40155844424964
import case_omega
# OMEGA used to be the hard-coded design value and it enters eta directly
# (eta = soT*V0/(soQ*OMEGA)), which this report PRINTS. For v11 at 1000 rpm a
# design-speed OMEGA would have printed an eta ~29 % too low, inside a document
# whose whole purpose is to judge whether the run settled. Resolved per tag in
# main() from the label argument instead.
TRIPLE = r"\(\s*([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)"


def series(path):
    txt = pathlib.Path(path).read_text(errors="ignore")
    rows = re.findall(r"^blade\s+" + TRIPLE + r"\s+" + TRIPLE + r"\s+" + TRIPLE,
                      txt, re.M)
    v = [(float(r[6]), float(r[7]), float(r[8])) for r in rows]
    F = [v[i] for i in range(0, len(v) - 1, 2)]
    M = [v[i + 1] for i in range(0, len(v) - 1, 2)]
    T = np.array([-f[2] for f in F])
    Q = np.array([m[2] for m in M])
    sym = np.array([100 * math.hypot(f[0], f[1]) / abs(f[2]) for f in F])
    return T, Q, sym


def ols(y):
    x = np.arange(len(y), dtype=float)
    n = len(y)
    if n < 3:
        return dict(slope=float("nan"), se=float("nan"), t=float("nan"))
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    s2 = float(resid @ resid) / (n - 2)
    sxx = float(((x - x.mean()) ** 2).sum())
    se = math.sqrt(s2 / sxx) if sxx > 0 else float("nan")
    return dict(slope=float(b), se=float(se),
                t=float(b / se) if se and se == se and se > 0 else float("nan"))


def report(name, y, label):
    pp = 100.0 * (y.max() - y.min()) / y.mean()
    r = ols(y)
    total = r["slope"] * (len(y) - 1)
    sem = float(y.std(ddof=1) / math.sqrt(len(y)))
    print("  %-8s mean %12.4f   peak-to-peak %5.2f %%   s.e.m. %8.4f (%.2f %%)"
          % (name, y.mean(), pp, sem, 100 * sem / abs(y.mean())))
    print("           trend %+10.4f per checkpoint  (t = %+5.2f)   "
          "total excursion %+.2f %% of the mean"
          % (r["slope"], r["t"], 100 * total / y.mean()))
    return dict(mean=float(y.mean()), peak_to_peak_pct=float(pp), sem=sem,
                slope_per_checkpoint=r["slope"], t_stat=r["t"],
                total_trend_pct=float(100 * total / y.mean()))


def main(path, label="run"):
    OMEGA = case_omega.resolve(label)
    print("  omega: %.9f rad/s  (%s)" % (OMEGA, case_omega.note(label)))
    T, Q, sym = series(path)
    if len(T) < 2:
        raise SystemExit("not enough checkpoints yet")
    soT, soQ, soS = T[1:], Q[1:], sym[1:]      # drop the first-order checkpoint
    eta = soT * V0 / (soQ * OMEGA)
    print("=" * 84)
    print("  CONVERGENCE CHARACTER -- %s" % label)
    print("  second-order window: %d checkpoints, %d iterations"
          % (len(soT), 60 * len(soT)))
    print("=" * 84)
    out = {}
    for nm, y in (("T [N]", soT), ("Q [N.m]", soQ), ("eta_p", eta),
                  ("sym [%]", soS)):
        out[nm] = report(nm, np.asarray(y, float), label)
        print()
    gate = out["T [N]"]["peak_to_peak_pct"] < 1.0 and out["Q [N.m]"]["peak_to_peak_pct"] < 1.0
    print("  PROJECT GATE (peak-to-peak of T and Q both < 1 %%): %s"
          % ("PASS" if gate else "FAIL"))
    tT = out["T [N]"]["t_stat"]
    stationary = abs(tT) < 2.0
    print("  CHARACTER: %s"
          % ("no significant trend in T (|t| = %.2f < 2) -- consistent with a "
             "STATIONARY oscillation about a fixed mean" % abs(tT) if stationary else
             "significant trend in T (|t| = %.2f) -- the solution is still DRIFTING"
             % abs(tT)))
    print()
    print("  LIMITATION: with %d points this test has low power. It can fail to detect"
          % len(soT))
    print("  a real trend. It does NOT convert a failed gate into a passed one, and the")
    print("  gate above is the verdict that counts.")
    json.dump(dict(label=label, source=str(path), n_second_order=len(soT),
                   iterations=60 * len(soT), quantities=out,
                   project_gate_pass=bool(gate),
                   trend_test="OLS against checkpoint index, second-order window only",
                   caveat=("this characterises the KIND of non-convergence; it does not "
                           "replace the peak-to-peak gate and cannot make a failed gate "
                           "pass")),
              open(pathlib.Path(__file__).with_name(
                  "convergence_character_%s.json" % label), "w"), indent=2)
    print("  wrote convergence_character_%s.json" % label)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: convergence_character.py <transcript.trn> [label]")
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "run"))
