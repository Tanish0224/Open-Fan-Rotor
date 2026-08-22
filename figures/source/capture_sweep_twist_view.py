"""
capture_sweep_twist_view.py -- take ONE additional view of the ALREADY-VERIFIED v02 blade
master to show sweep and twist clearly. Read-only: opens the part, sets a standard named view,
takes a screenshot, closes WITHOUT saving. No geometry is created, modified, or analyzed.
"""
import pathlib
import time
import win32com.client
import pythoncom

HERE = pathlib.Path(__file__).parent
CAD = HERE.parent.parent / "02_cad"
PART = CAD / "openfan_blade_v02_G1_VERIFIED.SLDPRT"
OUT = HERE

app = win32com.client.Dispatch("SldWorks.Application")
app.Visible = True
errs = win32com.client.VARIANT(pythoncom.VT_I4 | pythoncom.VT_BYREF, 0)
m = app.OpenDoc6(str(PART), 1, 0, "", errs, errs)
if m is None:
    m = app.OpenDoc(str(PART), 1)
if m is None:
    raise SystemExit("Could not open the verified v02 part -- aborting, no fallback.")

views = {"*Top": "blade_v02_top_sweep_twist", "*Front": "blade_v02_front"}
for name, outname in views.items():
    try:
        r = m.ShowNamedView2(name, -1)
        m.ViewZoomtofit2()
        time.sleep(0.4)
        out = OUT / f"{outname}.bmp"
        ok = m.SaveBMP(str(out), 1400, 900)
        print(name, "-> SaveBMP", ok, "exists:", out.exists())
    except Exception as e:
        print(name, "failed:", e)

app.CloseDoc(m.GetTitle)
print("closed without saving -- v02 master untouched")
