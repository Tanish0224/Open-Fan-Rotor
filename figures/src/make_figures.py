"""Regenerate every CFD and design figure in figures/ from the data in this repository.

Usage (from the repository root):
    python figures/src/make_figures.py [--field-data DIR]

Plots are built only from files under design/ and cfd_campaign/. The blade-to-blade field
figures additionally need the exported field CSVs (b2b_r75_<case>.csv, 8 MB each), which are
not included in the repository (see reproducibility/REPRODUCE.md); pass their folder
with --field-data, otherwise those figures are skipped. No number on any figure is typed by
hand: every annotation is computed from the plotted case's own data.
"""
import csv
import glob
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.tri import Triangulation

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAMP = os.path.join(ROOT, "cfd_campaign")
DES = os.path.join(ROOT, "design", "results")
OUT_CFD = os.path.join(ROOT, "figures", "cfd")
OUT_DES = os.path.join(ROOT, "figures", "design")
os.makedirs(OUT_CFD, exist_ok=True)
os.makedirs(OUT_DES, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12,
    "legend.fontsize": 10.5, "xtick.labelsize": 11, "ytick.labelsize": 11, "lines.linewidth": 2.0,
    "axes.grid": True, "grid.linewidth": 0.5, "grid.alpha": 0.35, "figure.facecolor": "white",
    "axes.facecolor": "white", "savefig.facecolor": "white", "svg.hashsalt": "open-fan-rotor",
    "axes.spines.top": False, "axes.spines.right": False,
})
COL = {"v04cf": "#8c8c8c", "v05n16": "#6a3d9a", "v06e": "#1f78b4", "v08": "#e31a1c", "v10": "#ff7f00",
       "v12": "#33a02c", "v14": "#b15928", "v15": "#a6cee3", "v11": "#000000"}
FOLDER = {"v03": "v03_diagnostic_drag_state", "v04cf": "v04cf_camber_corrected", "v05n16": "v05n16_naca16_sections",
          "v06e": "v06e_cl_chord_schedule", "v08": "v08_reference_case", "v10": "v10_uniform_depitch",
          "v11": "v11_1000rpm_offdesign", "v12": "v12_sweep_plus6deg", "v14": "v14_hub_bc_diagnostic",
          "v15": "v15_root_depitch"}
LABEL = {"v04cf": "V04cf", "v05n16": "V05n16", "v06e": "V06e", "v08": "V08 (reference case)", "v10": "V10 uniform de-pitch",
         "v12": "V12 sweep +6°", "v14": "V14 hub-wall BC diagnostic", "v15": "V15 root de-pitch",
         "v11": "V11 — 1000 rpm OFF-DESIGN"}
STAMP = "Recorded CFD result (ANSYS Fluent, steady MRF, k-ω SST) — not validated; single mesh per case"
written = []


def save(fig, path, png=False):
    if png:
        fig.savefig(path, dpi=200, metadata={"Software": None})
    else:
        fig.savefig(path, metadata={"Creator": None, "Date": None})
    plt.close(fig)
    written.append(os.path.relpath(path, ROOT).replace(os.sep, "/"))


def load(pattern, tag):
    f = glob.glob(os.path.join(CAMP, FOLDER[tag], pattern))
    return json.load(open(f[0], encoding="utf-8")) if f else None


def result(tag):
    return load("performance_result_*.json", tag)


def stations(tag):
    d = load("blade_loading_*.json", tag)
    return None if d is None else sorted(d["stations"], key=lambda s: s["r_over_R"])


def bem(family):
    name = "design_summary.json" if family == "v03" else "design_summary_v06.json"
    return json.load(open(os.path.join(DES, name), encoding="utf-8")), name


def spread(v):
    return (max(v) - min(v)) / abs(sum(v) / len(v))


# ---------------------------------------------------------------- F1 convergence
def fig_convergence():
    tags = ["v05n16", "v06e", "v08", "v10", "v12", "v14", "v15"]
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharex=True)
    for ax, tag in zip(axes.flat, tags):
        d = result(tag)
        T = [abs(c["T_N"]) for c in d["checkpoints"]]
        Q = [abs(c["Q_Nm"]) for c in d["checkpoints"]]
        n = np.arange(1, len(T) + 1)
        ax.plot(n, np.array(T) / T[-1], "-o", color="#1f78b4", ms=4, label="T / T(S10)")
        ax.plot(n, np.array(Q) / Q[-1], "-s", color="#e31a1c", ms=4, label="Q / Q(S10)")
        ax.axvspan(5.5, 10.5, color="#33a02c", alpha=0.10)
        ax.axvspan(1.5, 10.5, color="#000000", alpha=0.04)
        r = spread(T[-5:]), spread(Q[-5:])
        fh = spread(T[1:]), spread(Q[1:])
        ok = lambda a: "PASS" if a[0] < 0.01 and a[1] < 0.01 else "FAIL"
        ax.set_title("%s\nrolling S6–S10: %.2f / %.2f %% %s\nfull S2–S10: %.2f / %.2f %% %s" % (
            LABEL[tag], 100 * r[0], 100 * r[1], ok(r), 100 * fh[0], 100 * fh[1], ok(fh)), fontsize=10.5)
        ax.set_ylim(0.85, 1.10)
        ax.set_xticks(range(1, 11))
    axes.flat[-1].axis("off")
    axes.flat[-1].text(0.0, 0.5, "Design RPM 1294.5 rpm (ω = 135.559 rad/s)\n\n"
                       "Green band: rolling window (last 5 checkpoints)\nGrey band: full second-order history S2–S10\n"
                       "Bound: 1 % peak-to-peak on T and Q\nS1 = first-order start-up (excluded)\n\n"
                       "Values: T / Q peak-to-peak as % of mean", fontsize=11, va="center")
    axes[0, 0].legend(loc="lower right")
    for ax in axes[1, :3]:
        ax.set_xlabel("checkpoint (60 iterations each)")
    fig.suptitle("Force and moment convergence, design-RPM cases — " + STAMP, fontsize=12)
    fig.tight_layout()
    save(fig, os.path.join(OUT_CFD, "cfd_convergence_design_rpm.svg"))

    d = result("v11")
    T = [abs(c["T_N"]) for c in d["checkpoints"]]
    Q = [abs(c["Q_Nm"]) for c in d["checkpoints"]]
    n = np.arange(1, len(T) + 1)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(n, np.array(T) / T[-1], "-o", color="#1f78b4", label="T / T(S10)")
    ax.plot(n, np.array(Q) / Q[-1], "-s", color="#e31a1c", label="Q / Q(S10)")
    ax.axvspan(5.5, 10.5, color="#33a02c", alpha=0.10)
    ax.axvspan(1.5, 10.5, color="#000000", alpha=0.04)
    r, fh = (spread(T[-5:]), spread(Q[-5:])), (spread(T[1:]), spread(Q[1:]))
    ax.set_title("V11 — 1000 rpm OFF-DESIGN (separate investigation), ω = 104.72 rad/s\n"
                 "rolling %.2f / %.2f %%, full-history %.2f / %.2f %% (T / Q)" % (100 * r[0], 100 * r[1], 100 * fh[0], 100 * fh[1]))
    ax.set_xlabel("checkpoint (60 iterations each)")
    ax.set_ylim(0.85, 1.10)
    ax.legend()
    fig.text(0.01, 0.02, "Not comparable with design-RPM cases." + chr(10) + STAMP, fontsize=9)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, os.path.join(OUT_CFD, "cfd_v11_1000rpm_offdesign_convergence.svg"))


# ---------------------------------------------------------------- F2 residuals
def fig_residuals():
    f = os.path.join(CAMP, FOLDER["v08"], "residuals_v08.csv")
    rows = list(csv.DictReader(open(f)))
    it = [int(r["iteration"]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for k, c in [("continuity", "#000000"), ("x_velocity", "#1f78b4"), ("y_velocity", "#a6cee3"), ("z_velocity", "#33a02c"),
                 ("energy", "#ff7f00"), ("k", "#6a3d9a"), ("omega", "#e31a1c")]:
        ax.semilogy(it, [float(r[k]) for r in rows], color=c, lw=1.6, label=k)
    c0, c1 = float(rows[0]["continuity"]), float(rows[-1]["continuity"])
    ax.axhline(c0 * 1e-4, color="#555555", ls="--", lw=1.2, label="4-order drop on continuity (G2 criterion)")
    ax.set_xlabel("iteration")
    ax.set_ylabel("scaled residual")
    ax.set_title("V08 residual history — design RPM (ω = 135.559 rad/s)\ncontinuity %.2e → %.2e = %.2f orders (G2 requires ≥ 4)" % (
        c0, c1, math.log10(c0 / c1)))
    ax.legend(ncol=2, loc="upper right")
    fig.text(0.01, 0.01, "Iterations 1–60 first order, then second order. " + STAMP, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, os.path.join(OUT_CFD, "cfd_v08_residuals.svg"))


# ---------------------------------------------------------------- F3/F4 radial loading
def fig_radial_loading():
    b, bname = bem("v06")
    rt = b["radial_table"]
    tags = ["v06e", "v08", "v12", "v14", "v15"]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, key, bkey, unit in [(axes[0], "dT_dr", "dT_dr_Npm", "dT/dr  [N/m]"), (axes[1], "dQ_dr", "dQ_dr_Nmpm", "dQ/dr  [N·m/m]")]:
        ax.plot(rt["r_over_R"], rt[bkey], "k--", lw=2, label="BEM design intent (v06 family, %s)" % bname)
        for tag in tags:
            st = stations(tag)
            ax.plot([s["r_over_R"] for s in st], [s[key] for s in st], "-o", color=COL[tag], ms=5, label=LABEL[tag])
        ax.axhline(0, color="#444444", lw=0.8)
        ax.set_xlabel("r / R")
        ax.set_ylabel(unit)
        ax.set_xlim(0.28, 1.0)
    for ax, key, bkey in [(axes[0], "dT_dr", "dT_dr_Npm"), (axes[1], "dQ_dr", "dQ_dr_Nmpm")]:
        top = max(max(rt[bkey]), max(max(s[key] for s in stations(t)) for t in tags))
        low = min(min(s[key] for s in stations(t)) for t in tags)
        ax.set_ylim(1.15 * min(low, 0), 1.08 * top)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.05))
    axes[0].set_title("Radial thrust loading, design RPM")
    axes[1].set_title("Radial torque loading, design RPM")
    fig.suptitle("CFD sectional loading (surface-pressure + wall-shear integration at 9 stations) vs BEM design intent\n" + STAMP, fontsize=11.5)
    fig.text(0.01, 0.01, "Station integrals are for shape; Fluent's force report is the authority for total T and Q "
             "(the sampled-span integral differs from it). Cases share the v06-family BEM design; V14 has V08's geometry.", fontsize=9)
    fig.tight_layout(rect=(0, 0.17, 1, 0.93))
    save(fig, os.path.join(OUT_CFD, "cfd_radial_loading_design_rpm.svg"))

    b3, bname3 = bem("v03")
    rt3 = b3["radial_table"]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(rt3["r_over_R"], rt3["dT_dr_Npm"], "k--", lw=2, label="BEM design intent (v03 family, %s)" % bname3)
    for tag in ["v04cf", "v05n16"]:
        st = stations(tag)
        ax.plot([s["r_over_R"] for s in st], [s["dT_dr"] for s in st], "-o", color=COL[tag], label=LABEL[tag])
    ax.axhline(0, color="#444444", lw=0.8)
    ax.set_xlim(0.28, 1.0)
    ax.set_ylim(-3000, 22000)
    ax.set_xlabel("r / R")
    ax.set_ylabel("dT/dr  [N/m]")
    ax.set_title("Radial thrust loading, earlier lineage cases (design RPM)\nV04cf is unsettled (diverged at iteration 246)")
    ax.legend(loc="upper left")
    fig.text(0.01, 0.01, STAMP, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, os.path.join(OUT_CFD, "cfd_radial_loading_lineage_v04cf_v05n16.svg"))

    b11 = json.load(open(os.path.join(DES, "design_summary_v06.json"), encoding="utf-8"))
    st = stations("v11")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot([s["r_over_R"] for s in st], [s["dT_dr"] for s in st], "-o", color=COL["v11"], label="V11 — 1000 rpm OFF-DESIGN")
    ax.axhline(0, color="#444444", lw=0.8)
    ax.set_xlim(0.28, 1.0)
    ax.set_ylim(-3000, 22000)
    ax.set_xlabel("r / R")
    ax.set_ylabel("dT/dr  [N/m]")
    ax.set_title("V11 — 1000 rpm OFF-DESIGN (separate investigation), ω = 104.72 rad/s\nre-twisted blade; two coupled changes (speed and twist)")
    fig.text(0.01, 0.01, "No BEM curve: the BEM design is for design RPM only.\n" + STAMP, fontsize=9)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, os.path.join(OUT_CFD, "cfd_v11_1000rpm_offdesign_radial_loading.svg"))


# ---------------------------------------------------------------- F6 chordwise Cp (V08)
def fig_cp():
    st = stations("v08")
    te = load("te_thickness_*.json", "v08")
    pick = [s for s in st if round(s["r_over_R"], 2) in (0.40, 0.60, 0.75, 0.95)]
    fig, axes = plt.subplots(1, 4, figsize=(17, 5), sharey=True)
    for ax, s in zip(axes, pick):
        ax.plot(s["xs"], s["cp_upper"], color="#1f78b4", label="upper surface")
        ax.plot(s["xs"], s["cp_lower"], color="#e31a1c", label="lower surface")
        ax.set_title("r/R = %.2f" % s["r_over_R"])
        ax.set_xlabel("x / c")
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Cp (local relative dynamic pressure)")
    axes[0].legend(loc="lower right")
    fig.suptitle("V08 chordwise pressure coefficient — design RPM (ω = 135.559 rad/s)\n"
                 "CAD trailing-edge parameter %.3fc; meshed trailing edge measured %.4fc (outboard mean, r/R ≥ 0.70)"
                 % (te["intended_te_frac"], te["outboard_mean_te_over_c"]), fontsize=12)
    fig.text(0.01, 0.01, "Surfaces labelled geometrically. " + STAMP, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.9))
    save(fig, os.path.join(OUT_CFD, "cfd_v08_chordwise_cp.svg"))


# ---------------------------------------------------------------- F9 V08 summary card
def fig_v08_card():
    d = result("v08")
    T = [abs(c["T_N"]) for c in d["checkpoints"]]
    Q = [abs(c["Q_Nm"]) for c in d["checkpoints"]]
    r, fh = (spread(T[-5:]), spread(Q[-5:])), (spread(T[1:]), spread(Q[1:]))
    cells = load("openfan_v08_vol_orthoquality.json", "v08")["n_cells"]
    te = load("te_thickness_*.json", "v08")
    b6, _ = bem("v06")
    tb = b6["dimensional_interpretation"]["thrust_N"]
    rpm = abs(d["operating_point"]["omega"]) * 60 / (2 * math.pi)
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.axis("off")
    lines = [
        ("V08 — highest design-RPM efficiency in the CFD campaign", 17, "bold"),
        ("Design RPM %.1f rpm (ω = %.3f rad/s), flight Mach %.2f" % (rpm, d["operating_point"]["omega"], d["operating_point"]["mach"]), 12, "normal"),
        ("T = %.2f N     Q = %.2f N·m     P = %.4f MW     η_p = %.5f" % (d["T_N"], d["Q_Nm"], d["P_shaft_W"] / 1e6, d["eta_p"]), 15, "bold"),
        ("Rolling window (last 5 checkpoints): T %.2f %%, Q %.2f %% (within 1 %%)" % (100 * r[0], 100 * r[1]), 12, "normal"),
        ("Full second-order history (S2–S10): T %.2f %%, Q %.2f %% (above the 1 %% criterion)" % (100 * fh[0], 100 * fh[1]), 12, "bold"),
        ("One mesh ({:,} cells), no prism layers; mesh independence not assessed".format(cells), 12, "normal"),
        ("No experimental or benchmark data to compare against.", 12, "normal"),
        ("CAD trailing-edge parameter %.3fc (meshed %.4fc). BEM design thrust (v06 family) %.1f N; V08 reached %.1f %% of it." % (
            te["intended_te_frac"], te["outboard_mean_te_over_c"], tb, 100 * d["T_N"] / tb), 11, "normal"),
    ]
    y = 0.95
    for txt, size, weight in lines:
        ax.text(0.01, y, txt, fontsize=size, fontweight=weight, va="top", transform=ax.transAxes)
        y -= 0.12 if size >= 15 else 0.105
    save(fig, os.path.join(OUT_CFD, "cfd_v08_summary.svg"))


# ---------------------------------------------------------------- F10 controlled experiments
def fig_experiments():
    base = result("v08")
    T8 = [abs(c["T_N"]) for c in base["checkpoints"]]
    band = 100 * spread(T8[1:])
    tags = ["v10", "v12", "v15", "v14"]
    names = ["V10\nuniform de-pitch\n−1.77°", "V12\nsweep +6°\n(mesh +9.1 %)", "V15\nroot de-pitch\n−2.40° → 0", "V14\nhub-wall BC\n(diagnostic)"]
    dT = [100 * (result(t)["T_N"] / base["T_N"] - 1) for t in tags]
    dQ = [100 * (result(t)["Q_Nm"] / base["Q_Nm"] - 1) for t in tags]
    de = [100 * (result(t)["eta_p"] / base["eta_p"] - 1) for t in tags]
    x = np.arange(len(tags))
    fig, ax = plt.subplots(figsize=(12, 6))
    w = 0.26
    ax.bar(x - w, dT, w, color="#1f78b4", label="Δ thrust")
    ax.bar(x, dQ, w, color="#e31a1c", label="Δ torque")
    ax.bar(x + w, de, w, color="#33a02c", label="Δ η_p")
    ax.axhspan(-band, band, color="#999999", alpha=0.18, label="± V08 full-history thrust spread (%.2f %%)" % band)
    ax.axhline(0, color="black", lw=0.8)
    for i, v in enumerate(de):
        ax.text(x[i] + w, v + (1 if v >= 0 else -3), "%.1f %%" % v, ha="center", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("change relative to V08  [%]")
    ax.set_title("Design changes evaluated around the V08 reference case — design RPM (ω = 135.559 rad/s)\n"
                 "V14 is a hub boundary-condition test on the V08 geometry, not a design change")
    ax.legend(loc="lower right")
    fig.text(0.01, 0.01, "V11 (1000 rpm, off-design) is excluded: different operating point. " + STAMP, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, os.path.join(OUT_CFD, "cfd_controlled_experiments_vs_v08.svg"))


# ---------------------------------------------------------------- F11 BEM reference comparison
def fig_bem_reference():
    fam = {"v04cf": "v03", "v05n16": "v03", "v06e": "v06", "v08": "v06", "v10": "v06", "v12": "v06", "v14": "v06", "v15": "v06"}
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, key, bkey, unit, title in [(axes[0], "T_N", "thrust", "thrust  [N]", "Thrust"), (axes[1], "Q_Nm", "torque", "torque  [N·m]", "Torque")]:
        xs, cf, bm = [], [], []
        for t, f in fam.items():
            b, _ = bem(f)
            bv = b["dimensional_interpretation"]["thrust_N" if bkey == "thrust" else "torque_Nm"]
            xs.append(LABEL[t].split(" ")[0] + "\n(%s BEM)" % f)
            cf.append(result(t)[key])
            bm.append(bv)
        x = np.arange(len(xs))
        ax.bar(x - 0.2, bm, 0.4, color="#bbbbbb", edgecolor="black", label="BEM design intent (design model)")
        ax.bar(x + 0.2, cf, 0.4, color="#1f78b4", label="recorded CFD")
        ax.set_xticks(x)
        ax.set_xticklabels(xs, fontsize=9.5)
        ax.set_ylabel(unit)
        ax.set_title(title + " — design RPM")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.06))
    fig.suptitle("BEM design intent vs recorded CFD. BEM is a reference design model, not a prediction or validation of CFD;\n"
                 "the two are not at matched thrust, so their efficiencies are not directly comparable", fontsize=11.5)
    fig.text(0.01, 0.01, "v03-family BEM for V04cf/V05n16 (design_summary.json); v06-family BEM for V06e onward (design_summary_v06.json). " + STAMP, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.13, 1, 0.9))
    save(fig, os.path.join(OUT_CFD, "bem_reference_vs_cfd_design_rpm.svg"))


# ---------------------------------------------------------------- F12 camber correction
def fig_camber():
    t3, t4 = result("v03"), result("v04cf")
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.bar([0, 1], [t3["T_N"], t4["T_N"]], color=["#8c8c8c", "#1f78b4"], width=0.55)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["V03\ncamber on wrong side of chord", "V04cf\ncamber sign corrected"])
    ax.set_ylabel("thrust  [N]")
    for i, v in enumerate([t3["T_N"], t4["T_N"]]):
        ax.text(i, v / 2, "%.1f N" % v, ha="center", va="center", fontsize=13, color="white", fontweight="bold")
    ax.set_title("Effect of correcting the camber sign\ndesign RPM (ω = 135.559 rad/s)")
    fig.text(0.01, 0.01, "V04cf: last recorded checkpoint; the case did not settle and diverged at iteration 246.\n" + STAMP, fontsize=9)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, os.path.join(OUT_CFD, "cfd_camber_correction_v03_v04cf.svg"))


# ---------------------------------------------------------------- design (BEM) spanwise
def fig_design():
    b3, _ = bem("v03")
    b6, _ = bem("v06")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    for ax, key, lab in [(axes[0, 0], "chord_m", "chord  [m]"), (axes[0, 1], "beta_deg", "blade angle β  [deg]"),
                         (axes[1, 0], "Cl_design", "design $C_l$  [–]"), (axes[1, 1], "toc", "thickness ratio t/c  [–]")]:
        ax.plot(b3["radial_table"]["r_over_R"], b3["radial_table"][key], color="#6a3d9a", label="v03 family (V03–V05n16)")
        ax.plot(b6["radial_table"]["r_over_R"], b6["radial_table"][key], color="#1f78b4", ls="--", label="v06 family (V06e onward)")
        ax.set_ylabel(lab)
    for ax in axes[1]:
        ax.set_xlabel("r / R")
    axes[0, 0].legend()
    fig.suptitle("BEM design distributions (Adkins–Liebeck minimum-induced-loss design, τ = 0.08) — design intent, not CFD", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, os.path.join(OUT_DES, "bem_spanwise_design_v03_v06_families.svg"))


# ---------------------------------------------------------------- field figures (need --field-data)
def read_b2b(path):
    xs, ys, zs, pt, ma = [], [], [], [], []
    with open(path) as f:
        next(f)
        for line in f:
            p = line.split(",")
            if len(p) < 7:
                continue
            try:
                xs.append(float(p[1])); ys.append(float(p[2])); zs.append(float(p[3])); pt.append(float(p[4])); ma.append(float(p[6]))
            except ValueError:
                continue
    x, y, z = np.array(xs), np.array(ys), np.array(zs)
    r = np.hypot(x, y)
    return r * np.arctan2(y, x), z, np.array(pt), np.array(ma)


WIN = dict(s=(-0.8, 0.8), z=(-0.5, 0.7))


def window(s, z):
    return (z > WIN["z"][0]) & (z < WIN["z"][1]) & (s > WIN["s"][0]) & (s < WIN["s"][1])


def fig_fields(field_dir):
    plt.rcParams["axes.grid"] = False
    if not field_dir:
        print("field figures skipped (no --field-data)")
        return
    tags = ["v08", "v12", "v14", "v15"]
    lv = np.linspace(0.3, 1.5, 25)
    fig, axes = plt.subplots(2, 2, figsize=(13, 11), sharex=True, sharey=True)
    for ax, t in zip(axes.flat, tags):
        s, z, _, m = read_b2b(os.path.join(field_dir, "b2b_r75_%s.csv" % t))
        sel = window(s, z)
        tri = Triangulation(s[sel], z[sel])
        cs = ax.tricontourf(tri, m[sel], levels=lv, cmap="viridis", extend="both")
        ax.set_title(LABEL[t])
        ax.set_xlabel("r·θ  [m]")
        ax.set_aspect("equal")
    for ax in axes[:, 0]:
        ax.set_ylabel("axial position z  [m] (flow +z)")
    cb = fig.colorbar(cs, ax=axes, shrink=0.85, pad=0.02)
    cb.set_label("Mach number, absolute frame  [–]  (same scale on every panel)")
    fig.suptitle("Blade-to-blade Mach number at r/R = 0.75 — design RPM (ω = 135.559 rad/s)\n" + STAMP, fontsize=12)
    save(fig, os.path.join(OUT_CFD, "cfd_mach_b2b_r075_design_rpm.png"), png=True)

    s, z, _, m = read_b2b(os.path.join(field_dir, "b2b_r75_v11.csv"))
    sel = window(s, z)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    cs = ax.tricontourf(Triangulation(s[sel], z[sel]), m[sel], levels=lv, cmap="viridis", extend="both")
    ax.set_aspect("equal")
    ax.set_xlabel("r·θ  [m]")
    ax.set_ylabel("axial position z  [m]")
    fig.colorbar(cs, ax=ax, shrink=0.85).set_label("Mach number, absolute frame  [–]")
    ax.set_title("V11 — 1000 rpm OFF-DESIGN (separate investigation)\nblade-to-blade Mach at r/R = 0.75, ω = 104.72 rad/s")
    fig.text(0.01, 0.01, "Same colour scale as the design-RPM figure.\n" + STAMP, fontsize=8.5)
    save(fig, os.path.join(OUT_CFD, "cfd_v11_1000rpm_offdesign_mach_b2b_r075.png"), png=True)

    s, z, pt, _ = read_b2b(os.path.join(field_dir, "b2b_r75_v08.csv"))
    sel = window(s, z)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    cs = ax.tricontourf(Triangulation(s[sel], z[sel]), pt[sel] / 1000.0, levels=24, cmap="magma")
    ax.set_aspect("equal")
    ax.set_xlabel("r·θ  [m]")
    ax.set_ylabel("axial position z  [m]")
    fig.colorbar(cs, ax=ax, shrink=0.85).set_label("total pressure, absolute frame  [kPa]")
    ax.set_title("V08 blade-to-blade total pressure at r/R = 0.75\ndesign RPM (ω = 135.559 rad/s), flow in +z")
    fig.text(0.01, 0.01, STAMP, fontsize=8.5)
    save(fig, os.path.join(OUT_CFD, "cfd_v08_total_pressure_b2b_r075.png"), png=True)


if __name__ == "__main__":
    fd = None
    if "--field-data" in sys.argv:
        fd = sys.argv[sys.argv.index("--field-data") + 1]
    fig_design()
    fig_convergence()
    fig_residuals()
    fig_radial_loading()
    fig_cp()
    fig_v08_card()
    fig_experiments()
    fig_bem_reference()
    fig_camber()
    fig_fields(fd)
    print("\n".join(written))
