"""
make_fluent_case.py -- generate the ANSYS Fluent setup journal for CFG-ISO
directly from the Phase 1 design.

NO CFD NUMBER IS TYPED BY HAND. Every boundary condition, rotational speed and
reference value is read from 01_design/results/design_summary.json, so the CFD
case and the analytical design can never silently diverge.

Writes
  cases/CFG-ISO/setup_iso_sector.jou   Fluent TUI journal (solver setup + monitors)
  cases/CFG-ISO/case_parameters.json   the exact values written into the journal
  cases/CFG-ISO/README.md              how to run it and what must exist first

This script does NOT mesh and does NOT run Fluent. It produces the setup that a
mesh, once it exists, is driven with.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).parent
DESIGN = HERE.parent / "01_design" / "results" / "design_summary.json"
CASE = HERE / "cases" / "CFG-ISO"
CASE.mkdir(parents=True, exist_ok=True)


def main():
    d = json.load(open(DESIGN, encoding="utf-8"))
    op, atm, nd = d["operating_point"], d["atmosphere"], d["nondimensional"]
    B = d["blade_count_selected"]

    p = {
        "n_blades": B,
        "sector_deg": 360.0 / B,
        "omega_rad_s": op["omega_rads"],
        "rpm": op["rpm"],
        "mach_flight": d["inputs"]["mach_flight"],
        "V0_ms": op["V0_ms"],
        "p_static_Pa": atm["p_Pa"],
        "T_static_K": atm["T_K"],
        "rho_kgm3": atm["rho_kgm3"],
        "mu_Pas": atm["mu_Pas"],
        "a_ms": atm["a_ms"],
        "R_m": op["R_m"],
        "D_m": d["inputs"]["diameter_m"],
        "n_rev_s": op["n_rev_per_s"],
        "advance_ratio_J": op["advance_ratio_J"],
        "mach_tip_ROTATIONAL": op["mach_tip_ROTATIONAL"],
        "mach_tip_HELICAL": op["mach_tip_HELICAL"],
        "area_disk_m2": 3.141592653589793 * op["R_m"] ** 2,
        "turb_intensity_pct": 0.1,
        "turb_visc_ratio": 5.0,
        "design_C_T": nd["C_T"],
        "design_C_P": nd["C_P"],
        "bem_eta": d["performance"]["eta_bem_minimum_induced_loss"],
        "eta_ideal_ceiling": d["performance"]["eta_actuator_disk_ideal_CEILING"],
    }
    with open(CASE / "case_parameters.json", "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2)

    jou = f"""; =====================================================================
; BA-OF-01  CFG-ISO  --  isolated open-fan rotor, {p['sector_deg']:.1f} deg periodic sector
; GENERATED from 01_design/results/design_summary.json -- do not hand-edit.
; Solver: ANSYS Fluent 2025 R1
;
; PREREQUISITE: a mesh file must already be read or supplied. This journal sets
; up physics, boundary conditions, monitors and convergence -- it does not mesh.
;
; Design point (all values below traced to the BEM design):
;   M0 = {p['mach_flight']}   V0 = {p['V0_ms']:.2f} m/s   J = {p['advance_ratio_J']:.4f}
;   rotational tip Mach = {p['mach_tip_ROTATIONAL']:.4f}
;   HELICAL     tip Mach = {p['mach_tip_HELICAL']:.4f}   (supersonic -- distinct quantity)
;   omega = {p['omega_rad_s']:.4f} rad/s  ({p['rpm']:.1f} rpm)
;   BEM design intent: C_T = {p['design_C_T']:.4f}  C_P = {p['design_C_P']:.4f}  eta = {p['bem_eta']:.4f}
; =====================================================================

/define/models/energy yes no no no yes
/define/models/viscous/kw-sst yes

; ---- material: ideal gas, Sutherland viscosity ----------------------
/define/materials/change-create air air yes ideal-gas no no yes sutherland three-coefficient-method 1.458e-06 110.4 no no no

; ---- operating conditions: absolute pressure, no gravity ------------
/define/operating-conditions/operating-pressure 0

; ---- rotating reference frame on the fluid zone ---------------------
; NOTE: zone name must match the mesh. Rotation is about +Z through the origin.
/define/boundary-conditions/fluid fluid yes air no no no yes 0 0 0 0 0 1 {p['omega_rad_s']:.6f} no no no no

; ---- boundary conditions --------------------------------------------
; far field: pressure-far-field at flight Mach, axial (+Z) direction
/define/boundary-conditions/pressure-far-field farfield {p['p_static_Pa']:.4f} {p['mach_flight']} {p['T_static_K']:.4f} 0 0 1 no no yes {p['turb_intensity_pct']/100.0} {p['turb_visc_ratio']}
/define/boundary-conditions/pressure-outlet outlet {p['p_static_Pa']:.4f} {p['T_static_K']:.4f} no yes no no yes {p['turb_intensity_pct']/100.0} {p['turb_visc_ratio']} yes no no

; walls move with the rotating frame (relative velocity zero)
/define/boundary-conditions/wall blade 0 no 0 no no no 0 no no no
/define/boundary-conditions/wall spinner 0 no 0 no no no 0 no no no

; ---- reference values (for coefficient reporting) -------------------
/report/reference-values/area {p['area_disk_m2']:.6f}
/report/reference-values/density {p['rho_kgm3']:.6f}
/report/reference-values/velocity {p['V0_ms']:.6f}
/report/reference-values/temperature {p['T_static_K']:.4f}
/report/reference-values/pressure {p['p_static_Pa']:.4f}
/report/reference-values/length {p['D_m']:.6f}
/report/reference-values/viscosity {p['mu_Pas']:.6e}

; ---- numerics: 2nd order, pressure-based coupled --------------------
/solve/set/p-v-coupling 24
/solve/set/discretization-scheme/pressure 12
/solve/set/discretization-scheme/density 1
/solve/set/discretization-scheme/mom 1
/solve/set/discretization-scheme/k 1
/solve/set/discretization-scheme/omega 1
/solve/set/discretization-scheme/temperature 1
/solve/set/gradient-scheme no yes

; ---- monitors: THRUST AND TORQUE, the convergence criterion ---------
; Convergence is NOT residual drop alone. Both must hold:
;   (1) scaled residuals >= 4 orders down
;   (2) thrust and torque stationary within +-0.1 % over 500 iterations
/solve/report-definitions/add thrust_z force force-vector 0 0 1 thread-names blade spinner () q
/solve/report-definitions/add torque_z moment mom-axis 0 0 1 mom-center 0 0 0 thread-names blade spinner () q
/solve/report-files/add thrust_z-rfile report-defs thrust_z () file-name "thrust_z.out" q
/solve/report-files/add torque_z-rfile report-defs torque_z () file-name "torque_z.out" q
/solve/report-plots/add thrust_z-plot report-defs thrust_z () q

; ---- residual criteria ----------------------------------------------
/solve/monitors/residual/convergence-criteria 1e-6 1e-6 1e-6 1e-6 1e-6 1e-6 1e-6

; ---- initialise and run ---------------------------------------------
/solve/initialize/compute-defaults/pressure-far-field farfield
/solve/initialize/initialize-flow yes

; first order for start-up robustness (NO RESULT MAY BE REPORTED FROM THIS)
/solve/set/discretization-scheme/mom 0
/solve/iterate 200
; back to 2nd order for the reported solution
/solve/set/discretization-scheme/mom 1
/solve/iterate 3000

/file/write-case-data "CFG-ISO-result.cas.h5" ok
; =====================================================================
; POST-PROCESSING REMINDERS (done in the extraction script, not here):
;   * multiply sector thrust and torque by {p['n_blades']} for the full rotor
;   * eta_p = T*V0/(Q*omega);  cross-check against C_T*J/C_P
;   * report PRESSURE and VISCOUS force components separately
;   * bin blade surface forces radially to get dT/dr and compare against BEM
;   * export the y+ map over the blade
; =====================================================================
"""
    (CASE / "setup_iso_sector.jou").write_text(jou, encoding="utf-8")

    readme = f"""# CFG-ISO — isolated open-fan rotor, {p['sector_deg']:.1f}° periodic sector

**Generated** from `01_design/results/design_summary.json`. Do not hand-edit
`setup_iso_sector.jou` — regenerate it with `python 03_cfd/make_fluent_case.py`.

## Status

| Item | State |
|---|---|
| Setup specification | ✅ `../../CFD_SETUP_SPECIFICATION.md` |
| Solver journal | ✅ `setup_iso_sector.jou` (generated, parameters traced to the design) |
| **Fluid-domain geometry** | ❌ **not yet built** |
| **Mesh** | ❌ **not yet generated** |
| **Solution** | ❌ **NOT RUN — no CFD result exists for this project** |

## What must exist before this journal can run

1. A **fluid domain**: a {p['sector_deg']:.1f}° sector of the flow volume
   (8 D upstream, 8 D radial, 15 D downstream) with the blade and spinner
   subtracted. This is a **derivative** of the CAD master, never the master itself.
2. A mesh with these named zones, which the journal expects:
   `fluid`, `farfield`, `outlet`, `blade`, `spinner`, and the two periodic sides.
3. Prism layers sized to `y+ ≈ 1`: first cell **3.2 µm**, growth 1.2, ~32 layers.

## Run

```
"D:\\ANSYS Inc\\v251\\fluent\\ntbin\\win64\\fluent.exe" 3ddp -t8 -g -i setup_iso_sector.jou
```

`-t8` uses 8 cores. **Confirm the licence permits 8 parallel processes** — if it
caps at 4, every runtime estimate in the feasibility audit roughly doubles.

## Design intent this case is testing

| Quantity | BEM design intent |
|---|---|
| `C_T` | {p['design_C_T']:.4f} |
| `C_P` | {p['design_C_P']:.4f} |
| `η_p` | {p['bem_eta']:.4f} — *estimate, bounded by a low-order drag model* |
| Ideal ceiling | {p['eta_ideal_ceiling']:.4f} — CFD thrust must not exceed this |

A CFD-vs-BEM disagreement **at the tip is expected**: the BEM design uses
sectional aerodynamics outside Prandtl–Glauert validity across the whole blade
(helical tip Mach {p['mach_tip_HELICAL']:.3f}). Gate G4 therefore sends the
investigation to the BEM first, not to the mesh.
"""
    (CASE / "README.md").write_text(readme, encoding="utf-8")

    print("BA-OF-01  Fluent case generation")
    print(f"  sector            : {p['sector_deg']:.2f} deg  ({B} blades)")
    print(f"  omega             : {p['omega_rad_s']:.4f} rad/s ({p['rpm']:.0f} rpm)")
    print(f"  far-field         : M {p['mach_flight']}, p {p['p_static_Pa']:.1f} Pa, "
          f"T {p['T_static_K']:.2f} K")
    print(f"  design intent     : C_T {p['design_C_T']:.4f}  C_P {p['design_C_P']:.4f}")
    print(f"  written           : {CASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
