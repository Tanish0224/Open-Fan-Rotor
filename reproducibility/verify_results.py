"""Recompute every headline CFD number in this repository from the recorded result files.

Usage (from the repository root):
    python reproducibility/verify_results.py            # check only
    python reproducibility/verify_results.py --write    # also (re)write cfd_campaign/campaign_summary.json

What it checks, for every case folder in cfd_campaign/:
  1. shaft power  P   = Q * |omega|             against the stored P_shaft_W
  2. efficiency   eta = T * V0 / P              against the stored eta_p
  3. rolling convergence window   = peak-to-peak / |mean| of the last 5 checkpoints (T and Q)
  4. full-history convergence window = peak-to-peak / |mean| of checkpoints S2..S10 (T and Q)
     (S1 is the first-order start-up stage and is excluded from both windows)
  5. rotational speed recomputed from omega (rpm = |omega| * 60 / 2pi)

The recorded result files are NOT modified. Some of them carry a stored `rpm` field that
was not updated when omega changed (it reads the design value 1294.49 for every case,
including the 1000 rpm off-design case). This script reports the stored field and the
value implied by omega side by side; the operating point used everywhere in this
repository is the one implied by omega and the case definition.

Exit code 0 when every stored value reproduces; 1 otherwise.
"""
import glob
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPAIGN = os.path.join(ROOT, "cfd_campaign")
CRITERION = 0.01          # 1 % peak-to-peak bound used for both windows

CLASSIFICATION = {
    "v03_diagnostic_drag_state": "DIAGNOSTIC (drag state, design RPM)",
    "v04cf_camber_corrected": "DIAGNOSTIC (camber corrected; unsettled, diverged at iteration 246)",
    "v05n16_naca16_sections": "DESIGN-RPM CFD OBSERVATION",
    "v06e_cl_chord_schedule": "DESIGN-RPM CFD OBSERVATION",
    "v08_reference_case": "DESIGN-RPM CFD OBSERVATION (reference case)",
    "v10_uniform_depitch": "DESIGN-RPM CONTROLLED EXPERIMENT",
    "v11_1000rpm_offdesign": "OFF-DESIGN CFD OBSERVATION (1000 rpm)",
    "v12_sweep_plus6deg": "DESIGN-RPM CONTROLLED EXPERIMENT",
    "v14_hub_bc_diagnostic": "BOUNDARY-CONDITION DIAGNOSTIC (design RPM)",
    "v15_root_depitch": "DESIGN-RPM CONTROLLED EXPERIMENT",
}


def spread(values):
    mean = sum(values) / len(values)
    return (max(values) - min(values)) / abs(mean)


def main(write):
    ok = True
    summary = {}
    for folder in sorted(CLASSIFICATION):
        files = glob.glob(os.path.join(CAMPAIGN, folder, "performance_result_*.json"))
        if len(files) != 1:
            print("MISSING or ambiguous result file in", folder)
            ok = False
            continue
        d = json.load(open(files[0], encoding="utf-8"))
        op = d["operating_point"]
        V0, omega = op["V0"], op["omega"]
        T, Q, P = d["T_N"], d["Q_Nm"], d["P_shaft_W"]
        P_re = Q * abs(omega)
        eta_re = T * V0 / P_re if T > 0 and P_re > 0 else None
        eta = d.get("eta_p")
        p_ok = abs(P_re - P) <= 1e-6 * abs(P)
        e_ok = (eta is None and eta_re is None) or (eta is not None and eta_re is not None and abs(eta_re - eta) < 1e-9)
        cps = d.get("checkpoints") or []
        Ts = [abs(c["T_N"]) for c in cps]
        Qs = [abs(c["Q_Nm"]) for c in cps]
        rolling = full = None
        if len(cps) >= 10:
            rolling = (spread(Ts[-5:]), spread(Qs[-5:]))
            full = (spread(Ts[1:]), spread(Qs[1:]))
        rpm_omega = abs(omega) * 60 / (2 * math.pi)
        rec = {
            "classification": CLASSIFICATION[folder],
            "result_file": os.path.relpath(files[0], ROOT).replace(os.sep, "/"),
            "omega_rad_s": omega,
            "rpm_from_omega": round(rpm_omega, 2),
            "rpm_field_stored": op.get("rpm"),
            "rpm_field_consistent_with_omega": abs(op.get("rpm", rpm_omega) - rpm_omega) < 0.01,
            "thrust_N": T, "torque_Nm": Q, "shaft_power_W": P, "eta_p": eta,
            "P_recomputed_matches": p_ok, "eta_recomputed_matches": e_ok,
            "n_checkpoints": len(cps),
            "rolling_window_T_Q_pct": None if rolling is None else [round(100 * rolling[0], 6), round(100 * rolling[1], 6)],
            "rolling_window_pass": None if rolling is None else (rolling[0] < CRITERION and rolling[1] < CRITERION),
            "full_history_T_Q_pct": None if full is None else [round(100 * full[0], 6), round(100 * full[1], 6)],
            "full_history_pass": None if full is None else (full[0] < CRITERION and full[1] < CRITERION),
        }
        summary[folder] = rec
        ok &= p_ok and e_ok
        print("%-28s P %s  eta %s  rpm(omega) %7.2f  stored rpm %7.2f  rolling %s  full %s" % (
            folder, "OK " if p_ok else "BAD", "OK " if e_ok else "BAD", rpm_omega, op.get("rpm", float("nan")),
            rec["rolling_window_T_Q_pct"], rec["full_history_T_Q_pct"]))
    if write:
        out = {
            "_note": ("Derived file written by reproducibility/verify_results.py from the recorded result files. "
                      "The stored rpm field in some recorded files is stale; operating conditions are taken "
                      "from omega and the case definition. Windows use a 1 % peak-to-peak bound. "
                      "These are recorded CFD observations, not validated performance."),
            "cases": summary,
        }
        json.dump(out, open(os.path.join(CAMPAIGN, "campaign_summary.json"), "w", encoding="utf-8"), indent=1)
        print("wrote cfd_campaign/campaign_summary.json")
    print("ALL STORED VALUES REPRODUCE" if ok else "MISMATCH FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
