import pathlib, time
import win32com.client

HERE = pathlib.Path(__file__).parent
PART = HERE / "openfan_blade_v01.SLDPRT"

app = win32com.client.Dispatch("SldWorks.Application")
app.Visible = True
errs = win32com.client.VARIANT(win32com.client.pywintypes.VT_BYREF | win32com.client.pywintypes.VT_I4, 0)
m = app.OpenDoc6(str(PART), 1, 0, "", errs, errs)
print("OpenDoc6 result:", m)
if m is None:
    m = app.OpenDoc(str(PART), 1)
    print("fallback OpenDoc result:", m)
if m is None:
    raise SystemExit("Could not open the part.")

for name in ("*Isometric", "*Trimetric"):
    try:
        r = m.ShowNamedView2(name, -1)
        print(name, "->", r)
        break
    except Exception as e:
        print(name, "failed:", e)

m.ViewZoomtofit2()
time.sleep(0.5)
out = HERE / "diagnostics_archive" / "blade_v01_iso.bmp"
ok = m.SaveBMP(str(out), 1100, 850)
print("SaveBMP ->", ok, "exists:", out.exists())
app.CloseDoc(m.GetTitle)
