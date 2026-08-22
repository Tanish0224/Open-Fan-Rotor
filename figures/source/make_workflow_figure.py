"""
make_workflow_figure.py -- Figure 4: engineering workflow diagram, built purely from the
project's own recorded stage status (BOEING_OPEN_FAN_PROJECT_REPORT.md / PROJECT_STATUS.md).
No new engineering analysis; this is a status diagram, not a data plot.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

GREEN = "#1a7f37"
GREEN_BG = "#e6f4ea"
GREY = "#666666"
GREY_BG = "#eeeeee"
TEXT = "#1a1a1a"

stages = [
    ("Requirements &\nnon-dimensional loading", "VERIFIED", "00_requirements/\nPROJECT_REQUIREMENTS.md"),
    ("First-principles\naerodynamic design (BEM)", "VERIFIED\nGate G0: 7/7", "01_design/\nopenfan_design.py"),
    ("Geometry generation\n(radial stations, sweep law)", "VERIFIED", "01_design/results/\ndesign_table.csv"),
    ("Parametric SolidWorks CAD\n+ independent verification", "VERIFIED\nGate G1: 6/6", "02_cad/\nopenfan_blade_v02_G1_VERIFIED"),
    ("CFD domain + boundary\ntopology (periodic sector)", "VERIFIED", "03_cfd/zone_definition/\nZONE_RECORD.json"),
    ("Volume mesh,\nsolver, results", "NOT STARTED", "03_cfd/CFD_STATUS.md"),
]

fig, ax = plt.subplots(figsize=(15.5, 3.4), dpi=200)
ax.set_xlim(0, len(stages))
ax.set_ylim(0, 1)
ax.axis("off")

box_w, box_h = 0.86, 0.62
y0 = 0.22

for i, (title, status, evidence) in enumerate(stages):
    x = i + 0.07
    verified = status.startswith("VERIFIED")
    fc = GREEN_BG if verified else GREY_BG
    ec = GREEN if verified else GREY
    box = FancyBboxPatch((x, y0), box_w, box_h, boxstyle="round,pad=0.02,rounding_size=0.04",
                          linewidth=2.2, edgecolor=ec, facecolor=fc)
    ax.add_patch(box)
    ax.text(x + box_w / 2, y0 + box_h - 0.12, title, ha="center", va="top",
            fontsize=10.3, weight="bold", color=TEXT, linespacing=1.3)
    status_color = GREEN if verified else "#8b1a1a"
    ax.text(x + box_w / 2, y0 + 0.19, status, ha="center", va="center",
            fontsize=9.3, weight="bold", color=status_color)
    ax.text(x + box_w / 2, y0 - 0.07, evidence, ha="center", va="top",
            fontsize=7.6, color="#555555", family="monospace", linespacing=1.3)

    if i < len(stages) - 1:
        arrow = FancyArrowPatch((x + box_w + 0.005, y0 + box_h / 2),
                                 (x + box_w + 0.115, y0 + box_h / 2),
                                 arrowstyle="-|>", mutation_scale=16,
                                 linewidth=2, color="#333333")
        ax.add_patch(arrow)

ax.text(len(stages) / 2, 0.98, "BA-OF-01 Boeing Open-Fan Rotor -- engineering workflow and current verification status",
        ha="center", va="top", fontsize=12.5, weight="bold", color=TEXT)

legend_elems = [
    mpatches.Patch(facecolor=GREEN_BG, edgecolor=GREEN, linewidth=2, label="Completed and independently verified"),
    mpatches.Patch(facecolor=GREY_BG, edgecolor=GREY, linewidth=2, label="Not yet started"),
]
ax.legend(handles=legend_elems, loc="lower center", bbox_to_anchor=(0.5, -0.14),
          ncol=2, frameon=False, fontsize=9.5)

plt.tight_layout()
plt.savefig("../04_workflow_status.png", bbox_inches="tight", facecolor="white")
print("wrote 04_workflow_status.png")
