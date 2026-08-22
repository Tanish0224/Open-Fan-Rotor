# PROJECT ROADMAP
### BA-OF-01 — phases, gates, stop conditions, and what each phase entitles the project to claim

**Created:** 22 August 2026 · **Phase:** 0

---

## STAGING — effort vs phases

The authorised effort (~5 working days, personal workstation) does not span all phases. Staging and
phasing are **different axes** and are kept separate so that neither disguises the other.

| Stage | Effort | Phases covered | Honest project description on completion |
|---|---|---|---|
| **Stage 1** | Day 1 | 0, 1, 2, + a *preliminary* touch of 4 | "Designed and built; preliminary CFD set up" |
| **Stage 2** | Days 2–5 | 3, 4 | "Designed, verified, and characterised isolated; method validated" |
| **Stage 3** | Unscheduled | 5, 6, 7 | "…and installation effects quantified" |

**The approved title describes the Stage 3 endpoint.** It is the project's target, not a description
of what exists after five days.

---

## ORDERING — one deliberate change from the approved sequence

The approved conceptual sequence was Phase 0 → 1 → 2 → 3 (methodology verification) → 4 (isolated) →
5 (installed) → 6 (assessment) → 7 (sensitivity). **That ordering is retained**, with one addition:

> **Phase 3 (methodology verification) must complete before any Phase 4 number is reported as a
> result** — but a *preliminary, explicitly non-reportable* Phase 4 run is permitted in Stage 1 to
> prove the workflow end-to-end on Day 1.

This resolves the tension between "validate before you report" and "produce something visible on
Day 1" without compromising the first principle. **The Day-1 run is a workflow demonstration, not a
measurement**, and the claim hierarchy enforces that.

---

## PHASE 0 — Research and project definition ✅ COMPLETE

| | |
|---|---|
| **Objective** | Define the project so every later decision traces to evidence → requirement → decision → verification |
| **Inputs** | Parent research (774 lines); targeted follow-up research; user scope decisions of 22 Aug 2026 |
| **Methods** | Source investigation; option evaluation; claim-hierarchy construction |
| **Outputs** | The 13 documents in `00_requirements/` plus the Phase 0 report |
| **Verification gate** | Every parameter is CALCULATED, PROVISIONAL, or TBD — **none invented** |
| **Stop condition** | Would have triggered if no defensible benchmark existed. **It did not** — two fully public benchmarks were found |
| **Claims enabled** | *"Conducted a documented industry and technical investigation and derived a controlled project definition from it."* No engineering claim |

---

## PHASE 1 — Analytical aerodynamic design

| | |
|---|---|
| **Objective** | Produce the radial blade definition from first principles, and resolve the open TBDs by calculation |
| **Inputs** | Design point; Adkins–Liebeck minimum-induced-loss BEM formulation; sectional polar data |
| **Methods** | Actuator-disk sizing → BEM with Prandtl tip/hub loss and compressibility correction → sweep layered on from the `M_hel(r)` distribution |
| **Outputs** | `blade_design.py`; radial table (`r/R`, `c`, `β`, `t/c`, `Λ`, `Cl_des`, `M_rel`, `M_hel`, `M_n`, `Re`, `a`, `a'`, `F`, `dT/dr`, `dQ/dr`); integrated `T`, `Q`, `P`, `η_p`, `C_T`, `C_P`; velocity triangles at ≥3 radii; **resolved values for blade count, hub/tip ratio, airfoil family, sweep** |
| **Verification gates** | **G0** — actuator-disk closure < 0.1 %; two efficiency routes agree < 1 %; radial-station independence < 0.1 % |
| **Stop conditions** | ▸ Required `Cl_des` exceeds what the section family can deliver at the local Mach → revisit `B` or `D`, do not proceed with an unachievable design ▸ No polar data exists at the required Mach → change family and record it; **do not extrapolate polars beyond stated validity** ▸ Design thrust cannot be sourced → **invert to a prescribed disk loading**; do not keep an unsourced number |
| **Claims enabled** | *"Designed an open-fan rotor from first principles using blade-element momentum theory under an explicit helical-tip-Mach constraint."* **Tier 2 form only** — "designed for", not "achieves" |

---

## PHASE 2 — SolidWorks geometry and CAD verification

| | |
|---|---|
| **Objective** | Realise the radial table as a solid, with **no dimension typed by hand** |
| **Inputs** | Phase 1 radial table (the single source of truth) |
| **Methods** | Python generates section coordinates → SolidWorks API (pywin32 COM, per master-context §36) lofts the blade → pattern to `B` blades → hub and spinner → assembly. **Reference planes only; no face sketches** (§36.4) |
| **Outputs** | Master blade part; rotor assembly; CFD-derivative fluid domain kept **separate from the master** (master/derivative rule); verification JSON; dimensioned drawing with design-point velocity triangles annotated |
| **Verification gates** | **G1** — sections match the table; re-measured chord/twist/thickness/sweep < 0.1 %; body count exact; `Check2()` passes; volume and bbox verified; **save → close → reopen → re-verify** |
| **Stop conditions** | ▸ Loft fails or self-intersects → fix the section stacking, **do not** hand-edit the geometry ▸ Re-measured geometry disagrees with the table → **the CAD is wrong, not the table** ▸ Reopened geometry differs from saved → stop; treat as a save-integrity failure (§36.8) |
| **Claims enabled** | *"Built parametric CAD driven entirely by the analytical design, verified geometrically and re-verified after save/reopen."* |

---

## PHASE 3 — Numerical methodology verification

| | |
|---|---|
| **Objective** | Earn the right to trust the CFD **before** using it to measure anything |
| **Inputs** | CFD methodology decisions; Caradonna–Tung geometry (reconstructed from the published definition); UIUC propeller geometry and data |
| **Methods** | Timing calibration run → **Caradonna–Tung** case (subcritical + transonic `M_tip` 0.877) → **UIUC propeller** `J` sweep → comparison against the **pre-declared** acceptance bands |
| **Outputs** | Calibration measurement replacing all runtime estimates; sectional `Cp` comparison at published radial stations; shock-location comparison; `C_T`/`C_P` vs `J` comparison; mesh and `y⁺` evidence |
| **Verification gates** | **G3** — bands declared **in advance** (Cp shape + suction peak within 10 %; shock location within 5 % chord; `C_T`/`C_P` within 10 % with the trend and peak-`η` `J` reproduced) |
| **Stop conditions** | ▸ **Band missed → report the miss, diagnose it, and do NOT proceed to claim Phase 4 results as trustworthy.** An honest failure is reported, not engineered away by widening the band ▸ Calibration shows Level 2 is unaffordable → re-cut the feasibility levels before committing |
| **Claims enabled** | *"Validated the compressible rotating-blade CFD method against published experimental data (hover regime), and the axial-flight performance bookkeeping against published propeller measurements (low-Mach regime)."* **Plus the mandatory statement of the residual gap.** |

---

## PHASE 4 — Isolated open-fan rotor CFD

| | |
|---|---|
| **Objective** | Measure the designed rotor and test the design intent |
| **Inputs** | Verified CAD; verified method; design point |
| **Methods** | Periodic sector, rotating frame, compressible, k-ω SST; 3-mesh independence study; SA sensitivity; `y⁺` sensitivity; domain sensitivity; full-annulus periodicity check; `J`/tip-Mach sweep |
| **Outputs** | `T`, `Q`, `P`, `η_p`, `C_T`, `C_P` with uncertainty; **`dT/dr` compared against BEM**; blade `Cp` at hub/mid/tip; `M_hel(r)`; slipstream swirl and total-pressure survey; tip-vortex diagnostics; efficiency vs helical tip Mach |
| **Verification gates** | **G2** — `T` and `Q` within 2 % between the two finest meshes; residuals ≥4 orders **and** integrated quantities stationary. **G4** — CFD thrust within a pre-declared band of BEM intent |
| **Stop conditions** | ▸ **G2 fails → no performance number may be reported at all** ▸ G4 fails → investigate the **BEM** first (tip loss, compressibility correction at the transonic tip — the known weakness L1), then the mesh. **A G4 miss is a finding to report, not a failure to hide** ▸ CFD thrust exceeds the actuator-disk ideal ceiling → a bookkeeping or reference-frame error exists; stop and fix |
| **Claims enabled** | Tier 1: mesh-independent isolated performance with stated uncertainty; the tip-Mach trade; the 3-D-vs-1-D design comparison |

---

## PHASE 5 — Wing-installed configuration *(Stage 3)*

| | |
|---|---|
| **Objective** | Produce CFG-WING and CFG-INST under a strict control |
| **Inputs** | Verified isolated rotor; selected tractor configuration; declared bookkeeping convention BK-1 |
| **Methods** | Body-force rotor **calibrated against the resolved isolated result** (must reproduce isolated `T`, `Q` and slipstream swirl before use); full-annulus domain; wing segment; ≥2 blade clocking positions |
| **Outputs** | CFG-WING and CFG-INST force breakdowns; disk-plane inflow non-uniformity; wing spanwise `Cl(y)`, `Cd(y)`; `q_scrub/q_∞` |
| **Verification gates** | **G5** — CFG-ISO and CFG-INST differ **only** by the presence of the wing; body-force calibration reproduces resolved isolated `T`/`Q` within a declared band |
| **Stop conditions** | ▸ Body-force disk cannot reproduce the resolved isolated result → **it may not be used installed** ▸ Any control variable differs between cases → the comparison is void and must be rebuilt ▸ Memory or runtime exceeds the workstation → **do not coarsen the wing mesh to fit**; reduce the number of cases |
| **Claims enabled** | *(only on completion)* installed-vs-isolated performance change |

---

## PHASE 6 — Installation-effect assessment *(Stage 3)*

| | |
|---|---|
| **Objective** | Answer the primary research question and decompose the answer |
| **Methods** | Three-run decomposition: `F_INST − (F_ISO + F_WING)` = interference; attribute the remainder to inflow change (M1), wing force change (M2/M3) |
| **Outputs** | The installation delta in `NPF` and `η_p`; the decomposition table; results under **both** BK-1 and BK-2 |
| **Verification gates** | Delta must exceed the combined mesh-convergence and clocking uncertainty |
| **Stop conditions** | ▸ **Delta smaller than uncertainty → the result is NULL and must be reported as null.** An effect below the resolution of the method is not a finding ▸ Conclusion sign flips between BK-1 and BK-2 → **that becomes the headline finding** and must be reported as such |
| **Claims enabled** | The full approved title |

---

## PHASE 7 — Sensitivity and engineering interpretation *(Stage 3)*

| | |
|---|---|
| **Objective** | Establish how robust the answer is, and what it means |
| **Methods** | Axial and vertical offset variation; thrust-setting variation; rotation-direction effect on spanwise asymmetry |
| **Outputs** | Sensitivity tables; the limitations page; the interview brief |
| **Stop condition** | ▸ Sensitivity exceeds the effect being measured → the conclusion is configuration-specific and must be stated as such, not generalised |
| **Claims enabled** | Robustness qualifiers on all Phase 6 claims |

---

## PROJECT-WIDE STOP CONDITIONS

Immediate stop-and-report, at any phase:

1. A required number cannot be sourced and there is a temptation to invent one.
2. A verification gate fails and there is a temptation to loosen it after the fact.
3. A benchmark band is missed and there is a temptation to widen it retrospectively.
4. Mesh quality would have to be degraded to meet a deadline.
5. The result requires acoustics, structures, or a mission model to be meaningful.
6. A claim is being drafted that sits in Tier 3.
7. Proprietary geometry is being considered as a shortcut.
8. Institutional HPC is about to be used or claimed without authorisation.

---

## GATE SUMMARY

| Gate | Phase | Condition | Failure consequence |
|---|---|---|---|
| **G0** | 1 | Design point closes < 1 % | Phase 1 cannot close |
| **G1** | 2 | CAD verified; survives save/reopen | Phase 2 cannot close |
| **G2** | 4 | `T`, `Q` < 2 % between two finest meshes | **No performance number may be reported** |
| **G3** | 3 | Benchmark within pre-declared band | Method verification fails; report honestly |
| **G4** | 4 | CFD vs BEM within pre-declared band | A finding; investigate BEM first |
| **G5** | 5 | Only the wing differs | Comparison void |
