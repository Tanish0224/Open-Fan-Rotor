"""
verify_cad_v02.py -- INDEPENDENT verification of the v02 saved part (gate G1),
in a SEPARATE process from the build, with full topology diagnostics per the
recovery-task requirement (not volume/Check2 alone).
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pythoncom
import win32com.client

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from blade_geometry import BladeGeometry, load_design_table, N_CAD_SECTIONS, R_START, R_END  # noqa: E402

DESIGN = HERE.parent / "01_design"
PART = HERE / "openfan_blade_v02_G1_VERIFIED.SLDPRT"
OUT = HERE / "cad_verification_v02_G1_independent.json"

swDocPART = 1
NULL = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)


def topology_diagnostics(body):
    faces = list(body.GetFaces()) if body.GetFaces() else []
    face_kinds = {"plane": 0, "cylinder": 0, "cone": 0, "sphere": 0,
                 "torus": 0, "bspline_or_other": 0}
    n_face_edge_refs = 0
    for f in faces:
        s = f.GetSurface
        if s is None:
            face_kinds["bspline_or_other"] += 1
        elif s.IsPlane:
            face_kinds["plane"] += 1
        elif s.IsCylinder:
            face_kinds["cylinder"] += 1
        elif s.IsCone:
            face_kinds["cone"] += 1
        elif s.IsSphere:
            face_kinds["sphere"] += 1
        elif s.IsTorus:
            face_kinds["torus"] += 1
        else:
            face_kinds["bspline_or_other"] += 1
        edges = f.GetEdges
        el = list(edges) if edges else []
        n_face_edge_refs += len(el)

    return {
        "n_faces": len(faces),
        "face_kinds": face_kinds,
        "n_face_edge_references": n_face_edge_refs,
        # edge_ids/vertex_ids identity dedup is unreliable via late-bound COM wrappers
        # (each GetEdges() call can return NEW wrapper objects for the same
        # underlying edge), so a true unique edge/vertex COUNT is not reliably
        # obtainable this way. This limitation is stated rather than reporting a
        # number that looks precise but is not: face-count and face-kind counts
        # ARE reliable (queried once per session, no identity comparison needed).
        "note_on_edge_vertex_counts": "Unique edge/vertex counts via COM object "
                                      "identity are unreliable under late binding "
                                      "(GetEdges may return new wrapper instances "
                                      "per call) and are not reported as a precise "
                                      "number for that reason -- not because the "
                                      "check was skipped.",
    }


def main():
    if not PART.exists():
        print(f"Part not found: {PART}")
        return 1

    tbl = load_design_table(DESIGN / "results" / "design_table.csv")
    summ = json.load(open(DESIGN / "results" / "design_summary.json", encoding="utf-8"))
    bg = BladeGeometry(tbl, summ)

    ref = json.load(open(HERE / "blade_geometry_reference.json", encoding="utf-8"))
    v_lower = ref["2a_cad_input_polygon_lower_bound"]["volume_one_blade_m3"]
    v_upper = ref["1_design_idealisation_smooth_closed_form"]["volume_one_blade_m3"]

    app = win32com.client.Dispatch("SldWorks.Application")
    app.Visible = True
    model = app.OpenDoc(str(PART), swDocPART)
    if model is None:
        print("Reopen FAILED -- save integrity cannot be proven.")
        return 1

    bs = model.GetBodies2(0, True)
    bs = list(bs) if bs else []
    sheets = model.GetBodies2(1, True)
    n_sheet = len(list(sheets)) if sheets else 0

    rep = {
        "part_file": str(PART),
        "file_size_bytes": PART.stat().st_size,
        "reopened_ok": True,
        "solid_bodies": len(bs),
        "surface_bodies": n_sheet,
    }
    if not bs:
        rep["FATAL"] = "no solid body in the saved part"
        json.dump(rep, open(OUT, "w"), indent=2)
        print(rep["FATAL"])
        return 1

    b = bs[0]
    vol = b.GetMassProperties(0)[3]
    bbox = tuple(b.GetBodyBox())
    check2 = b.Check2()
    check1 = b.Check()
    topo = topology_diagnostics(b)

    rep["volume_m3"] = vol
    rep["bbox_m"] = bbox
    rep["check2"] = check2
    rep["check1"] = check1
    rep["topology"] = topo

    r_root_exp, r_tip_exp = float(bg.r[0]), float(bg.r[-1])
    e_root = abs(bbox[0] - r_root_exp)
    e_tip = abs(bbox[3] - r_tip_exp)

    in_bracket = bool(v_lower * 0.98 <= vol <= v_upper * 1.02)   # small margin either side

    checks = {
        "reopened_and_measurable": {"value": True, "pass": True},
        "single_solid_body": {"value": len(bs), "expected": 1,
                              "pass": bool(len(bs) == 1)},
        "zero_unintended_surface_bodies": {"value": n_sheet, "pass": bool(n_sheet == 0)},
        "check2_matches_known_good_reference": {
            "value": check2, "expected": 0, "pass": bool(check2 == 0),
            "what": "all 7 known-good reference bodies in "
                    "_SolidWorks_API_Final_Automation_Test return Check2()==0"},
        "volume_within_independent_bracket": {
            "value": vol, "lower_bound_m3": v_lower, "upper_bound_m3": v_upper,
            "pass": in_bracket,
            "what": "bracket computed WITHOUT SolidWorks from the exact final "
                    "section data (see blade_geometry_reference.json): "
                    "[48-point polygon lower bound, smooth closed-form upper bound]"},
        "radial_root_error_m": {"value": e_root, "limit": 0.02,
                                "pass": bool(e_root < 0.02)},
        "radial_tip_error_m": {"value": e_tip, "limit": 0.02,
                               "pass": bool(e_tip < 0.02)},
        "no_negative_or_degenerate_bbox": {
            "value": bbox, "pass": bool(bbox[3] > bbox[0] and bbox[4] > bbox[1]
                                        and bbox[5] > bbox[2]),
            "what": "catches the v01 wrong-axis-spinner failure mode "
                    "(negative/absurd bbox extent) directly"},
    }
    checks["ALL_PASS"] = all(v["pass"] for v in checks.values())
    rep["gate_G1"] = checks

    app.CloseDoc(model.GetTitle)
    json.dump(rep, open(OUT, "w"), indent=2, default=str)

    print("=" * 78)
    print("BA-OF-01  GATE G1 (v02) -- independent verification, separate process")
    print("=" * 78)
    print(f"  file       : {PART.name}  ({rep['file_size_bytes']:,} bytes)")
    print(f"  solids     : {len(bs)}   surfaces: {n_sheet}")
    print(f"  volume     : {vol*1e6:.2f} cm^3")
    print(f"  bracket    : [{v_lower*1e6:.2f}, {v_upper*1e6:.2f}] cm^3")
    print(f"  Check()    : {check1}    Check2(): {check2}")
    print(f"  faces      : {topo['n_faces']}  {topo['face_kinds']}")
    print(f"  bbox       : {bbox}")
    print()
    for k, v in checks.items():
        if k == "ALL_PASS" or not isinstance(v, dict):
            continue
        print(f"  {'PASS' if v['pass'] else 'FAIL'}  {k:<38} = {v.get('value')}")
    print(f"\n  ==> GATE G1: {'PASS' if checks['ALL_PASS'] else 'FAIL'}")
    print(f"  report -> {OUT}")
    return 0 if checks["ALL_PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
