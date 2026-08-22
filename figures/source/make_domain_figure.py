"""
make_domain_figure.py -- Figure 5: CFD periodic-sector domain schematic, built directly from
the VERIFIED domain parameters (03_cfd/geometry_transfer/build_fluid_domain.py,
03_cfd/zone_definition/ZONE_RECORD.json). No new CFD analysis -- this is a labeled diagram of
already-built, already-verified geometry, not a new solid model or mesh render.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Wedge, Polygon
import numpy as np

# verified parameters (build_fluid_domain.py / domain_verification_v01.json)
R_HUB, R_FAR = 0.49, 7.0
Z0, Z1 = -7.0, 10.5
SECTOR_DEG = 22.5

fig, axes = plt.subplots(1, 2, figsize=(14, 6.6), dpi=200,
                          gridspec_kw={"width_ratios": [2.1, 1]})
ax, ax2 = axes

# ---- left: meridional (R-Z) cross-section, labeled boundaries -----------------
ax.set_xlim(Z0 - 2, Z1 + 2)
ax.set_ylim(-1, R_FAR + 1.5)
ax.set_aspect("equal")
ax.axis("off")

# fluid domain rectangle (R-Z)
dom = Polygon([(Z0, R_HUB), (Z1, R_HUB), (Z1, R_FAR), (Z0, R_FAR)],
              closed=True, facecolor="#dbeeff", edgecolor="none", zorder=1)
ax.add_patch(dom)

# blade schematic footprint (span 0.56-1.72 m). NOTE: sweep in this project is a TANGENTIAL
# (circumferential) offset, not an axial one -- it is correctly shown in the right-hand plan
# view, not here. This left panel deliberately shows only a neutral hatched band at the
# blade's radial span (its true axial position/shape is not fabricated for this schematic).
r_root, r_tip = 0.56, 1.724
band_z0, band_z1 = -0.35, 0.35
ax.add_patch(mpatches.Rectangle((band_z0, r_root), band_z1 - band_z0, r_tip - r_root,
             facecolor="#888888", edgecolor="black", hatch="////", linewidth=1.2, zorder=3,
             alpha=0.55))
ax.annotate("", xy=(band_z0, r_root), xytext=(band_z0, r_root))

# hub line
ax.plot([Z0, Z1], [R_HUB, R_HUB], color="#8a5a00", linewidth=3, zorder=2)
ax.plot([Z0, Z1], [R_FAR, R_FAR], color="#8a1a1a", linewidth=3, zorder=2)
ax.plot([Z0, Z0], [R_HUB, R_FAR], color="#1a4a8a", linewidth=3, zorder=2)
ax.plot([Z1, Z1], [R_HUB, R_FAR], color="#1a6a1a", linewidth=3, zorder=2)

def label(x, y, text, color, ha="center", dy=0.35):
    ax.annotate(text, (x, y), xytext=(x, y + dy), ha=ha, va="bottom", fontsize=10.5,
                weight="bold", color=color,
                arrowprops=dict(arrowstyle="-", color=color, lw=1.2))

label(Z0, (R_HUB + R_FAR) / 2, "INLET\npressure-far-field\nz = -7.0 m", "#1a4a8a", dy=0.0)
label(Z1, (R_HUB + R_FAR) / 2, "OUTLET\npressure-outlet\nz = +10.5 m", "#1a6a1a", dy=0.0)
label((Z0 + Z1) / 2, R_FAR, "FARFIELD  --  pressure-far-field  --  r = 7.0 m", "#8a1a1a", dy=0.25)
label((Z0 + Z1) / 2, R_HUB, "HUB  --  wall  --  r = 0.49 m", "#8a5a00", dy=-0.9)
ax.annotate("BLADE -- wall\n(r = 0.56-1.72 m,\nfootprint schematic only)",
            (band_z1 + 0.3, (r_root + r_tip) / 2),
            fontsize=9.5, weight="bold", color="#2a2a2a", va="center")

ax.set_title("Meridional (R-Z) cross-section -- one 22.5° periodic sector",
              fontsize=11.5, weight="bold", pad=14)

# ---- right: sector plan view (looking down +Z), periodic faces labeled --------
ax2.set_xlim(-1.5, 8.5)
ax2.set_ylim(-1.5, 8.5)
ax2.set_aspect("equal")
ax2.axis("off")

theta = np.linspace(0, np.radians(SECTOR_DEG), 60)
outer = np.column_stack([R_FAR * np.cos(theta), R_FAR * np.sin(theta)])
inner = np.column_stack([R_HUB * np.cos(theta[::-1]), R_HUB * np.sin(theta[::-1])])
sector_pts = np.vstack([outer, inner])
ax2.fill(sector_pts[:, 0], sector_pts[:, 1], facecolor="#dbeeff", edgecolor="#1a1a1a", linewidth=1.2, zorder=1)

# periodic faces (theta=0 and theta=22.5)
p1 = np.array([[R_HUB, 0], [R_FAR, 0]])
p2 = np.array([[R_HUB * np.cos(np.radians(SECTOR_DEG)), R_HUB * np.sin(np.radians(SECTOR_DEG))],
               [R_FAR * np.cos(np.radians(SECTOR_DEG)), R_FAR * np.sin(np.radians(SECTOR_DEG))]])
ax2.plot(p1[:, 0], p1[:, 1], color="#7a1a8a", linewidth=4, zorder=4)
ax2.plot(p2[:, 0], p2[:, 1], color="#c77800", linewidth=4, zorder=4)
ax2.annotate("periodic-1\nθ = 0°", (R_FAR * 0.55, -0.55), color="#7a1a8a",
             fontsize=9.7, weight="bold", ha="center")
ax2.annotate("periodic-2\nθ = 22.5°", (R_FAR * np.cos(np.radians(11)) + 0.3,
             R_FAR * np.sin(np.radians(SECTOR_DEG)) * 0.55 + 1.3), color="#c77800",
             fontsize=9.7, weight="bold", ha="center")
ax2.annotate("hub", (R_HUB * np.cos(np.radians(11)), R_HUB * np.sin(np.radians(11)) - 0.9),
             color="#8a5a00", fontsize=9.5, weight="bold", ha="center")
ax2.annotate("farfield", (R_FAR * np.cos(np.radians(11)), R_FAR * np.sin(np.radians(11)) + 0.5),
             color="#8a1a1a", fontsize=9.5, weight="bold", ha="center")
ax2.annotate("rotation\naxis (+Z\nout of page)", (-0.3, -0.3), fontsize=8.3, color="#444", ha="right")
ax2.set_title("Sector plan (view down +Z) -- 1 of 16 blades\n(exact for the axisymmetric isolated case)",
              fontsize=11.5, weight="bold", pad=10)

fig.suptitle("BA-OF-01 CFD fluid domain -- verified geometry and boundary classification (CFG-ISO, preliminary reduced extents)",
             fontsize=12.6, weight="bold", y=1.01)
note = ("Domain volume independently verified vs. analytic wedge-minus-blade expectation: 0.0006% delta.\n"
        "Boundary classification independently verified by measured centroid/normal/area vs. analytic geometry (≤ 0.16% area error).\n"
        "This figure depicts VERIFIED geometry and topology only -- no mesh or CFD solution exists.")
fig.text(0.5, -0.04, note, ha="center", fontsize=9.3, color="#555555", linespacing=1.5)

plt.tight_layout()
plt.savefig("../05_cfd_domain_boundaries.png", bbox_inches="tight", facecolor="white")
print("wrote 05_cfd_domain_boundaries.png")
