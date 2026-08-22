"""
diag_two_spline_scaling.py -- the two-spline profile worked at 3 sections but
failed at 21. Binary-search the profile count to find where it breaks, and
whether it's a COUNT issue or a specific problem STATION.
"""
import pathlib, sys, json
import pythoncom, win32com.client
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


def try_n_profiles(app, tmpl, bg, idxs):
    app.NewDocument(tmpl, 0, 0, 0)
    model = app.ActiveDoc
    ext, fm, sk = model.Extension, model.FeatureManager, model.SketchManager
    names = []
    for i in idxs:
        ab_closed = bg.section_points_sketch(i)
        ab = ab_closed[:-1]
        d_from_start = np.hypot(ab[:, 0] - ab[0, 0], ab[:, 1] - ab[0, 1])
        i_le = int(np.argmax(d_from_start))
        upper = ab[:i_le + 1]
        lower = np.vstack([ab[i_le:], ab[0]])
        r = float(bg.r[i])
        ext.SelectByID2("Right Plane", "PLANE", 0, 0, 0, False, 0, NULL, 0)
        pl = fm.InsertRefPlane(8, r, 0, 0, 0, 0)
        ext.SelectByID2(pl.Name, "PLANE", 0, 0, 0, False, 0, NULL, 0)
        sk.InsertSketch(True)
        sk.AddToDB = True
        sk.DisplayWhenAdded = False
        sk.CreateSpline2(spline_var(upper), False)
        sk.CreateSpline2(spline_var(lower), False)
        sk.AddToDB = False
        sk.DisplayWhenAdded = True
        sk.InsertSketch(True)
        model.ClearSelection2(True)
        names.append(fnames(model)[-1])

    model.ClearSelection2(True)
    for nm in names:
        ext.SelectByID2(nm, "SKETCH", 0, 0, 0, True, 1, NULL, 0)
    try:
        r_ = fm.InsertProtrusionBlend2(*LOFT18)
        model.EditRebuild3
        ns = n_solids(model)
        row = {"idxs": idxs, "n_profiles": len(idxs), "solids": ns}
        if ns:
            bd = list(model.GetBodies2(0, True))[0]
            row["volume_m3"] = bd.GetMassProperties(0)[3]
            row["check2"] = bd.Check2()
    except Exception as e:
        row = {"idxs": idxs, "n_profiles": len(idxs), "exception": str(e)[:100]}
    app.CloseDoc(model.GetTitle)
    return row


def main():
    tbl = load_design_table(DESIGN / "results" / "design_table.csv")
    summ = json.load(open(DESIGN / "results" / "design_summary.json", encoding="utf-8"))
    bg = BladeGeometry(tbl, summ)
    app = win32com.client.Dispatch("SldWorks.Application")
    app.Visible = True
    tmpl = app.GetDocumentTemplate(swDocPART, "", 0, 0, 0)

    results = []
    # test increasing counts, evenly spread each time
    for n in (3, 5, 8, 12, 16, 21):
        idxs = list(np.linspace(0, N_CAD_SECTIONS - 1, n).astype(int))
        idxs = sorted(set(idxs))
        row = try_n_profiles(app, tmpl, bg, idxs)
        print(f"n={n:>2} (actual {len(idxs)}) -> solids={row.get('solids')} "
              f"check2={row.get('check2')} {row.get('exception','')}")
        results.append(row)

    with open(HERE / "diag_two_spline_scaling.json", "w") as f:
        json.dump(results, f, indent=2, default=str)


if __name__ == "__main__":
    main()
