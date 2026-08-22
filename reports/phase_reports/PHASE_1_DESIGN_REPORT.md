# PHASE 1 — ANALYTICAL AERODYNAMIC DESIGN REPORT
### BA-OF-01 · Open-Fan Rotor

**Date:** 22 August 2026 · **Status:** **COMPLETE — GATE G0 PASS**
**Reproduce:** `python 01_design/run_phase1_design.py`

**Format:** requirement → decision → implementation → independent verification → claim.
**Evidence labels:** `[REQUIREMENT]` `[PUBLISHED INPUT]` `[DESIGN DECISION]` `[DERIVED]`
`[ASSUMPTION]` `[CFD-TBD]`

---

## 1. BLOCKING ITEMS CLOSED

### B1 — design thrust had no source → **CLOSED by removing it from the chain**

`[REQUIREMENT]` The Phase 1 authorisation directed that no aircraft-level thrust requirement be
invented, and that the rotor be defined by a prescribed non-dimensional loading instead.

**Decision (ED-009-R1):** the design input is

```
tau  =  T / (rho * A * V0^2)  =  0.08          [DESIGN DECISION]
```

This is a pure aerodynamic loading parameter. It sets the actuator-disk efficiency ceiling directly:

```
eta_ideal = 2 / (1 + sqrt(1 + 2*tau)) = 0.9629     [DERIVED]
```

**Consequence:** thrust in newtons is now an **output** of the design, obtained by dimensional
interpretation at the very end of the chain. The previously-flagged 20 kN placeholder has been
**deleted from the project**. The design chain is exactly as authorised:

```
cruise condition -> diameter -> rotational speed / tip-Mach constraint
   -> advance ratio -> non-dimensional loading -> C_T, C_P -> dimensional interpretation
```

**What tau = 0.08 is and is not.** It is a `[DESIGN DECISION]`, selected so the resulting planform is
propfan-representative (chord/diameter ≈ 0.07 at 0.75R). It is **not** an industry requirement and is
**not** traceable to any company document. It is owned by this project.

### B2 — airfoil polar data → **CLOSED without waiting on external data**

`[REQUIREMENT]` Select a publicly documented section family reconstructable **exactly**, and do not
depend on request-only polar data.

**Decision:** **NACA 4-digit series.** `[DESIGN DECISION]`
Its geometry is defined by published closed-form equations, so it is reconstructable to machine
precision with no external dataset. The trailing-edge coefficient −0.1036 is used so the section
closes exactly at `x/c = 1`.

**Sectional aerodynamics, by evidence class as required:**

| Quantity | How obtained | Class |
|---|---|---|
| Section coordinates | published closed-form NACA 4-digit equations | **published/known** |
| `Cl` at the ideal (shock-free entry) angle | thin-airfoil theory, `Cl_ideal = π·A₁`, integrated numerically | **analytical / low-order estimate** |
| Ideal incidence `α_ideal` | thin-airfoil theory | **analytical / low-order estimate** |
| Camber `m` to deliver the design `Cl` | solved analytically (`Cl_ideal` is linear in `m`) | **analytical** |
| `Cd` | flat-plate turbulent `Cf` × thickness form factor + a quadratic lift term | **project assumption — the weakest input** |
| Compressibility correction | Prandtl–Glauert, applied **only** where valid | **analytical, validity-bounded** |
| **Achieved sectional `Cl`, `Cd`, shock behaviour** | — | **`[CFD-TBD]` — ANSYS Fluent determines these** |

**Honest limitation, stated before use:** NACA 4-digit is **not** a high-critical-Mach propeller
family (NACA 16-series would be). Exact public reconstructability was traded for aerodynamic
optimality, deliberately. CFD will quantify the penalty. **No polar has been extrapolated into the
transonic regime and presented as validated.**

---

## 2. THE DESIGN CHAIN, STEP BY STEP

| Step | Quantity | Value | Class |
|---|---|---|---|
| 1 | Flight Mach `M₀` | 0.75 | `[DESIGN DECISION]` inside CFM's stated M0.75–0.85 |
| 1 | Altitude / ISA | 35 000 ft → `T` 218.8 K, `ρ` 0.3795 kg/m³, `a` 296.5 m/s | `[DERIVED]` |
| 1 | `V₀` | 222.4 m/s | `[DERIVED]` |
| 2 | Diameter `D` | 3.5 m | `[DESIGN DECISION]` from CFM "blade over 1.6 m" |
| 2 | Hub/tip | 0.28 | `[DESIGN DECISION]` |
| 3 | **Rotational** tip Mach | **0.800** | `[DESIGN DECISION]` classical propfan practice |
| 3 | `U_tip`, `ω`, `N` | 237.2 m/s, 135.5 rad/s, **1294 rpm** | `[DERIVED]` |
| 4 | Advance ratio `J` | **2.945** | `[DERIVED]` |
| 4 | **Helical** tip Mach | **1.0966 — supersonic** | `[DERIVED]` |
| 5 | Loading `τ` | 0.08 | `[DESIGN DECISION]` |
| 6 | `C_T`, `C_P` | 0.5450, 1.9886 | `[DERIVED]` |
| 6 | `η` ideal ceiling / BEM | 0.9629 / **0.8072** | `[DERIVED]` (BEM value is `[CFD-TBD]`-bounded) |
| 7 | Thrust, power | 14.45 kN, 3.98 MW | `[DERIVED]` — **interpretation, not requirement** |

> **Rotational vs helical tip Mach.** The rotational value (0.800) is the *constraint imposed*. The
> helical value (1.0966) is the *vector sum with flight Mach* and is what the tip sections actually
> experience. They are never interchanged in this project. Per the Phase 1 authorisation, the
> supersonic helical tip is treated as a **derived constraint requiring careful verification**, not
> as proof that the final rotor must run supersonic — if CFD shows an unmanageable tip shock, the
> response is more sweep first, and reduced tip speed only as a recorded trade.

---

## 3. QUANTITIES THE METHOD PRODUCED (not assumed)

### 3.1 Blade count = 16 — an output

`[REQUIREMENT]` Blade count must be an output of the solidity calculation, not an input.

**Structural finding, established by inspection of the formulation:** local solidity
`σ = Bc/(2πr)` is **very nearly independent of blade count**, because Adkins–Liebeck chord scales as
`1/B` at fixed loading. Solidity is set by `τ`, `λ` and design `Cl` — not by `B`. It is therefore a
feasibility bound on the *design*, and **cannot discriminate between blade counts**. A second
criterion was needed.

**A criterion that was structurally wrong and was removed:** a "tip chord ≥ 0.05 R" test can
**never** pass, because Adkins–Liebeck drives chord to zero at the tip by construction (Prandtl
`F → 0`). Chord at 0.90R is used instead.

| `B` | `η` | max `σ` | `c/D` at 0.75R | `c@0.9R/R` | AR | selectable |
|---|---|---|---|---|---|---|
| 8 | 0.7832 | 0.506 | 0.149 | 0.295 | 2.42 | ✗ AR |
| 10 | 0.7933 | 0.497 | 0.117 | 0.239 | 3.08 | ✗ AR |
| 12 | 0.7997 | 0.491 | 0.096 | 0.202 | 3.74 | ✗ AR |
| 14 | 0.8041 | 0.487 | 0.082 | 0.176 | 4.42 | ✓ |
| **16** | **0.8072** | **0.485** | **0.071** | **0.156** | **5.10** | **✓ SELECTED** |
| 18 | 0.8095 | 0.483 | 0.062 | 0.141 | 5.80 | ✓ |
| 20 | 0.8112 | 0.482 | 0.055 | 0.128 | 6.51 | ✗ `c/D` |

**Tie-break `[DESIGN DECISION]`:** the smallest count within 0.5 % of the best selectable efficiency.
Efficiency rises monotonically with `B` but with strongly diminishing returns, and every extra blade
costs weight, cost and complexity. **B = 16.**

*Downstream consequence:* the CFD periodic sector is **22.5°**, not the 30° assumed when B = 12 was a
placeholder — roughly 25 % fewer cells.

### 3.2 Sweep — derived, and independently corroborated

BEM is strip theory and **cannot produce sweep** (limitation L4). Sweep is therefore a separate
geometric decision with an explicit physical justification:

```
Lambda(r) = arccos( M_cap / M_hel(r) ),    M_cap = 0.78    [DESIGN DECISION]
```

`M_cap` is set marginally above the flight Mach so the inboard blade — where `M_hel` is dominated by
`M₀` — stays essentially unswept, and sweep is introduced only where rotation actually drives
`M_hel` up.

**Result: 44.7° of tip sweep.**

> **Independent corroboration.** NASA's **SR-3** propfan, a real M0.8 design, used **45° of tip
> sweep**. Nothing here was tuned to match that. The agreement follows from imposing the same
> physical constraint, and it is the strongest available sanity check on the design logic.
> *(This is a cross-check, not a validation — SR-3 is not being reproduced.)*

### 3.3 Other outcomes

| Quantity | Value |
|---|---|
| Hub/tip ratio | 0.28 `[DESIGN DECISION]` |
| Max local solidity | 0.485 |
| Chord at 0.75R | 0.247 m (`c/D` = 0.071) |
| Blade angle `β`, hub → tip | 76.5° → 48.3° (strongly non-linear twist) |
| `t/c`, hub → tip | 0.20 → 0.025 |
| Chord Reynolds number | 0.6 – 2.2 × 10⁶ |

---

## 4. GATE G0 — INDEPENDENT VERIFICATION ✅ **PASS**

| Check | Value | Limit | Result |
|---|---|---|---|
| Two efficiency routes agree (`C_T·J/C_P` vs `Tc/Pc`) | 1.4 × 10⁻¹⁴ % | < 1 % | **PASS** |
| BEM `η` below the actuator-disk ceiling | 0.8072 < 0.9629 | — | **PASS** |
| `∫(dT/dr)dr` vs coefficient-derived thrust | 1.4 × 10⁻⁹ % | < 2 % | **PASS** |
| `∫(dQ/dr)dr` vs coefficient-derived torque | 2.0 × 10⁻⁹ % | < 3 % | **PASS** |
| Prescribed `τ` recovered | 0 % | < 0.1 % | **PASS** |
| ζ iteration converged | yes | — | **PASS** |
| Radial-station independence, 41 → 81 | ΔT 0.0000 %, ΔQ 0.0070 %, Δη 0.0070 % | < 0.1 % | **PASS** |

**What G0 does and does not establish.** It establishes that the design is **internally consistent
and numerically converged** — the same quantity computed two independent ways agrees. It establishes
**nothing** about whether a real blade achieves it. That is Phase 4's job.

---

## 5. VALIDITY FLAGS — stated before any result is used

| Flag | Status |
|---|---|
| Stations outside Prandtl–Glauert validity | **41 of 41 — the entire blade** |
| Max `M_normal` after sweep | 0.78 |
| Max `M_helical` | 1.097 |

> **This is the single most important limitation of Phase 1, and it is deliberately not buried.**
> `M_n` = 0.78 exceeds the Prandtl–Glauert validity ceiling (taken conservatively as 0.70)
> **everywhere**, because the flight Mach alone is 0.75. The sectional aerodynamics underpinning the
> BEM design is therefore **nowhere strictly valid** for this rotor.
>
> No compressibility correction was applied, and no polar was extrapolated to pretend otherwise. The
> camber and twist distributions are consequently **design intent, not predicted performance**.
>
> **This is precisely why 3-D compressible CFD is required, and why a CFD-vs-BEM disagreement at the
> tip is a predicted finding rather than a bug.** Gate G4 accordingly sends the investigation to the
> BEM first, not to the mesh.

Also outstanding: `Cd` comes from a low-order correlation with no wave-drag term, and torque —
hence `η_p` — depends on it directly. **The 0.8072 efficiency is an estimate bounded by that
correlation, not a prediction.** `[CFD-TBD]`

---

## 6. ARTIFACTS

| Artifact | Contents |
|---|---|
| `01_design/openfan_design.py` | authoritative design module (ISA, NACA 4-digit, thin-airfoil theory, Adkins–Liebeck, sweep law, G0 checks) |
| `01_design/run_phase1_design.py` | reproducible driver |
| `results/design_table.csv` | **41 stations × 24 columns — the single source of truth for all downstream geometry** |
| `results/design_summary.json` | full labelled record incl. G0 and the blade-count trade |
| `results/blade_count_trade.csv` | the 7-candidate trade study |
| `results/sections/` (41 files) | exact NACA 4-digit coordinates per station |
| `results/figures/` (7) | geometry, Mach/sweep, sweep law, loading, velocity triangles, sections, Re/solidity |

---

## 7. CLAIM HIERARCHY AFTER PHASE 1

### ✅ TIER 1 — verified, safe to state

- "Designed an open-fan rotor from first principles using actuator-disk sizing and Adkins–Liebeck
  minimum-induced-loss blade-element momentum theory under an explicit helical-tip-Mach constraint."
- "Blade count, sweep distribution, chord and twist were **produced by the method**, not assumed."
- "The design was verified by five independent closure checks and a radial-station independence
  study (gate G0, all pass)."
- "The design is defined by a **non-dimensional loading parameter**; thrust and power are outputs."

### ⚠️ TIER 2 — true only in the "designed for" form

- "The rotor was **designed for** τ = 0.08 at M0.75, giving an actuator-disk efficiency ceiling of
  0.963." — **not** "achieves 0.963".
- "The BEM minimum-induced-loss efficiency is 0.807" — **must** carry "estimate, bounded by a
  low-order drag model; CFD to determine".
- "Sweep was **selected** to hold the leading-edge-normal Mach below 0.78."

### ❌ TIER 3 — forbidden

- ❌ Any statement that the rotor **produces** 14.45 kN or **achieves** any efficiency — nothing has
  been simulated or measured.
- ❌ "Optimised" — Adkins–Liebeck minimises *induced* loss only, not profile or wave drag.
- ❌ Any comparison to CFM RISE. The SR-3 sweep agreement is a **cross-check**, not a validation, and
  must always be described as such.
- ❌ Any installed, acoustic, fuel-burn or structural claim.

---

## 8. NEXT — Phase 2 only

Complete the parametric SolidWorks build and pass gate G1 (geometry verified against the independent
analytical volume; save → close → reopen → re-verify). **No CFD result may be reported until the
Phase 3 benchmark cases have run.**
