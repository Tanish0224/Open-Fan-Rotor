"""
run_phase1_design.py -- BA-OF-01 Phase 1 driver.

Reproducible entry point. Produces every Phase 1 artifact:
    results/blade_count_trade.csv     blade count selected as an OUTPUT, not assumed
    results/design_table.csv          the radial definition -- SINGLE SOURCE OF TRUTH
    results/design_summary.json       full labelled record incl. gate G0 verification
    results/sections/*.dat            exact NACA 4-digit section coordinates for CAD
    results/figures/*.png             design documentation plots

Run:  python run_phase1_design.py
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import asdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from openfan_design import (DesignSpec, OpenFanRotorDesign, naca4_section,
                            station_independence_check)

HERE = pathlib.Path(__file__).parent
RES = HERE / "results"
FIG = RES / "figures"
SEC = RES / "sections"
for d in (RES, FIG, SEC):
    d.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"figure.dpi": 140, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.axisbelow": True})
C1, C2, C3 = "#1f4e79", "#c0504d", "#4f8a3d"


def jsonable(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, dict):
        return {k: jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return o


# =====================================================================================
# STEP 1 -- BLADE COUNT TRADE STUDY  (closes open item O2: B must be an OUTPUT)
# =====================================================================================
def blade_count_trade(base: DesignSpec):
    """
    Blade count is selected on geometric and aerodynamic criteria, not assumed.

    IMPORTANT STRUCTURAL NOTE, established by inspection of the formulation:
      * Local solidity sigma = B*c/(2*pi*r) is very nearly INDEPENDENT of blade count,
        because Adkins-Liebeck chord scales as 1/B at fixed loading. Solidity is set by
        the loading tau, the speed ratio lambda and the design Cl -- NOT by B. It is
        therefore retained as a feasibility bound on the DESIGN, but it cannot
        discriminate between blade counts.
      * Chord goes to ZERO at the tip by construction (Prandtl F -> 0 there). A
        "tip chord" acceptance test can never pass and would be a meaningless
        criterion. Chord at 0.90R is used instead; the physical tip is truncated in CAD.

    Selection criteria [DESIGN DECISION]:
      C-a  chord/diameter at 0.75R within [0.06, 0.16]  -- propeller planform norm
      C-b  blade aspect ratio (span / chord@0.75R) within [4, 14]
      C-c  max local solidity <= 0.80                   -- feasibility bound on the design
      C-d  chord at 0.90R >= 0.02 R                     -- non-degenerate outboard blade
    Tie-break: choose the SMALLEST blade count whose efficiency is within 0.5 % of the
    best selectable candidate. Efficiency rises monotonically but with strongly
    diminishing returns, and each extra blade costs weight, cost and complexity.
    """
    rows = []
    for B in (8, 10, 12, 14, 16, 18, 20):
        spec = DesignSpec(**{**asdict(base), "n_blades": B})
        try:
            d = OpenFanRotorDesign(spec).solve()
        except RuntimeError as e:
            rows.append({"n_blades": B, "feasible": False, "note": str(e)[:60]})
            continue
        c75 = float(np.interp(0.75, d.xi, d.st["chord"]))
        c90_R = float(np.interp(0.90, d.xi, d.st["chord"]) / d.R)
        max_sol = float(np.max(d.solidity))
        ar = float((d.R - d.R_hub) / c75)
        rows.append({
            "n_blades": B, "feasible": True,
            "eta_bem": float(d.eta_bem),
            "max_solidity": max_sol,
            "chord_75R_m": c75,
            "chord_over_D_at_75R": c75 / spec.diameter_m,
            "chord_90R_over_R": c90_R,
            "blade_aspect_ratio": ar,
            "pass_chord_over_D": bool(0.06 <= c75 / spec.diameter_m <= 0.16),
            "pass_aspect_ratio": bool(4.0 <= ar <= 14.0),
            "pass_solidity": bool(max_sol <= 0.80),
            "pass_chord_90R": bool(c90_R >= 0.02),
        })
    for r in rows:
        if r.get("feasible"):
            r["SELECTABLE"] = bool(r["pass_chord_over_D"] and r["pass_aspect_ratio"]
                                   and r["pass_solidity"] and r["pass_chord_90R"])
    ok = [r for r in rows if r.get("SELECTABLE")]
    if not ok:
        return rows, None
    best_eta = max(r["eta_bem"] for r in ok)
    near = [r for r in ok if (best_eta - r["eta_bem"]) / best_eta <= 0.005]
    chosen = min(near, key=lambda r: r["n_blades"])["n_blades"]
    return rows, chosen


# =====================================================================================
# PLOTS
# =====================================================================================
def make_figures(d: OpenFanRotorDesign, tbl: dict):
    xi = tbl["r_over_R"]

    # --- Fig 1: planform + twist ------------------------------------------------
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
    ax[0].plot(xi, tbl["chord_m"], color=C1, lw=2)
    ax[0].set_xlabel("r/R"); ax[0].set_ylabel("chord [m]"); ax[0].set_title("Chord distribution")
    ax[1].plot(xi, tbl["beta_deg"], color=C1, lw=2, label=r"blade angle $\beta$")
    ax[1].plot(xi, tbl["phi_deg"], color=C2, lw=1.5, ls="--", label=r"flow angle $\phi$")
    ax[1].set_xlabel("r/R"); ax[1].set_ylabel("angle [deg]")
    ax[1].set_title("Twist"); ax[1].legend(fontsize=7)
    ax[2].plot(xi, tbl["toc"] * 100, color=C1, lw=2)
    ax[2].set_xlabel("r/R"); ax[2].set_ylabel("t/c [%]"); ax[2].set_title("Thickness ratio")
    fig.suptitle("BA-OF-01 open-fan rotor — radial geometry (BEM design output)", y=1.03)
    fig.tight_layout(); fig.savefig(FIG / "fig1_geometry.png", bbox_inches="tight"); plt.close(fig)

    # --- Fig 2: THE Mach figure -- the design constraint -------------------------
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(xi, tbl["M_helical"], color=C2, lw=2.2, label=r"$M_{hel}$  (helical, kinematic)")
    ax.plot(xi, tbl["M_rel"], color=C1, lw=1.6, ls="--", label=r"$M_{rel}$  (relative, with induction)")
    ax.plot(xi, tbl["M_normal"], color=C3, lw=2.2, label=r"$M_n = M_{hel}\cos\Lambda$  (after sweep)")
    ax.axhline(1.0, color="k", lw=0.9, ls=":")
    ax.text(0.30, 1.012, "sonic", fontsize=7.5)
    ax.axhline(d.spec.mn_limit, color=C3, lw=0.9, ls=":")
    ax.text(0.30, d.spec.mn_limit + 0.012, r"$M_n$ design cap", fontsize=7.5, color=C3)
    ax.axhline(0.70, color="grey", lw=0.9, ls="-.")
    ax.text(0.30, 0.712, "Prandtl–Glauert validity limit", fontsize=7.5, color="grey")
    ax.set_xlabel("r/R"); ax.set_ylabel("Mach number")
    ax.set_title("Why this blade is swept:\nsweep holds the leading-edge-normal Mach below the cap")
    ax.legend(fontsize=7.5, loc="upper left"); ax.set_ylim(0.4, 1.2)
    fig.tight_layout(); fig.savefig(FIG / "fig2_mach_and_sweep.png", bbox_inches="tight"); plt.close(fig)

    # --- Fig 3: sweep law --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(xi, tbl["sweep_deg"], color=C1, lw=2.2)
    ax.axhline(45.0, color=C2, lw=1.0, ls="--")
    ax.text(0.30, 46.0, "NASA SR-3 tip sweep = 45° (published, M0.8 propfan)",
            fontsize=7, color=C2)
    ax.set_xlabel("r/R"); ax.set_ylabel(r"sweep $\Lambda$ [deg]")
    ax.set_title("Sweep distribution derived from the helical-Mach field")
    fig.tight_layout(); fig.savefig(FIG / "fig3_sweep.png", bbox_inches="tight"); plt.close(fig)

    # --- Fig 4: loading ----------------------------------------------------------
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
    ax[0].plot(xi, tbl["dT_dr_Npm"] / 1000.0, color=C1, lw=2)
    ax[0].set_xlabel("r/R"); ax[0].set_ylabel("dT/dr [kN/m]"); ax[0].set_title("Radial thrust loading")
    ax[1].plot(xi, tbl["dQ_dr_Nmpm"] / 1000.0, color=C2, lw=2)
    ax[1].set_xlabel("r/R"); ax[1].set_ylabel("dQ/dr [kN·m/m]"); ax[1].set_title("Radial torque loading")
    ax[2].plot(xi, tbl["F_prandtl"], color=C3, lw=2)
    ax[2].set_xlabel("r/R"); ax[2].set_ylabel("F"); ax[2].set_title("Prandtl tip/hub loss factor")
    fig.suptitle("BA-OF-01 — radial load distribution", y=1.03)
    fig.tight_layout(); fig.savefig(FIG / "fig4_loading.png", bbox_inches="tight"); plt.close(fig)

    # --- Fig 5: velocity triangles ----------------------------------------------
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    for ax_, target in zip(axs, (0.35, 0.70, 0.98)):
        i = int(np.argmin(np.abs(xi - target)))
        Va = d.V0 * (1.0 + d.st["a_ax"][i])
        Vt = d.omega * d.r[i] * (1.0 - d.st["a_tan"][i])
        ax_.arrow(0, 0, Vt, 0, color=C2, width=1.2, length_includes_head=True,
                  head_width=6, head_length=9)
        ax_.arrow(Vt, 0, 0, Va, color=C3, width=1.2, length_includes_head=True,
                  head_width=6, head_length=9)
        ax_.arrow(0, 0, Vt, Va, color=C1, width=1.2, length_includes_head=True,
                  head_width=6, head_length=9)
        ax_.text(Vt * 0.5, -18, r"$\Omega r(1-a')$", color=C2, fontsize=8, ha="center")
        ax_.text(Vt + 8, Va * 0.5, r"$V_0(1+a)$", color=C3, fontsize=8)
        ax_.text(Vt * 0.42, Va * 0.62, "W", color=C1, fontsize=9, fontweight="bold")
        ax_.set_title(f"r/R = {xi[i]:.2f}\n"
                      rf"$\phi$={tbl['phi_deg'][i]:.1f}°  $\beta$={tbl['beta_deg'][i]:.1f}°  "
                      rf"$M_{{rel}}$={tbl['M_rel'][i]:.2f}", fontsize=8)
        ax_.set_xlim(-30, max(Vt * 1.25, 60)); ax_.set_ylim(-40, Va * 1.9)
        ax_.set_aspect("equal"); ax_.set_xlabel("tangential [m/s]"); ax_.set_ylabel("axial [m/s]")
    fig.suptitle("Velocity triangles at the design point (rotor frame)", y=1.04)
    fig.tight_layout(); fig.savefig(FIG / "fig5_velocity_triangles.png", bbox_inches="tight"); plt.close(fig)

    # --- Fig 6: stacked sections -------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for target in (0.30, 0.50, 0.70, 0.85, 1.00):
        i = int(np.argmin(np.abs(xi - target)))
        pts = naca4_section(float(tbl["camber_m"][i]), float(tbl["camber_p"][i]),
                            float(tbl["toc"][i]))
        c = float(tbl["chord_m"][i])
        b = np.radians(float(tbl["beta_deg"][i]))
        x, y = pts[:, 0] * c, pts[:, 1] * c
        xr = x * np.cos(-b) - y * np.sin(-b)
        yr = x * np.sin(-b) + y * np.cos(-b)
        ax.plot(xr, yr + target * 1.1, lw=1.1,
                label=f"r/R={xi[i]:.2f}, t/c={tbl['toc'][i]*100:.1f}%")
    ax.set_aspect("equal"); ax.legend(fontsize=6.5, ncol=2)
    ax.set_xlabel("[m]"); ax.set_ylabel("stacked (offset for clarity)")
    ax.set_title("NACA 4-digit sections at design chord, thickness, camber and stagger")
    fig.tight_layout(); fig.savefig(FIG / "fig6_sections.png", bbox_inches="tight"); plt.close(fig)

    # --- Fig 7: Reynolds + solidity ---------------------------------------------
    fig, ax = plt.subplots(1, 2, figsize=(8.2, 3.2))
    ax[0].semilogy(xi, tbl["Re_chord"], color=C1, lw=2)
    ax[0].set_xlabel("r/R"); ax[0].set_ylabel("Re (chord)"); ax[0].set_title("Chord Reynolds number")
    ax[1].plot(xi, tbl["solidity"], color=C2, lw=2)
    ax[1].axhline(0.40, color="grey", ls="--", lw=1.0)
    ax[1].text(0.30, 0.408, "selection cap 0.40", fontsize=7, color="grey")
    ax[1].set_xlabel("r/R"); ax[1].set_ylabel(r"$\sigma = Bc/2\pi r$"); ax[1].set_title("Local solidity")
    fig.tight_layout(); fig.savefig(FIG / "fig7_re_solidity.png", bbox_inches="tight"); plt.close(fig)


# =====================================================================================
# MAIN
# =====================================================================================
def main():
    print("=" * 78)
    print("BA-OF-01  PHASE 1  --  first-principles open-fan rotor design")
    print("=" * 78)

    base = DesignSpec()

    # ---- STEP 1: blade count as an OUTPUT ------------------------------------
    print("\n[1] Blade-count trade study (open item O2)")
    trade, chosen = blade_count_trade(base)
    hdr = (f"{'B':>3} {'eta':>7} {'max sigma':>10} {'c@.75R':>8} {'c/D':>7} "
           f"{'c@.9R/R':>8} {'AR':>6} {'select':>7}")
    print("    " + hdr)
    for r in trade:
        if not r.get("feasible"):
            print(f"    {r['n_blades']:>3}  INFEASIBLE: {r.get('note','')}")
            continue
        print(f"    {r['n_blades']:>3} {r['eta_bem']:>7.4f} {r['max_solidity']:>10.3f} "
              f"{r['chord_75R_m']:>8.3f} {r['chord_over_D_at_75R']:>7.3f} "
              f"{r['chord_90R_over_R']:>8.3f} "
              f"{r['blade_aspect_ratio']:>6.2f} {str(r['SELECTABLE']):>7}")
    if chosen is None:
        raise SystemExit("STOP: no blade count satisfies the selection criteria.")
    print(f"    -> SELECTED B = {chosen}  (smallest within 0.5% of best selectable eta)")

    with open(RES / "blade_count_trade.csv", "w", encoding="utf-8") as f:
        keys = ["n_blades", "feasible", "eta_bem", "max_solidity", "chord_75R_m",
                "chord_over_D_at_75R", "chord_90R_over_R", "blade_aspect_ratio",
                "pass_chord_over_D", "pass_aspect_ratio", "pass_solidity",
                "pass_chord_90R", "SELECTABLE"]
        f.write(",".join(keys) + "\n")
        for r in trade:
            f.write(",".join(str(r.get(k, "")) for k in keys) + "\n")

    # ---- STEP 2: the design ---------------------------------------------------
    spec = DesignSpec(**{**asdict(base), "n_blades": chosen})
    d = OpenFanRotorDesign(spec).solve()
    tbl = d.radial_table()
    summ = d.summary()

    op = summ["operating_point"]
    print(f"\n[2] Design point")
    print(f"    M0 = {spec.mach_flight}   alt = {spec.altitude_m:.0f} m   "
          f"V0 = {op['V0_ms']:.1f} m/s")
    print(f"    D  = {spec.diameter_m} m   N = {op['rpm']:.0f} rpm   J = {op['advance_ratio_J']:.3f}")
    print(f"    M_tip ROTATIONAL = {op['mach_tip_ROTATIONAL']:.4f}")
    print(f"    M_tip HELICAL    = {op['mach_tip_HELICAL']:.4f}   <-- distinct quantity")
    print(f"    tau = {spec.tau}  ->  Tc = {d.Tc:.4f}   C_T = {d.C_T:.4f}   C_P = {d.C_P:.4f}")
    print(f"    eta ideal ceiling = {d.eta_ideal:.4f}")
    print(f"    eta BEM (min induced loss, est. Cd) = {d.eta_bem:.4f}")
    print(f"    dimensional interpretation: T = {d.thrust_N/1000:.2f} kN, "
          f"P = {d.power_W/1e6:.3f} MW  [OUTPUT, not a requirement]")
    print(f"    sweep at tip = {np.degrees(d.sweep_rad[-1]):.1f} deg")
    print(f"    stations outside PG validity: "
          f"{summ['validity_flags']['stations_outside_PG_validity']} / {len(d.xi)}")

    # ---- STEP 3: gate G0 ------------------------------------------------------
    print("\n[3] GATE G0 -- verification")
    checks = d.verify()
    for k, v in checks.items():
        if k == "ALL_PASS":
            continue
        val = v["value"]
        vs = f"{val:.5g}" if isinstance(val, (int, float)) else str(val)
        print(f"    {'PASS' if v['pass'] else 'FAIL'}  {k:<32} = {vs:<12} ({v['what']})")

    indep = station_independence_check(spec)
    print(f"    {'PASS' if indep['pass'] else 'FAIL'}  station independence "
          f"({indep['n_base']}->{indep['n_refined']}): dT={indep['thrust_change_pct']:.4f}% "
          f"dQ={indep['torque_change_pct']:.4f}% deta={indep['eta_change_pct']:.4f}%")

    g0 = checks["ALL_PASS"] and indep["pass"]
    print(f"    ==> GATE G0: {'PASS' if g0 else 'FAIL'}")

    # ---- STEP 4: artifacts ----------------------------------------------------
    keys = list(tbl.keys())
    with open(RES / "design_table.csv", "w", encoding="utf-8") as f:
        f.write(",".join(keys) + "\n")
        for i in range(len(tbl["r_over_R"])):
            f.write(",".join(f"{float(tbl[k][i]):.8g}" for k in keys) + "\n")

    # exact section coordinates for CAD -- one file per station
    for i in range(len(tbl["r_over_R"])):
        pts = naca4_section(float(tbl["camber_m"][i]), float(tbl["camber_p"][i]),
                            float(tbl["toc"][i]))
        np.savetxt(SEC / f"station_{i:02d}_rR_{tbl['r_over_R'][i]:.4f}.dat", pts,
                   header=f"NACA 4-digit  m={tbl['camber_m'][i]:.6f} "
                          f"p={tbl['camber_p'][i]:.3f} t/c={tbl['toc'][i]:.6f}  "
                          f"unit chord, x y", comments="# ")

    summ["gate_G0"] = jsonable(checks)
    summ["station_independence"] = jsonable(indep)
    summ["blade_count_trade"] = jsonable(trade)
    summ["blade_count_selected"] = chosen
    summ["radial_table"] = jsonable(tbl)
    with open(RES / "design_summary.json", "w", encoding="utf-8") as f:
        json.dump(jsonable(summ), f, indent=2)

    make_figures(d, tbl)

    print(f"\n[4] Artifacts written to {RES}")
    print(f"    design_table.csv        ({len(tbl['r_over_R'])} stations x {len(keys)} columns)")
    print(f"    design_summary.json")
    print(f"    blade_count_trade.csv")
    print(f"    sections/               ({len(tbl['r_over_R'])} exact NACA coordinate files)")
    print(f"    figures/                (7 figures)")
    print("\nDONE." if g0 else "\nDONE -- WITH GATE G0 FAILURE, see above.")
    return 0 if g0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
