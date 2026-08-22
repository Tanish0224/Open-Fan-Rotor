"""
verify_cad.py -- INDEPENDENT verification of the saved blade part (gate G1).

This does not build anything. It opens the saved SLDPRT fresh, re-measures it,
and compares against the analytical target computed by blade_geometry.py without
SolidWorks. Verifying the saved artifact in a separate process is stronger
evidence than verifying in the build process, because it also proves the file on
disk is what the build thought it made (CLAUDE.md S36.8).
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
from blade_geometry import (BladeGeometry, load_design_table, N_CAD_SECTIONS,  # noqa: E402
                            N_SKETCH_PTS, R_START, R_END)

DESIGN = HERE.parent / "01_design"
PART = HERE / "openfan_blade_v01.SLDPRT"
OUT = HERE / "cad_verification_G1.json"

swDocPART = 1
NULL = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)


def main():
    if not PART.exists():
        print(f"Part not found: {PART}")
        return 1

    tbl = load_design_table(DESIGN / "results" / "design_table.csv")
    summ = json.load(open(DESIGN / "results" / "design_summary.json", encoding="utf-8"))
    bg = BladeGeometry(tbl, summ)

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

    vols = [b.GetMassProperties(0)[3] for b in bs]
    boxes = [tuple(b.GetBodyBox()) for b in bs]
    rep["body_volumes_m3"] = vols
    rep["total_volume_m3"] = float(sum(vols))
    rep["check2_all_bodies"] = [b.Check2() for b in bs]
    rep["bbox_m"] = [min(v[0] for v in boxes), min(v[1] for v in boxes),
                     min(v[2] for v in boxes), max(v[3] for v in boxes),
                     max(v[4] for v in boxes), max(v[5] for v in boxes)]

    v_cad = float(vols[0])
    v_an = bg.volume_one_blade
    err = abs(v_cad - v_an) / v_an * 100.0

    bb = rep["bbox_m"]
    r_root_exp, r_tip_exp = float(bg.r[0]), float(bg.r[-1])
    e_root = abs(bb[0] - r_root_exp)
    e_tip = abs(bb[3] - r_tip_exp)

    checks = {
        "reopened_and_measurable": {
            "value": True, "pass": True,
            "what": "the saved file reopens and yields a measurable solid (S36.8)"},
        "single_blade_body": {
            "value": len(bs), "expected": 1, "pass": bool(len(bs) == 1),
            "what": "the CFD master is ONE blade (22.5 deg sector)"},
        "blade_volume_vs_analytical_pct": {
            "value": err, "limit": 10.0, "pass": bool(err < 10.0),
            "cad_m3": v_cad, "analytical_m3": v_an,
            "what": "CAD volume vs independent numerical integration of the exact "
                    "NACA sections, computed WITHOUT SolidWorks"},
        "radial_root_error_m": {
            "value": e_root, "limit": 0.02, "pass": bool(e_root < 0.02),
            "measured": bb[0], "expected": r_root_exp,
            "what": "blade root radius matches the design"},
        "radial_tip_error_m": {
            "value": e_tip, "limit": 0.02, "pass": bool(e_tip < 0.02),
            "measured": bb[3], "expected": r_tip_exp,
            "what": "blade tip radius matches the design"},
        "geometry_valid_check2": {
            "value": rep["check2_all_bodies"],
            "pass": bool(all(v == 0 for v in rep["check2_all_bodies"])),
            "what": "Check2()==0 means no geometry errors; all 7 known-good "
                    "reference bodies in _SolidWorks_API_Final_Automation_Test "
                    "return 0, so a non-zero value here is a REAL defect"},
    }
    checks["ALL_PASS"] = all(v["pass"] for v in checks.values() if isinstance(v, dict))
    rep["gate_G1"] = checks
    rep["provenance"] = {
        "design_table": str(DESIGN / "results" / "design_table.csv"),
        "n_cad_sections": N_CAD_SECTIONS,
        "sketch_points_per_section": N_SKETCH_PTS,
        "cad_span_r_over_R": [R_START, R_END],
        "no_dimension_typed_by_hand": True,
    }

    app.CloseDoc(model.GetTitle)
    json.dump(rep, open(OUT, "w"), indent=2, default=str)

    print("=" * 74)
    print("BA-OF-01  GATE G1 -- independent verification of the SAVED part")
    print("=" * 74)
    print(f"  file            : {PART.name}  ({rep['file_size_bytes']:,} bytes)")
    print(f"  solid bodies    : {rep['solid_bodies']}")
    print(f"  volume  CAD     : {v_cad*1e6:.2f} cm^3")
    print(f"  volume  target  : {v_an*1e6:.2f} cm^3   (analytical, no SolidWorks)")
    print(f"  volume  error   : {err:.3f} %")
    print(f"  radial extent   : {bb[0]:.5f} .. {bb[3]:.5f} m  "
          f"(design {r_root_exp:.5f} .. {r_tip_exp:.5f})")
    print()
    for k, v in checks.items():
        if k == "ALL_PASS" or not isinstance(v, dict):
            continue
        print(f"  {'PASS' if v['pass'] else 'FAIL'}  {k:<34} = {v['value']}")
    print(f"\n  ==> GATE G1: {'PASS' if checks['ALL_PASS'] else 'FAIL'}")
    print(f"  report -> {OUT}")
    return 0 if checks["ALL_PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
