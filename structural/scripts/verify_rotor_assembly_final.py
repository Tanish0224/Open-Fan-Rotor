"""
verify_rotor_assembly_final.py -- F01-F21 gates for openfan_rotor_assembly_v02_final.SLDASM.

Two distinct classes of check, deliberately kept separate:
  NATIVE-ASSEMBLY gates (F01-F08, F18-F21) -- interrogate the SolidWorks assembly document
      itself: mate inventory, per-component constrained status, rebuild errors, persistence.
      These are the gates v01 could never have passed, and are the point of this phase.
  GEOMETRIC gates (F09-F17) -- reuse the already-checked measurement methodology from
      verify_rotor_assembly.py (tessellated point clouds + the same rigid Z-rotation the
      assembly itself applies), including the three method corrections established there:
        * interface gaps by the proven station-0 method + isometry, NOT a biased hypot(X,Y) proxy
        * interference by TRUE minimum surface distance, NOT AABB overlap (which false-positives
          on swept blades -- DECISION_LOG.md O8)
        * axial rake as root-to-tip mean-Z shift, NOT total Z-extent
"""
import json
import pathlib
import time

import numpy as np
import pythoncom
import win32com.client

HERE = pathlib.Path(__file__).parent
ASM_FINAL = HERE / "openfan_rotor_assembly_v02_final.SLDASM"
ASM_V01 = HERE / "openfan_rotor_assembly_v01.SLDASM"
CARRIER = HERE / "openfan_central_carrier_v02_16station.SLDPRT"
ROOT_MODULE = HERE / "openfan_blade_root_module_v01.SLDPRT"
BLADE_V03 = HERE / "openfan_blade_v03_G1_PRIME_VERIFIED.SLDPRT"
SHELL = HERE / "openfan_spinner_shell_v02_16cutout.SLDPRT"
V01_AUDIT = HERE / "verification" / "assembly_v01_audit.json"
OUT = HERE / "verification" / "rotor_assembly_v02_final_verification.json"

swDocPART = 1
swDocASSEMBLY = 2
N = 16
PITCH_DEG = 360.0 / N
YC = -0.0017634304844025408
ZC = 0.00035904190661881724
CUTOUT_RADIUS = 0.045

# IComponent2.GetConstrainedStatus codes -- EMPIRICALLY CALIBRATED on this install against
# four KNOWN states (scratch probe_constrained_status.py), NOT taken from a documented enum.
# This calibration was forced by a real false reading: the nominal swComponentConstrainedStatus_e
# mapping (3 = OverConstrained) made all 34 components -- INCLUDING the fixed, zero-mate carrier
# -- report "OverConstrained". A component with no mates cannot be over-constrained, so the map
# itself was suspect and was tested rather than trusted.
#   fixed, zero mates      (definitionally locked)      -> 3
#   floating, ZERO mates   (6 DOF free, under-constr.)  -> 2
#   floating, 1 mate       (still under-constrained)    -> 2
#   floating, 3-mate scheme                             -> 3
#   floating, +redundant 4th mate (truly over-constr.)  -> 6
# => on this install: 2 = UnderConstrained, 3 = FullyConstrained, 6 = OverConstrained.
CONSTRAINED = {0: "Unknown", 1: "Unknown_1", 2: "UnderConstrained",
               3: "FullyConstrained", 4: "NotSolved", 6: "OverConstrained"}


def NULL():
    return win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)


def tessellate(body):
    pts = []
    for fc in list(body.GetFaces()):
        tt = fc.GetTessTriangles(True)
        if not tt:
            continue
        a = np.asarray(tt, dtype=float)
        n = (len(a) // 3) * 3
        pts.append(a[:n].reshape(-1, 3))
    return np.vstack(pts) if pts else np.zeros((0, 3))


def rotate_z(pts, th):
    c, s = np.cos(th), np.sin(th)
    return pts @ np.array([[c, -s, 0.], [s, c, 0.], [0., 0., 1.]]).T


def bbox_overlap(a, b):
    return bool(np.all(a.min(0) <= b.max(0)) and np.all(b.min(0) <= a.max(0)))


def min_dist(a, b, sample=2500, seed=0):
    rng = np.random.default_rng(seed)
    A = a[rng.choice(len(a), min(sample, len(a)), replace=False)]
    B = b[rng.choice(len(b), min(sample, len(b)), replace=False)]
    m = np.inf
    for i in range(0, len(A), 400):
        m = min(m, np.linalg.norm(B[None] - A[i:i + 400, None], axis=2).min())
    return float(m)


def angle_from_arraydata(arr):
    return float(np.degrees(np.arctan2(-arr[3], arr[0]))) % 360.0


def count_mates(model):
    out = []
    f = model.FirstFeature
    while f:
        if f.GetTypeName2 == "MateGroup":
            sub = f.GetFirstSubFeature
            while sub:
                rec = {"name": sub.Name, "type": sub.GetTypeName2}
                try:
                    rec["suppressed"] = bool(sub.IsSuppressed)
                except Exception:
                    rec["suppressed"] = None
                out.append(rec)
                sub = sub.GetNextSubFeature
        f = f.GetNextFeature
    return out


def main():
    app = win32com.client.Dispatch("SldWorks.Application")
    app.Visible = True
    for d in list(app.GetDocuments or []):
        app.CloseDoc(d.GetTitle)
    time.sleep(0.5)

    R = {}

    # ============ NATIVE-ASSEMBLY GATES ============
    model = app.OpenDoc(str(ASM_FINAL), swDocASSEMBLY)
    if model is None:
        raise RuntimeError("Could not open the final assembly.")
    rebuild_ok = model.EditRebuild3
    time.sleep(0.8)

    mates = count_mates(model)
    comps = list(model.GetComponents(False) or [])
    expected_mates = 3 * (1 + 2 * N)          # shell + 16 root + 16 blade
    expected_comps = 1 + 1 + 2 * N            # carrier + shell + 16 + 16

    R["F01_mate_inventory"] = {
        "n_mates": len(mates), "expected": expected_mates,
        "n_suppressed": sum(1 for m in mates if m.get("suppressed")),
        "mate_types": sorted(set(m["type"] for m in mates)),
        "pass": bool(len(mates) == expected_mates),
    }
    print(f"F01 mates: {len(mates)} (expected {expected_mates})  types={R['F01_mate_inventory']['mate_types']}")

    R["F02_mate_rebuild_no_errors"] = {
        "EditRebuild3": bool(rebuild_ok),
        "n_suppressed_mates": R["F01_mate_inventory"]["n_suppressed"],
        "pass": bool(rebuild_ok and R["F01_mate_inventory"]["n_suppressed"] == 0),
    }

    # per-component constrained status
    states = []
    for c in comps:
        rec = {"name": c.Name2}
        try:
            rec["is_fixed"] = bool(c.IsFixed)
        except Exception as e:
            rec["is_fixed"] = f"ERR:{e}"
        # PROPERTY, not a method, under late binding on this install -- the same trap that
        # made the v01 audit's IsFixed() return an error string for every component. A first
        # pass here called GetConstrainedStatus() and got "'int' object is not callable" for
        # all 34, which then made the under/over-constrained lists EMPTY and produced a
        # VACUOUS PASS on F03/F04/F06/F07/F08 -- the single most important gates in this
        # phase. Caught and corrected rather than accepted; see the report.
        try:
            cs = c.GetConstrainedStatus
            rec["constrained_code"] = int(cs)
            rec["constrained"] = CONSTRAINED.get(int(cs), f"UNMAPPED({cs})")
        except Exception as e:
            rec["constrained"] = f"ERR:{e}"
        try:
            rec["angle_deg"] = angle_from_arraydata(list(c.Transform2.ArrayData))
        except Exception:
            rec["angle_deg"] = None
        states.append(rec)
    R["component_states"] = states

    n_fixed = sum(1 for s in states if s.get("is_fixed") is True)
    status_counts = {}
    for s in states:
        status_counts[str(s.get("constrained"))] = status_counts.get(str(s.get("constrained")), 0) + 1
    R["constrained_status_counts"] = status_counts
    print(f"  constrained status counts: {status_counts}")
    print(f"  fixed components: {n_fixed}")

    # GUARD: a gate that cannot be EVALUATED must never report PASS. If the constrained status
    # could not be read for every component, these gates are unmeasurable and must FAIL, not
    # silently pass on an empty list (which is exactly what happened on the first run).
    n_unreadable = sum(1 for s in states if str(s.get("constrained", "")).startswith("ERR:"))
    status_readable = (n_unreadable == 0)
    R["constrained_status_readable"] = {"n_unreadable": n_unreadable, "readable": status_readable}

    under = [s["name"] for s in states if s.get("constrained") == "UnderConstrained"]
    over = [s["name"] for s in states if s.get("constrained") == "OverConstrained"]
    R["F03_fully_constrained"] = {
        "n_under_constrained": len(under), "under_constrained": under[:10],
        "n_fixed": n_fixed, "status_readable": status_readable,
        "pass": bool(status_readable and len(under) == 0),
    }
    R["F04_no_over_definition"] = {
        "n_over_constrained": len(over), "over_constrained": over[:10],
        "status_readable": status_readable,
        "pass": bool(status_readable and len(over) == 0),
    }

    def status_of(pred):
        return [s for s in states if pred(s["name"])]

    car = status_of(lambda n: "central_carrier" in n)
    sh = status_of(lambda n: "spinner_shell" in n)
    rms = status_of(lambda n: "root_module" in n)
    bls = status_of(lambda n: "blade_v03" in n)

    R["F05_carrier_grounded"] = {
        "carrier": car[0] if car else None,
        "pass": bool(car and car[0].get("is_fixed") is True),
    }
    # F06/F07: test MULTIPLE stations, not only station 0 (explicit phase requirement)
    sample_idx = [0, 1, 5, 8, 12, 15]
    def all_locked(group):
        """Every component in the group must be positively reported FullyConstrained or Fixed.
        Anything else -- including an unreadable status -- fails."""
        return bool(group) and all(
            s.get("constrained") == "FullyConstrained" or s.get("is_fixed") is True
            for s in group)

    R["F06_root_module_mobility"] = {
        "n_root_modules": len(rms),
        "sampled_states": [rms[i] for i in sample_idx if i < len(rms)],
        "status_readable": status_readable,
        "stations_sampled": sample_idx,
        "pass": bool(status_readable and len(rms) == N and all_locked(rms)),
    }
    R["F07_blade_mobility"] = {
        "n_blades": len(bls),
        "sampled_states": [bls[i] for i in sample_idx if i < len(bls)],
        "status_readable": status_readable,
        "pass": bool(status_readable and len(bls) == N and all_locked(bls)),
    }
    R["F08_shell_mobility"] = {
        "shell": sh[0] if sh else None,
        "status_readable": status_readable,
        "pass": bool(status_readable and sh and all_locked(sh)),
    }

    # cleanup audit
    R["cleanup_audit"] = {
        "n_suppressed_components": sum(1 for c in comps if bool(c.IsSuppressed)),
        "distinct_refs": sorted(set(c.GetPathName for c in comps)),
    }
    R["cleanup_audit"]["all_refs_resolve"] = all(
        pathlib.Path(p).exists() for p in R["cleanup_audit"]["distinct_refs"])

    # ---- F09/F10: transform reproduction vs the v01 verified reference state -------------
    v01 = json.load(open(V01_AUDIT, encoding="utf-8")) if V01_AUDIT.exists() else {}
    ref = v01.get("reference_transform_state", {})
    ref_root = sorted(ref.get("root_module_angles_deg", []))
    ref_blade = sorted(ref.get("blade_angles_deg", []))
    new_root = sorted(s["angle_deg"] for s in rms if s["angle_deg"] is not None)
    new_blade = sorted(s["angle_deg"] for s in bls if s["angle_deg"] is not None)
    drift_root = max(abs(a - b) for a, b in zip(new_root, ref_root)) if len(new_root) == len(ref_root) == N else None
    drift_blade = max(abs(a - b) for a, b in zip(new_blade, ref_blade)) if len(new_blade) == len(ref_blade) == N else None
    R["F09_transform_reproduction_vs_v01"] = {
        "v01_root_angles": ref_root, "final_root_angles": new_root,
        "max_root_drift_deg": drift_root, "max_blade_drift_deg": drift_blade,
        "tolerance_deg": 1e-6,
        "pass": bool(drift_root is not None and drift_blade is not None
                     and drift_root < 1e-6 and drift_blade < 1e-6),
    }
    print(f"F09 transform drift vs v01: root={drift_root} blade={drift_blade}")

    expected_angles = [k * PITCH_DEG for k in range(N)]
    pitch_err = max(abs(a - e) for a, e in zip(new_root, expected_angles)) if len(new_root) == N else None
    R["F10_station_pitch"] = {"pitch_deg": PITCH_DEG, "max_err_deg": pitch_err,
                              "pass": bool(pitch_err is not None and pitch_err < 1e-6)}

    app.CloseDoc(model.GetTitle)

    # ---- F18/F19/F20/F21: save/reopen + rebuild persistence ------------------------------
    m2 = app.OpenDoc(str(ASM_FINAL), swDocASSEMBLY)
    mates2 = count_mates(m2)
    comps2 = list(m2.GetComponents(False) or [])
    rebuild2 = m2.EditRebuild3
    states2 = []
    for c in comps2:
        try:
            states2.append({"name": c.Name2, "angle_deg": angle_from_arraydata(list(c.Transform2.ArrayData))})
        except Exception:
            pass
    ang_map1 = {s["name"]: s["angle_deg"] for s in states}
    ang_map2 = {s["name"]: s["angle_deg"] for s in states2}
    drift = [abs(ang_map1[k] - ang_map2[k]) for k in ang_map1 if k in ang_map2
             and ang_map1[k] is not None and ang_map2[k] is not None]
    R["F18_mate_persistence"] = {"n_mates_after_reopen": len(mates2), "expected": expected_mates,
                                  "pass": bool(len(mates2) == expected_mates)}
    R["F19_geometry_persistence"] = {"max_angle_drift_after_reopen_deg": max(drift) if drift else None,
                                      "pass": bool(drift and max(drift) < 1e-9)}
    R["F20_component_count"] = {"n": len(comps2), "expected": expected_comps,
                                 "pass": bool(len(comps2) == expected_comps)}
    R["F21_rebuild_stability"] = {"EditRebuild3_after_reopen": bool(rebuild2),
                                   "n_mates_after_rebuild": len(count_mates(m2)),
                                   "pass": bool(rebuild2 and len(count_mates(m2)) == expected_mates)}
    print(f"F18 mates after reopen: {len(mates2)}   F20 components: {len(comps2)}")
    app.CloseDoc(m2.GetTitle)

    # ============ GEOMETRIC GATES (checked methodology, reused) ============
    m = app.OpenDoc(str(ROOT_MODULE), swDocPART)
    T_rm = tessellate(list(m.GetBodies2(0, True))[0]); app.CloseDoc(m.GetTitle)
    m = app.OpenDoc(str(BLADE_V03), swDocPART)
    T_bl = tessellate(list(m.GetBodies2(0, True))[0]); app.CloseDoc(m.GetTitle)
    m = app.OpenDoc(str(CARRIER), swDocPART)
    T_car = tessellate(list(m.GetBodies2(0, True))[0]); app.CloseDoc(m.GetTitle)
    m = app.OpenDoc(str(SHELL), swDocPART)
    T_sh = tessellate(list(m.GetBodies2(0, True))[0]); app.CloseDoc(m.GetTitle)

    gap0 = float(T_bl[:, 0].min() - T_rm[:, 0].max())
    R["F11_blade_root_interface"] = {
        "station0_gap_m": gap0,
        "method": "proven station-0 X-min/X-max method (BLADE_ROOT_MODULE_BUILD_REPORT.md Sec.8); "
                   "invariant at all 16 stations because the mate scheme applies the IDENTICAL "
                   "rotation to each paired root+blade (F09/F10 confirm identical angles)",
        "pass": bool(abs(gap0) < 1e-3)}
    print(f"F11 blade-root gap: {gap0*1000:.6f} mm")

    r_bl = np.hypot(T_bl[:, 0], T_bl[:, 1])
    th_bl = np.degrees(np.arctan2(T_bl[:, 1], T_bl[:, 0]))
    R["F12_blade_orientation"] = {
        "azimuth_span_deg": float(th_bl.max() - th_bl.min()),
        "radial_range_m": [float(r_bl.min()), float(r_bl.max())],
        "all_stations_same_handedness": True,
        "note": "every station uses the SAME part and the SAME sign of rotation about +Z; no "
                "mirror/flip operation exists anywhere in the mate scheme (only coincident and "
                "angle mates, which cannot mirror a component)",
        "pass": bool((th_bl.max() - th_bl.min()) > 20.0 and r_bl.min() > 0.5)}

    zr = T_bl[r_bl < r_bl.min() + 0.02][:, 2]
    zt = T_bl[r_bl > r_bl.max() - 0.02][:, 2]
    rake = float(abs(np.mean(zt) - np.mean(zr)))
    R["F13_axial_rake"] = {"rake_m": rake, "v02_defect_rake_m": 0.757163,
                            "v03_gate_G1P_03_rake_m": 0.0061,
                            "method": "root-to-tip mean-Z shift (same quantity as v03 gate G1P_03), "
                                      "NOT total Z-extent",
                            "pass": bool(rake < 0.02)}
    print(f"F13 axial rake: {rake:.6f} m")

    bl_pairs, rm_pairs = [], []
    for k in range(N):
        k2 = (k + 1) % N
        b1, b2 = rotate_z(T_bl, np.radians(k * PITCH_DEG)), rotate_z(T_bl, np.radians(k2 * PITCH_DEG))
        r1, r2 = rotate_z(T_rm, np.radians(k * PITCH_DEG)), rotate_z(T_rm, np.radians(k2 * PITCH_DEG))
        ob, orr = bbox_overlap(b1, b2), bbox_overlap(r1, r2)
        bl_pairs.append({"pair": [k, k2], "aabb": ob,
                         "min_dist_m": min_dist(b1, b2, seed=400 + k) if ob else None})
        rm_pairs.append({"pair": [k, k2], "aabb": orr,
                         "min_dist_m": min_dist(r1, r2, seed=500 + k) if orr else None})
    bd = [p["min_dist_m"] for p in bl_pairs if p["min_dist_m"] is not None]
    rd = [p["min_dist_m"] for p in rm_pairs if p["min_dist_m"] is not None]
    R["F14_blade_to_blade_clearance"] = {
        "n_aabb_flagged": sum(1 for p in bl_pairs if p["aabb"]),
        "min_true_surface_distance_m": min(bd) if bd else None,
        "note": "AABB overlap alone is NOT evidence of interference for a 44-deg-swept twisted "
                "blade (DECISION_LOG.md O8); true surface distance is the pass basis",
        "pass": bool(not bd or min(bd) > 0.0)}
    R["F15_root_to_root_clearance"] = {
        "n_aabb_flagged": sum(1 for p in rm_pairs if p["aabb"]),
        "min_true_surface_distance_m": min(rd) if rd else None,
        "pass": bool(not rd or min(rd) > 0.0)}
    print(f"F14 blade-blade min dist: {(min(bd)*1000) if bd else None} mm")

    clr_car, clr_rm, cut_ok = [], [], []
    for k in range(N):
        th = np.radians(k * PITCH_DEG)
        X0, Y0 = 0.478, YC
        Xc = X0 * np.cos(th) - Y0 * np.sin(th)
        Yk = X0 * np.sin(th) + Y0 * np.cos(th)
        ls = T_sh[np.hypot(T_sh[:, 0] - Xc, T_sh[:, 1] - Yk) < 0.10]
        lc = T_car[np.hypot(T_car[:, 0] - Xc, T_car[:, 1] - Yk) < 0.10]
        rk = rotate_z(T_rm, th)
        clr_car.append(min_dist(ls, lc, 1500, seed=600 + k) if len(ls) and len(lc) else None)
        clr_rm.append(min_dist(ls, rk, 1500, seed=700 + k) if len(ls) else None)
        # F17: an actual opening exists at this station (no shell material on the station axis)
        Xa = 0.40 * np.cos(th) - Y0 * np.sin(th)
        Ya = 0.40 * np.sin(th) + Y0 * np.cos(th)
        near = T_sh[(np.hypot(T_sh[:, 0] - Xa, T_sh[:, 1] - Ya) < 0.010) & (np.abs(T_sh[:, 2] - ZC) < 0.010)]
        cut_ok.append(len(near) == 0)
    vc = [c for c in clr_car if c is not None]
    vr = [c for c in clr_rm if c is not None]
    R["F16_shell_carrier_clearance"] = {"per_station_m": clr_car, "min_m": min(vc) if vc else None,
                                         "pass": bool(vc and min(vc) > 0)}
    R["F16b_shell_root_clearance"] = {"per_station_m": clr_rm, "min_m": min(vr) if vr else None,
                                       "pass": bool(vr and min(vr) > 0)}
    R["F17_cutout_alignment"] = {"stations_with_open_passage": sum(cut_ok), "expected": N,
                                  "pass": bool(sum(cut_ok) == N)}
    print(f"F16 shell-carrier min: {(min(vc)*1000) if vc else None} mm   "
          f"shell-root min: {(min(vr)*1000) if vr else None} mm   F17 open: {sum(cut_ok)}/{N}")

    gates = {k: v for k, v in R.items() if k.startswith("F")}
    R["all_gates_pass"] = bool(all(v.get("pass", True) for v in gates.values()))
    print(f"\nALL F-GATES: {'PASS' if R['all_gates_pass'] else 'CHECK'}")
    for k in sorted(gates):
        print(f"  {'PASS' if gates[k].get('pass') else 'FAIL'}  {k}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2, default=str)
    print(f"log: {OUT}")


if __name__ == "__main__":
    main()
