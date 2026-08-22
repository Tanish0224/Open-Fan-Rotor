"""
make_maturity_figure.py -- Figure 6: project maturity graphic, built directly from the
verification hierarchy already established in BOEING_OPEN_FAN_PROJECT_REPORT.md Section 13.
No new engineering analysis -- a status graphic only.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

rows = [
    ("Aerodynamic design",        "VERIFIED",     "Gate G0 -- 7/7 independent closure checks"),
    ("CAD geometry",               "VERIFIED",     "Gate G1 -- parametric SolidWorks, v02 master"),
    ("CAD verification",           "VERIFIED",     "Check2()=0, independent volume bracket, save/reopen"),
    ("CFD domain geometry",        "VERIFIED",     "volume vs. analytic: 0.0006% delta"),
    ("CFD boundary topology",      "VERIFIED",     "measured zone classification + HDF5 periodic check"),
    ("CFD volume mesh",            "NOT STARTED",  "blocked -- Fluent process-startup stall"),
    ("CFD solver",                 "NOT STARTED",  "no case has been run"),
    ("CFD results",                "NOT STARTED",  "no thrust / torque / power / efficiency exists"),
    ("Experimental validation",    "NOT STARTED",  "no benchmark comparison performed"),
    ("Installed-configuration study", "NOT STARTED", "no installed geometry exists"),
]

GREEN, GREEN_BG = "#1a7f37", "#e6f4ea"
RED, RED_BG = "#8b1a1a", "#faeaea"

fig, ax = plt.subplots(figsize=(11.5, 6.6), dpi=200)
ax.set_xlim(0, 10)
ax.set_ylim(0, len(rows) + 1.3)
ax.axis("off")

ax.text(0.1, len(rows) + 0.75, "BA-OF-01 Boeing Open-Fan Rotor -- project maturity",
        fontsize=15, weight="bold", va="bottom")
ax.text(0.1, len(rows) + 0.28,
        "Verified = a saved artifact exists and was independently checked. Not started = no artifact exists.",
        fontsize=9.7, color="#555555", va="bottom")

row_h = 0.86
for i, (name, status, note) in enumerate(rows):
    y = len(rows) - i - 0.5
    verified = status == "VERIFIED"
    bg = GREEN_BG if verified else RED_BG
    fg = GREEN if verified else RED
    ax.add_patch(mpatches.FancyBboxPatch((0.1, y - row_h / 2 + 0.05), 9.8, row_h - 0.1,
                 boxstyle="round,pad=0.01,rounding_size=0.06", facecolor=bg,
                 edgecolor=fg, linewidth=1.6))
    ax.text(0.35, y, name, fontsize=11.3, weight="bold", va="center", color="#1a1a1a")
    ax.add_patch(mpatches.FancyBboxPatch((5.55, y - 0.19), 1.85, 0.38,
                 boxstyle="round,pad=0.02,rounding_size=0.08", facecolor=fg, edgecolor="none"))
    ax.text(5.55 + 1.85 / 2, y, status, fontsize=9.3, weight="bold", va="center", ha="center", color="white")
    ax.text(7.65, y, note, fontsize=8.6, va="center", color="#444444", style="italic")

plt.tight_layout()
plt.savefig("../06_project_maturity.png", bbox_inches="tight", facecolor="white")
print("wrote 06_project_maturity.png")
