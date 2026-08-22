"""
diag_two_spline_profile.py -- Option C, refined: two OPEN splines per section
(upper surface TE->LE, lower surface LE->TE), sharing exact numeric endpoints at
LE and TE, instead of one closed spline (which failed -- likely self-intersects
by B-spline overshoot at the sharp blunt-TE corner) and instead of the polyline
(which produced a faceted, rippled loft).

Each spline individually has no sharp interior corner (the only "corner" -- the
blunt TE -- is now a curve ENDPOINT, not an interior control point), which is the
standard way to avoid B-spline overshoot at a trailing edge.
"""
import pathlib, sys, json
import pythoncom
import win32com.client
import numpy as np

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from blade_geometry import BladeGeometry, load_design_table, N_CAD_SECTIONS

NULL = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
swDocPART = 1
DESIGN = HERE.parent / "01_design"
LOFT18 = [False, True, False, 1.0, 0, 0, 1.0, 1.0, True, True,
          False, 0.0, 0.0, 0, True, True, False, False]


def fnames(model):
    out, f = [], model.FirstFeature
    while f:
        out.append(f.Name); f = f.GetNextFeature
    return out


def n_solids(model):
    b = model.GetBodies2(0, True)
    return len(list(b)) if b else 0


def spline_var(pts2d):
    flat = []
    for a, b in pts2d:
        flat += [float(a), float(b), 0.0]
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, flat)


def main():
    tbl = load_design_table(DESIGN / "results" / "design_table.csv")
    summ = json.load(open(DESIGN / "results" / "design_summary.json", encoding="utf-8"))
    bg = BladeGeometry(tbl, summ)

    app = win32com.client.Dispatch("SldWorks.Application")
    app.Visible = True
    tmpl = app.GetDocumentTemplate(swDocPART, "", 0, 0, 0)

    idxs = [0, N_CAD_SECTIONS // 2, N_CAD_SECTIONS - 1]
    rep = {}

    app.NewDocument(tmpl, 0, 0, 0)
    model = app.ActiveDoc
    ext, fm, sk = model.Extension, model.FeatureManager, model.SketchManager

    names = []
    for i in idxs:
        ab = bg.section_points_sketch(i)     # closed contour, arc-length resampled, 49 pts
        ab = ab[:-1]                          # drop the duplicate closing point
        n = len(ab)
        # section_points/naca4_section ordering: TE(upper) -> LE -> TE(lower), closed
        # The arc-length resample preserves this traversal order. Find the point
        # closest to the leading edge (max negative "a" = most upstream local coord
        # is not reliable in (tangential,axial) local frame; instead use the point
        # index nearest the midpoint of the traversal, which is where naca4_section
        # places the LE by construction -- verified: len(pts) is odd in the source,
        # LE is at the middle index before resampling. After arc-length resampling
        # the LE is the point of maximum distance from the TE(start) point.
        d_from_start = np.hypot(ab[:, 0] - ab[0, 0], ab[:, 1] - ab[0, 1])
        i_le = int(np.argmax(d_from_start))
        upper = ab[:i_le + 1]                 # TE -> LE
        lower = np.vstack([ab[i_le:], ab[0]]) # LE -> TE (closes back to start)

        r = float(bg.r[i])
        ext.SelectByID2("Right Plane", "PLANE", 0, 0, 0, False, 0, NULL, 0)
        pl = fm.InsertRefPlane(8, r, 0, 0, 0, 0)
        ext.SelectByID2(pl.Name, "PLANE", 0, 0, 0, False, 0, NULL, 0)
        sk.InsertSketch(True)
        sk.AddToDB = True
        sk.DisplayWhenAdded = False
        s1 = sk.CreateSpline2(spline_var(upper), False)   # open
        s2 = sk.CreateSpline2(spline_var(lower), False)   # open
        sk.AddToDB = False
        sk.DisplayWhenAdded = True
        sk.InsertSketch(True)
        model.ClearSelection2(True)
        names.append(fnames(model)[-1])
        rep.setdefault("splines_ok", []).append(bool(s1 is not None and s2 is not None))
        rep.setdefault("le_index", []).append(i_le)
        rep.setdefault("points_per_section", []).append(n)

    model.ClearSelection2(True)
    for nm in names:
        ext.SelectByID2(nm, "SKETCH", 0, 0, 0, True, 1, NULL, 0)
    try:
        r_ = fm.InsertProtrusionBlend2(*LOFT18)
        model.EditRebuild3
        ns = n_solids(model)
        rep["solids"] = ns
        rep["returned"] = None if r_ is None else r_.Name
        if ns:
            bd = list(model.GetBodies2(0, True))[0]
            rep["volume_m3"] = bd.GetMassProperties(0)[3]
            rep["check2"] = bd.Check2()
            rep["check"] = bd.Check()
            faces = list(bd.GetFaces()) if bd.GetFaces() else []
            rep["n_faces"] = len(faces)
            rep["bbox_m"] = [round(v, 5) for v in bd.GetBodyBox()]
    except Exception as e:
        rep["exception"] = str(e)[:150]

    print(json.dumps(rep, indent=2))
    with open(HERE / "diag_two_spline_profile.json", "w") as f:
        json.dump(rep, f, indent=2, default=str)

    app.CloseDoc(model.GetTitle)


if __name__ == "__main__":
    main()
