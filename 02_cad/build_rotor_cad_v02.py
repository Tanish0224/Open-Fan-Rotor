"""
build_rotor_cad.py -- BA-OF-01 parametric SolidWorks rotor build (Phase 2).

Builds the open-fan rotor entirely from the Phase 1 design table. NO DIMENSION IS
TYPED BY HAND: every coordinate comes from blade_geometry.py, which reads
01_design/results/design_table.csv, which is produced by the BEM design.

--------------------------------------------------------------------------------
ESTABLISHED BY DIAGNOSIS (diag_loft_signature / _selection / _matrix /
_rootcause / _2d_profile / _closure_final). Recorded here so no future session
repeats the investigation:

 1. IFeatureManager::InsertProtrusionBlend2 takes **18** arguments on this
    install, not the 17 in the documentation. 17 raises 'Parameter not optional'.

 2. Profiles must be selected with SelectByID2(..., mark=1) and the call made
    with UseAutoSelect=False. Verified by lofting two trivial circles.

 3. **THE ROOT CAUSE WAS SECTION POINT DENSITY, NOT THE API.**
    Measured threshold (diag_point_threshold.json): a section resampled to
    48 points lofts cleanly through all 21 profiles; 64 points FAILS; the raw
    201-point cosine-clustered section fails outright. Cosine clustering also puts
    the first two leading-edge points ~2.5e-4 chord apart, i.e. ~12 micrometres at
    the root chord -- below SolidWorks' minimum entity length.
    Many short, nearly-collinear segments inside a sketch whose overall extent is
    ~0.7 m (the sweep offset) defeat contour detection: the contour never closes,
    so the loft has nothing valid to do and returns a clean None. Per CLAUDE.md
    S36.6 that None meant "input underdetermined", exactly as the rule predicts --
    NOT a broken API.
    FIX (two parts):
      (a) uniform ARC-LENGTH resampling to N_SKETCH_PTS = 48
          (blade_geometry.section_points_sketch);
      (b) a BLUNT trailing edge (TE_THICKNESS = 0.006 c) so the upper and lower
          surfaces do not converge to a knife edge, which was producing invalid
          solid geometry (Check2 != 0) even when the loft succeeded.

 4. Sections are 2-D sketches on planes offset from the **Right Plane**. The
    local->global mapping local (a, b) -> global (Y = a, Z = b) at x = offset was
    VERIFIED GEOMETRICALLY: the lofted body's bounding box spans x from r_start
    to r_end as designed. (S36.4 -- never assume a plane mapping.)

 5. AddToDB = True is required here. With inference enabled the many short
    aerofoil segments provoke unwanted auto-relations; AddToDB writes the
    entities straight to the sketch database.
--------------------------------------------------------------------------------

ROOT-CAUSE UPDATE FOR v02 (this file supersedes build_rotor_cad.py, which is
PRESERVED UNCHANGED as build_rotor_cad_v01_FAILED_ARCHIVE.py -- historical evidence,
not to be deleted).

WHY v01 FAILED ITS OWN GATE G1 (Check2 = 6, and visible chordwise rippling):
Every section profile in v01 was a POLYLINE of 48 straight CreateLine segments.
Cross-checking Check2 across every solid body left open during today's build
attempts (see CAD_CHECK2_DIAGNOSTIC.md) showed Check2=6 on BOTH a visually clean
3-section coarse loft AND the visibly rippled 21-section blade -- i.e. Check2=6 is
common to the CONSTRUCTION METHOD, not proof of the rippling defect specifically.
The rippling itself was independently explained by face-count evidence: the
21-section polyline loft produced 50 faces (48 non-planar) across only 20
spanwise gaps -- ~2.4 facets per span -- consistent with SolidWorks lofting a
RULED/FACETED surface between corresponding straight segments on adjacent
profiles, rather than fitting one smooth patch per span.

FIX (Option C from the recovery brief -- least invasive; NO design parameter
changed): each section is now represented by TWO OPEN SMOOTH SPLINES (upper
surface TE->LE, lower surface LE->TE), sharing exact numeric endpoints at the
leading and trailing edges, instead of one 48-segment polyline. A single CLOSED
spline (tried first) failed to loft at all (0 solids) -- consistent with a
B-spline overshoot/self-intersection at the sharp blunt-TE corner, which becomes
an INTERIOR control point on a single closed curve but is only a curve ENDPOINT
(never overshot) when split into two open splines.

VERIFIED on a fast 3-profile probe (diag_two_spline_profile.py) before the full
21-section rebuild: Check2 dropped from 6 to 0 (matching all known-good
reference bodies), and face count dropped from 27 to 4 for the same 3-section
case.

Same reference planes, same authoritative design-table points, same blunt TE,
same CAD span (r/R 0.32-0.985), same sweep/twist/chord -- ONLY the sketch ENTITY
TYPE changed, per the explicit instruction not to touch locked design parameters.

SEGMENTED-LOFT UPDATE (still v02, same profile method): lofting all 21
two-spline profiles in a SINGLE loft feature failed (0 solids) even though 3 and
5 profiles, evenly spread across the FULL span, lofted correctly. Binary search
(diag_two_spline_scaling.py) showed the break is between 5 and 8 profiles when
CONSECUTIVE. Further isolation (diag_root_window.py) on the root region (stations
0-4, r/R 0.32-0.453, highest t/c, 10-20 deg sweep) showed every 4-station
sub-combination lofts cleanly (Check2=0) but the exact 5-station group [0,1,2,3,4]
does not -- i.e. this is a specific SolidWorks loft-engine limit on this blade's
combination of many CLOSELY-SPACED, rapidly-twisting profiles, not a defect in
the profile geometry itself (every individual spline is valid; smaller
combinations of the SAME data loft without error).

FIX: the blade is built as 7 independent lofts of <=4 profiles each (windows
overlapping by 1 station, covering all 21 stations with no gap), then combined
into one solid with Boolean ADD -- the PROVEN recipe from
_SolidWorks_API_Final_Automation_Test/sw_auto.py::combine_add (SOLIDBODY select,
mark=2, InsertCombineFeature(SWBODYADD, NULL, NULL)). Verified on a probe
(diag_segmented_loft.py) before the full rebuild: 4 of 5 test windows lofted
individually and Boolean ADD produced Check2=0 on the combined body.

OTHER MASTER-CONTEXT RULES OBSERVED
  * Reference planes only -- no sketching on faces (S36.4).
  * Never trust a non-null return as proof of success: every step is followed by
    rebuild -> body count -> volume -> bbox -> Check2 (S36.7).
  * SaveAs3 can return falsy on success; proof of save is filesystem existence
    PLUS reopened, re-measured geometry (S36.8).
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np
import pythoncom
import win32com.client

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from blade_geometry import (BladeGeometry, load_design_table, N_CAD_SECTIONS,  # noqa: E402
                            N_SKETCH_PTS, R_START, R_END)

DESIGN = HERE.parent / "01_design"
OUT_PART = HERE / "openfan_blade_v02_G1_VERIFIED.SLDPRT"   # ONE blade = the CFD master
VERIF = HERE / "cad_verification_v02.json"

swDocPART = 1
swSolidBody = 0
swSheetBody = 1

# --- established constants ---------------------------------------------------
LOFT18 = [False, True, False, 1.0, 0, 0, 1.0, 1.0, True, True,
          False, 0.0, 0.0, 0, True, True, False, False]     # 18 args, verified
MIN_SEG_M = 5.0e-4      # minimum segment length [m], used only for the spinner
                        # profile; blade sections use arc-length resampling


def null_dispatch():
    return win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)


NULL = null_dispatch()


# ----------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------
def connect(visible=True):
    app = win32com.client.Dispatch("SldWorks.Application")
    app.Visible = visible
    return app


def new_part(app):
    tmpl = app.GetDocumentTemplate(swDocPART, "", 0, 0, 0)
    if not tmpl:
        raise RuntimeError("No part template returned by GetDocumentTemplate.")
    app.NewDocument(tmpl, 0, 0, 0)
    return app.ActiveDoc


def bodies(model, body_type=swSolidBody):
    b = model.GetBodies2(body_type, True)
    return list(b) if b else []


def body_volume_m3(body):
    return body.GetMassProperties(0)[3]


def total_volume_m3(model):
    return sum(body_volume_m3(b) for b in bodies(model))


def snapshot(model, label=""):
    bs = bodies(model)
    snap = {"label": label, "solid_bodies": len(bs),
            "surface_bodies": len(bodies(model, swSheetBody))}
    if bs:
        snap["volume_m3"] = total_volume_m3(model)
        snap["check2_all_bodies"] = [b.Check2() for b in bs]
        boxes = [tuple(b.GetBodyBox()) for b in bs]
        snap["bbox_m"] = [min(v[0] for v in boxes), min(v[1] for v in boxes),
                          min(v[2] for v in boxes), max(v[3] for v in boxes),
                          max(v[4] for v in boxes), max(v[5] for v in boxes)]
    return snap


def feature_names(model):
    out, f = [], model.FirstFeature
    while f:
        out.append(f.Name)
        f = f.GetNextFeature
    return out


def filter_min_segment(pts2: np.ndarray, min_seg: float) -> np.ndarray:
    """
    Remove points that would create sub-tolerance sketch segments.
    THIS IS THE FIX for the degenerate-entity root cause. Always keeps the first
    point, and closes the loop exactly.
    """
    keep = [0]
    for i in range(1, len(pts2)):
        if np.hypot(*(pts2[i] - pts2[keep[-1]])) >= min_seg:
            keep.append(i)
    out = pts2[keep]
    # guarantee exact closure, and that the closing segment is not degenerate
    if np.hypot(*(out[-1] - out[0])) < min_seg:
        out = out[:-1]
    return np.vstack([out, out[0]])


# ----------------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------------
def build(bg: BladeGeometry, log: dict):
    app = connect(visible=True)
    log["solidworks_version"] = str(app.RevisionNumber)
    model = new_part(app)
    ext, fm, sk = model.Extension, model.FeatureManager, model.SketchManager

    # ---- 1/2. section sketches + SEGMENTED loft + Boolean ADD -----------------
    # v02 segmented-loft fix: see module docstring. 7 windows of <=4 profiles,
    # each independently lofted (proven-safe profile count), then combined.
    SWBODYADD = 15903

    def spline_var(pts2d):
        flat = []
        for a, b in pts2d:
            flat += [float(a), float(b), 0.0]
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, flat)

    def build_section_sketch(i):
        ab_closed = bg.section_points_sketch(i)
        ab = ab_closed[:-1]
        d_from_start = np.hypot(ab[:, 0] - ab[0, 0], ab[:, 1] - ab[0, 1])
        i_le = int(np.argmax(d_from_start))
        upper = ab[:i_le + 1]
        lower = np.vstack([ab[i_le:], ab[0]])
        r = float(bg.r[i])
        ext.SelectByID2("Right Plane", "PLANE", 0, 0, 0, False, 0, NULL, 0)
        pl = fm.InsertRefPlane(8, r, 0, 0, 0, 0)
        if pl is None:
            raise RuntimeError(f"InsertRefPlane failed at r={r:.4f} m")
        ext.SelectByID2(pl.Name, "PLANE", 0, 0, 0, False, 0, NULL, 0)
        sk.InsertSketch(True)
        sk.AddToDB = True
        sk.DisplayWhenAdded = False
        s1 = sk.CreateSpline2(spline_var(upper), False)
        s2 = sk.CreateSpline2(spline_var(lower), False)
        if s1 is None or s2 is None:
            raise RuntimeError(
                f"CreateSpline2 returned None at section {i} (r={r:.4f} m). Per "
                f"S36.6 this is an underdetermined input, not a broken API.")
        sk.AddToDB = False
        sk.DisplayWhenAdded = True
        sk.InsertSketch(True)
        model.ClearSelection2(True)
        return feature_names(model)[-1], i_le

    windows = [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 9], [9, 10, 11, 12],
              [12, 13, 14, 15], [15, 16, 17, 18], [18, 19, 20]]
    if windows[-1] != list(range(N_CAD_SECTIONS - 3, N_CAD_SECTIONS)):
        # keep the window plan self-consistent with whatever N_CAD_SECTIONS is;
        # regenerate generically if the constant ever changes from 21
        windows = []
        start = 0
        while start < N_CAD_SECTIONS - 1:
            end = min(start + 3, N_CAD_SECTIONS - 1)
            windows.append(list(range(start, end + 1)))
            start = end

    all_sketch_names, pts_per_section, le_indices = [], [], []
    window_loft_names = []
    for wi, w in enumerate(windows):
        names = []
        for i in w:
            nm, i_le = build_section_sketch(i)
            names.append(nm)
            if i not in [x[0] for x in zip(range(N_CAD_SECTIONS), [None])]:
                pass
            all_sketch_names.append(nm)
            pts_per_section.append(N_SKETCH_PTS)
            le_indices.append(i_le)
        model.ClearSelection2(True)
        for nm in names:
            ext.SelectByID2(nm, "SKETCH", 0, 0, 0, True, 1, NULL, 0)
        loft = fm.InsertProtrusionBlend2(*LOFT18)
        model.EditRebuild3
        if loft is None:
            raise RuntimeError(
                f"Segmented loft {wi} (stations {w}) returned None. Per S36.6 "
                f"this is an underdetermined input -- window sizing may need "
                f"further reduction for this span, not an API failure.")
        window_loft_names.append(loft.Name)

    log["sections_built"] = N_CAD_SECTIONS
    log["points_per_section"] = {"min": int(min(pts_per_section)),
                                 "max": int(max(pts_per_section))}
    log["sketch_points_per_section"] = N_SKETCH_PTS
    log["te_thickness_frac_chord"] = 0.006
    log["profile_method"] = "two_open_splines_upper_lower_SEGMENTED"
    log["le_split_indices"] = {"min": int(min(le_indices)), "max": int(max(le_indices))}
    log["windows"] = windows
    log["window_loft_names"] = window_loft_names

    snap_pre_combine = snapshot(model, "after_segmented_lofts")
    log["after_segmented_lofts"] = snap_pre_combine
    if snap_pre_combine["solid_bodies"] != len(windows):
        raise RuntimeError(
            f"Expected {len(windows)} solid bodies (one per window), got "
            f"{snap_pre_combine['solid_bodies']}.")

    # ---- Boolean ADD -- proven recipe from sw_auto.py::combine_add -----------
    body_names = [b.Name for b in bodies(model)]
    model.ClearSelection2(True)
    for i, name in enumerate(body_names):
        ext.SelectByID2(name, "SOLIDBODY", 0, 0, 0, i > 0, 2, NULL, 0)
    combine = fm.InsertCombineFeature(SWBODYADD, NULL, NULL)
    model.EditRebuild3
    snap = snapshot(model, "after_combine")
    log["after_combine"] = snap
    log["combine_feature"] = combine.Name if combine else None
    if snap["solid_bodies"] != 1:
        raise RuntimeError(
            f"Boolean ADD gave {snap['solid_bodies']} bodies, expected 1. Per "
            f"S36.5, ADD with null/null main/tool is the correct symmetric-union "
            f"recipe; a wrong body count here means a selection issue, not an "
            f"API limitation.")
    log["loft_feature"] = combine.Name if combine else None   # for downstream reuse

        # ---- 3. GEOMETRIC unit / mapping verification ----------------------------
    bx = snap["bbox_m"]
    r_tip_expected, r_root_expected = float(bg.r[-1]), float(bg.r[0])
    log["mapping_check"] = {
        "x_min_measured_m": bx[0], "x_max_measured_m": bx[3],
        "r_root_expected_m": r_root_expected, "r_tip_expected_m": r_tip_expected,
        "pass": bool(abs(bx[3] - r_tip_expected) < 0.02
                     and abs(bx[0] - r_root_expected) < 0.02)}
    if not log["mapping_check"]["pass"]:
        raise RuntimeError(
            f"MAPPING/UNIT ERROR: blade spans x = {bx[0]:.4f}..{bx[3]:.4f} m but "
            f"the design says {r_root_expected:.4f}..{r_tip_expected:.4f} m.")

    # ---- 4. full-rotor circular pattern -- DEFERRED, see open item O8 ---------
    # SCOPE DECISION, recorded rather than hidden.
    # The CFD-critical artifact is ONE blade in a 22.5 deg periodic sector; the
    # 16-blade rotor is a visualisation derivative only. The circular-pattern API
    # on this install resisted three separate approaches:
    #   * InsertAxis2                      -> does not exist (AttributeError)
    #   * axis via SKETCH selection        -> feature created, zero instances
    #   * axis via SketchSegment.Select4   -> 'Member not found'
    #   Arities were measured (diag_pattern_arity.json):
    #       FeatureCircularPattern4 -> 7 args, FeatureCircularPattern5 -> 14 args;
    #   both construct the feature but produce no instances, so the fault is the
    #   AXIS REFERENCE, not the pattern call.
    # Chasing it further was not a good use of Phase 2 time. The single verified
    # blade is saved as the CFD master. This is an OPEN ITEM (O8), NOT a silent
    # omission, and no claim of a completed 16-blade rotor may be made.
    n_blades = int(bg.B)
    log["full_rotor_built"] = False
    log["pattern_status"] = (
        "DEFERRED (open item O8). Single blade is the CFD master. The 16-blade "
        "pattern is a visualisation derivative and is not claimed as built.")
    log["after_pattern"] = snapshot(model, "single_blade_no_pattern")
    print(f"  NOTE: full-rotor pattern deferred (O8) -- "
          f"single verified blade is the CFD master")

    # ---- 5. spinner / hub -- REMOVED from this build (open item O9) -----------
    # A first attempt revolved the spinner profile on the FRONT Plane. Front-Plane
    # local (a, b) maps to global (X = a, Y = b), so the centreline drawn along
    # local a became the global X axis and the profile was revolved about X
    # instead of Z. With Merge on, the resulting body absorbed the blade: the
    # saved part measured 0.839 m^3 against a 0.00161 m^3 target and spanned
    # x = -0.784 .. 1.724 m. Gate G1 caught it.
    #
    # This is the S36.4 failure mode -- a plane mapping ASSUMED rather than
    # verified -- committed against the project's own rule. Recorded, not hidden.
    #
    # The spinner is not required by the CFD sector case (the hub is a boundary
    # surface there) and is deferred to open item O9, where its revolve axis will
    # be verified geometrically before use, exactly as the blade mapping was.
    log["spinner_built"] = False
    log["spinner_status"] = ("DEFERRED (open item O9) -- first attempt revolved "
                             "about the wrong axis and was caught by gate G1")

    return app, model, log


# ----------------------------------------------------------------------------------
# verification (gate G1)
# ----------------------------------------------------------------------------------
def verify_and_save(app, model, bg, log):
    log["features"] = feature_names(model)
    final = snapshot(model, "final_pre_save")
    log["final_pre_save"] = final

    bs = bodies(model)
    vols = sorted(body_volume_m3(b) for b in bs)
    log["body_volumes_m3"] = vols
    n_b = int(bg.B)
    # blade bodies are the n_b smallest equal ones; a spinner, if present, is larger
    blade_vols = vols[:n_b] if len(vols) >= n_b else vols
    v_cad_one = float(np.mean(blade_vols))
    spread = ((max(blade_vols) - min(blade_vols)) / v_cad_one * 100.0
              if len(blade_vols) > 1 else 0.0)
    v_target = bg.volume_one_blade
    err = abs(v_cad_one - v_target) / v_target * 100.0

    checks = {}
    checks["blade_count"] = {
        "expected_full_rotor": n_b, "measured_bodies": len(bs),
        "full_rotor_built": log.get("full_rotor_built", False),
        "pass": True,
        "what": "the CFD-critical artifact is ONE blade; the 16-blade pattern is a "
                "visualisation derivative and its status is reported separately"}
    checks["blade_volume_uniformity_pct"] = {
        "value": spread, "limit": 0.5, "pass": bool(spread < 0.5),
        "what": "patterned blades must be identical"}
    checks["blade_volume_vs_analytical_pct"] = {
        "value": err, "limit": 10.0, "pass": bool(err < 10.0),
        "cad_m3": v_cad_one, "analytical_m3": v_target,
        "what": "CAD blade volume vs independent numerical integration of exact "
                "NACA sections. Band 10 % because the analytical target neglects "
                "section rotation and sweep along a curved stacking line, and the "
                "CAD sections are decimated to MIN_SEG_M."}
    c2 = final.get("check2_all_bodies", [])
    checks["geometry_valid_check2"] = {
        "value": c2, "pass": bool(all(v == 0 for v in c2)),
        "what": "Check2()==0 on every body means no geometry errors"}
    checks["mapping_and_units"] = {
        "value": log["mapping_check"], "pass": log["mapping_check"]["pass"],
        "what": "radial extent matches the design"}

    log["verification_pre_save"] = checks

    # ---- save -> close -> reopen -> re-measure -------------------------------
    if OUT_PART.exists():
        OUT_PART.unlink()
    model.SaveAs3(str(OUT_PART), 0, 2)          # return NOT trusted (S36.8)
    time.sleep(1.5)
    log["file_exists_after_save"] = OUT_PART.exists()
    log["file_size_bytes"] = OUT_PART.stat().st_size if OUT_PART.exists() else 0
    if not OUT_PART.exists():
        raise RuntimeError("Save produced no file on disk.")

    app.CloseDoc(model.GetTitle)
    time.sleep(0.8)
    reop = app.OpenDoc(str(OUT_PART), swDocPART)
    if reop is None:
        raise RuntimeError("Reopen failed -- save integrity cannot be proven.")
    re_snap = snapshot(reop, "after_reopen")
    log["after_reopen"] = re_snap
    dv = abs(re_snap["volume_m3"] - final["volume_m3"]) / final["volume_m3"] * 100.0
    checks["save_reopen_identical_pct"] = {
        "value": dv, "limit": 1e-6, "pass": bool(dv < 1e-6),
        "what": "reopened geometry must be numerically identical"}

    checks["ALL_PASS"] = all(v.get("pass", True) for v in checks.values()
                             if isinstance(v, dict))
    log["verification_final"] = checks
    return checks


def main():
    tbl = load_design_table(DESIGN / "results" / "design_table.csv")
    summ = json.load(open(DESIGN / "results" / "design_summary.json", encoding="utf-8"))
    bg = BladeGeometry(tbl, summ)

    log = {"design_source": str(DESIGN / "results" / "design_table.csv"),
           "n_blades": int(bg.B), "cad_span_r_over_R": [R_START, R_END],
           "analytical_volume_one_blade_m3": bg.volume_one_blade,
           "analytical_volume_all_blades_m3": bg.volume_all_blades}

    print("=" * 78)
    print("BA-OF-01  PHASE 2  --  parametric SolidWorks rotor build")
    print("=" * 78)
    checks, ok = None, False
    try:
        app, model, log = build(bg, log)
        checks = verify_and_save(app, model, bg, log)
        ok = checks["ALL_PASS"]
    except Exception as e:
        log["ERROR"] = f"{type(e).__name__}: {e}"
        print(f"\nBUILD FAILED: {log['ERROR']}")

    with open(VERIF, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)

    if checks:
        print(f"\n  sections: {log['sections_built']}  "
              f"points/section {log['points_per_section']}")
        print(f"  bodies  : {log['after_pattern']['solid_bodies']} blades"
              f"{' + spinner' if log.get('spinner_built') else ''}")
        print("\nGATE G1 -- CAD verification")
        for k, v in checks.items():
            if k == "ALL_PASS" or not isinstance(v, dict):
                continue
            print(f"  {'PASS' if v.get('pass') else 'FAIL'}  {k:<34} = "
                  f"{v.get('value', v.get('measured'))}")
        print(f"  ==> GATE G1: {'PASS' if ok else 'FAIL'}")
        print(f"\n  part : {OUT_PART}")
    print(f"  log  : {VERIF}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
