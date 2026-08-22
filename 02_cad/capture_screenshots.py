"""
capture_screenshots.py -- one document open at a time, for the visual record
requested (Part33-equivalent coarse diagnostic vs the real Part65-equivalent
blade, which is openfan_blade_v01.SLDPRT on disk). Minimal RAM footprint: opens,
shoots, closes, one at a time.
"""
import pathlib
import time
import win32com.client

HERE = pathlib.Path(__file__).parent
ARCHIVE = HERE / "diagnostics_archive"
ARCHIVE.mkdir(exist_ok=True)

TARGETS = [
    (HERE / "diagnostics_archive" / "diag_3section_coarse_loft_npts48_REFERENCE.SLDPRT",
     ARCHIVE / "coarse_3section_view.png"),
    (HERE / "openfan_blade_v01.SLDPRT",
     ARCHIVE / "blade_v01_G1FAIL_view.png"),
]

swDocPART = 1


def main():
    app = win32com.client.Dispatch("SldWorks.Application")
    app.Visible = True
    for src, out in TARGETS:
        if not src.exists():
            print(f"MISSING: {src}")
            continue
        m = app.OpenDoc(str(src), swDocPART)
        if m is None:
            print(f"FAILED TO OPEN: {src}")
            continue
        try:
            m.ViewZoomtofit2()
            time.sleep(0.3)
            ok = m.SaveBMP(str(out.with_suffix(".bmp")), 1000, 750)
            print(f"{src.name}: SaveBMP api_return={ok} exists={out.with_suffix('.bmp').exists()}")
        except Exception as e:
            print(f"{src.name}: screenshot error: {e}")
        app.CloseDoc(m.GetTitle)
    print("done")


if __name__ == "__main__":
    main()
