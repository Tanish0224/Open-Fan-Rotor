# PHASE 0 — PROJECT DEFINITION REPORT
### BA-OF-01 · Open-Fan Rotor: Aerodynamic Design and Installation-Effect Assessment

**Date:** 22 August 2026
**Phase:** 0 — Definition. **No CAD, geometry, mesh, CFD case, or performance number has been produced.**
**Parent research:** [`OPEN_FAN_PROJECT_SELECTION_RESEARCH.md`](../OPEN_FAN_PROJECT_SELECTION_RESEARCH.md) — preserved, cited, **not superseded**
**Definition package:** [`00_requirements/`](00_requirements/) — 12 documents

---

## A. EXECUTIVE RECOMMENDATION

# ▶ PROCEED WITH CONDITIONS

The project is **technically well-founded and the definition is complete**, but it may not proceed
to Phase 1 closure until two blocking items are resolved, and it may not proceed to any expensive
simulation until a timing calibration is measured.

### The three conditions

| # | Condition | Why it blocks |
|---|---|---|
| **C1** | **Resolve the design thrust (B1).** Either source a cruise thrust from a primary document, **or — preferred — invert the problem and prescribe disk loading or power loading as the design input** | Every disk-loading, efficiency-ceiling and blade-loading number descends from it. The 20 kN currently in the documents is an **unsourced placeholder** and is labelled as one. The Boeing RFI ~30 000 lbf figure is **sea-level static**, not cruise, and must not be substituted |
| **C2** | **Confirm airfoil section polar data exists (B2)** across the required Mach range before selecting a family | Phase 1 cannot produce chord and twist without sectional `Cl`/`Cd`. Polars may **not** be extrapolated beyond their stated validity to fill the gap |
| **C3** | **Run the timing calibration before any expensive case** | All cell counts and runtimes in the feasibility audit are **estimates**. Committing an 8 M-cell overnight run against an estimate is exactly how a five-day budget is lost |

**None of these blocks starting Phase 1** — the BEM framework, the parametric geometry code and the
CAD automation can all be built while C1 and C2 are resolved. They block Phase 1 **closure**.

### And one scope correction that is not a condition but a fact

> **The approved title promises installation-effect assessment. That is Level 3 of the feasibility
> audit and it is NOT deliverable in the authorised ~5 days on a personal workstation.** The
> five-day project delivers the *design* and *isolated characterisation* half. This is recorded in
> the requirements as a Tier-3 claim prohibition, not merely as a scheduling note.

---

## B. FROZEN PROJECT STATEMENT

> Design a single-rotation open-fan rotor for high-subsonic cruise from first principles, realise it
> as parametric CAD in which no dimension is typed by hand, and measure — under a strictly
> controlled single-variable comparison — how much of its isolated propulsive performance survives
> installation ahead of a wing.

---

## C. FINAL RECOMMENDED ARCHITECTURE

A **single-rotation, unducted, swept rotor with a spinner and no outlet guide vane**, at full engine
scale, designed by minimum-induced-loss blade-element momentum theory under a helical-tip-Mach
constraint, and evaluated by compressible steady RANS in ANSYS Fluent — first isolated in a periodic
sector, then (Stage 3) **tractor-mounted ahead of a wing segment** in a full annulus.

**Three architectural decisions worth defending explicitly:**

- **No OGV** (ED-008). Swirl recovery is a +0.2–3 % effect on which the literature disagrees by an
  order of magnitude, it carries a ~+20 dB acoustic penalty that cannot be modelled here, and it
  doubles CFD cost without touching the research question. The object of study is therefore an open-fan
  **rotor** — the word "propulsor" or "stage" would imply hardware that does not exist.
- **Tractor, not pusher** (ED-005). Chosen on *method*: the pusher's defining mechanism is a blade
  cutting a viscous wake, which is inherently unsteady and needs URANS. The tractor's wing influence
  is a smooth potential perturbation, which a steady method can legitimately represent.
- **No upstream pylon in the baseline.** Adding one would reintroduce the wake-cutting mechanism
  just rejected, through the back door.

---

## D. FINAL PRIMARY RESEARCH QUESTION

> **For a single-rotation open-fan rotor held at a fixed design point and fixed operating condition,
> what is the change in net propulsive force and propulsive efficiency between an isolated
> free-stream installation and a wing-installed configuration, and how does that change decompose
> into altered rotor inflow, altered wing forces, and non-linear interference?**

---

## E. FINAL BASELINE COMPARISON

| | Held **constant** | **Changed** |
|---|---|---|
| Geometry | Blade shape, blade count, diameter, hub, spinner | **Wing present / absent** |
| Operation | Pitch setting, shaft speed, `J` | — |
| Flow | Flight Mach, altitude, `ρ`, `T`, `a` | — |
| Numerics | Turbulence model, discretisation order, near-blade mesh topology and sizing, convergence criteria | Domain (sector → full annulus, forced by loss of axisymmetry) |

**Three runs, not two:** CFG-ISO (rotor alone) · CFG-WING (wing alone) · CFG-INST (both). The third
is what permits the interference term `F_INST − (F_ISO + F_WING)` to be isolated rather than assumed.

**Gate G5:** any deviation from the "held constant" column voids the comparison and it must be rebuilt.

---

## F. VALIDATION HIERARCHY

```
1. ANALYTICAL   actuator-disk closure · two-route efficiency agreement · BEM station
                independence · momentum balance vs surface integral · Euler work
                                    ⇓  "numerically consistent"
2. CAD          sections vs design table · re-measured chord/twist/thickness/sweep ·
                body count · Check2() · volume/bbox · save→close→reopen→re-verify
                                    ⇓  "geometry verified"
3. NUMERICAL    3-mesh independence on T and Q · residual AND integrated-quantity
                stationarity · y⁺ maps · 2-closure sensitivity · domain sensitivity ·
                sector-vs-full-annulus check
                                    ⇓  "numerically verified / mesh-independent in T,Q"
4. BENCHMARK    Axis A — Caradonna–Tung (NASA TM-81232): compressible rotating blade,
                         transonic tip M_tip 0.877 · PUBLIC, no request
                Axis B — UIUC Propeller Database: axial-flight C_T/C_P/η vs J · PUBLIC
                                    ⇓  "method validated against experiment, per regime"

RESIDUAL GAP    No public benchmark covers compressible AND axial flight together —
                the actual design condition. The two axes BRACKET it; neither spans it.
                THIS MUST BE VOLUNTEERED, NOT CONCEALED.
```

**A correction to the parent research, made on evidence:** it recommended NASA SR-2/SR-3 and F31/A31
as the validation path. Investigation established that their **performance data is public but their
blade coordinate geometry is not confirmed obtainable** — and validation requires reproducing the
geometry. That path was replaced. The parent research is preserved unedited; the correction is
recorded in ED-006 and the evidence index.

**Highest honest project-level classification:**
> *A first-principles rotor design study with a CFD workflow verified numerically and validated
> against two published experimental benchmarks that bracket — but do not jointly cover — the design
> condition. The rotor design and the installed configuration are numerically verified and **not
> experimentally validated**.*

---

## G. CFD RECOMMENDATION (methodology level only)

| Decision | Choice | Reason in one line |
|---|---|---|
| Time treatment | **Steady RANS** | **Exact** for the isolated case; a declared approximation for the deliberately-chosen installed case |
| Frame | Rotating frame / **MRF** | Follows from steady; frozen-rotor bias mitigated by ≥2 blade clocking positions |
| Isolated domain | **Periodic sector 360°/B** | Exact for an axisymmetric configuration, and `B`× cheaper |
| Installed domain | **Full annulus** | The wing destroys axisymmetry — unavoidable, and the project's cost cliff |
| Isolated rotor | **Fully resolved** | Where the design is verified and blade `Cp` and `dT/dr` come from |
| Installed rotor | **Body force, calibrated against the resolved isolated result** | 50–65 M cells resolved is not workstation-feasible. Blade-level installed claims are **withdrawn**, not softened |
| Compressibility | **Compressible, ideal gas, pressure-based coupled, 2nd order** | `M_hel,tip` = 1.10 — the tip is supersonic in the relative frame |
| Turbulence | **k-ω SST**, + Spalart–Allmaras sensitivity | Standard for transonic external/turbomachinery flow; spread reported as model-form uncertainty, never averaged |
| Wall treatment | **`y⁺` ≈ 1** for reported cases | Torque carries a large viscous component and `η_p` divides by torque |

---

## H. TOP FIVE RISKS

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| **R1** | **Claim outruns evidence** — the approved title describes Stage 3, but only Stages 1–2 will exist after five days | **Critical** — this is the risk that destroys the project's credibility in an interview | Tier-3 prohibition on installation claims until Stage 3 exists on disk; the mandated interim description is written into the requirements; the README must state the current stage |
| **R2** | **Design thrust is unsourced (B1)** and propagates into every loading and efficiency number | **High** | Condition C1: invert to a prescribed disk loading, removing the unsourced number entirely |
| **R3** | **BEM is invalid at the transonic tip** (`M_hel` 1.10 vs Prandtl–Glauert validity `M_n ≲ 0.7`), so the design is least trustworthy exactly where the physics is hardest | **High** | Recorded in advance as limitation L1; a CFD-vs-BEM tip disagreement is a **declared expected finding**, and gate G4 sends the investigation to the BEM first, not the mesh |
| **R4** | **Compute reality bites** — estimates are unmeasured, RAM unconfirmed, and one 8 M-cell run can consume a night | **High** | Condition C3 calibration gate; three-level structure so no single run blocks the project; overnight scheduling; **never coarsen the near-blade mesh to fit a deadline — reduce the number of cases instead** |
| **R5** | **Benchmark band is missed** and there is pressure to widen it retrospectively | **Medium-High** | Bands declared before the runs. A missed band is reported and diagnosed, never engineered away |

---

## I. REMAINING UNRESOLVED DECISIONS

| ID | Item | Status | Blocks |
|---|---|---|---|
| **B1** | Design thrust has no primary source | `BLOCKED` | Phase 1 closure; all loading/efficiency numbers |
| **B2** | Airfoil polar data availability unconfirmed at the required Mach | `BLOCKED` | Phase 1 closure |
| **O1** | Workstation core count and RAM **not measured** | `INVESTIGATING` | Feasibility precision; whether the fine mesh is attemptable at all |
| **O2** | Blade count — must become a Phase 1 **output**, not an input | `PROPOSED` | CFD sector angle, hence cell count |
| **O3** | Hub/tip ratio | `PROPOSED` | Phase 1 |
| **O4** | Wing section, chord, span, rotor–wing offsets, **rotation direction** | `PROPOSED` | Stage 3 only — but rotation direction sets the *sign* of the spanwise asymmetry and must be reported with every installed result |
| **O5** | PANDORA download terms | `INVESTIGATING` | Nothing — optional cross-check only |

**Nothing is marked FROZEN.** Freezing happens at the end of Phase 1, when the design closes on
itself and the TBDs have been resolved by calculation rather than by assertion.

---

## J. EXACT NEXT ACTION

**Phase 1, and nothing beyond it.**

1. **Resolve C1** — restate the design input as a prescribed **disk loading** (or power loading), so
   the unsourced thrust disappears from the chain. Record as a Decision Log update to ED-009.
2. **Resolve C2** — confirm sectional polar data availability across the required Mach range; select
   the airfoil family on that evidence and record it.
3. **Build the BEM design code** — actuator-disk sizing, then Adkins–Liebeck minimum-induced-loss BEM
   with Prandtl tip/hub loss and a compressibility correction. Cosine-clustered radial stations.
4. **Resolve blade count and hub/tip ratio as outputs** of the solidity calculation.
5. **Derive the sweep distribution** from the computed `M_hel(r)`, and document the derivation — this
   is the step that converts "the blade is swept because open-fan blades are swept" into engineering.
6. **Pass gate G0** — actuator-disk closure < 0.1 %, two efficiency routes agreeing < 1 %, radial
   station independence < 0.1 %.
7. **Emit the radial design table** as the single source of truth for all downstream geometry, plus
   velocity triangles at hub, mid-span and tip.

**Do not, in Phase 1:** open SolidWorks, generate blade geometry, build a mesh, launch Fluent, or
write any performance claim.

---

## CLOSING NOTE — WHAT THIS PHASE ACTUALLY ESTABLISHED

Four things that were not true before this phase and are load-bearing for everything after it:

1. **The validation path was wrong and is now right.** The parent research's SR-2/SR-3 recommendation
   does not survive contact with the question *"is the geometry public?"*. Two fully-public,
   no-request benchmarks replaced it, and the residual gap between them is named rather than hidden.
2. **The design point closes on itself** — 0.03 % agreement between two independent routes to
   propulsive efficiency — which proves the parameter set is *consistent*, and proves nothing at all
   about whether a real blade achieves it. The distinction is the project.
3. **The helical tip Mach number is 1.10, and it is supersonic.** That single calculated number
   makes sweep a derived necessity rather than an imitation, forces a compressible solver, and sets
   the mesh requirement. It is the most consequential number in the definition.
4. **The scope and the title are honestly reconciled.** The five-day budget delivers the design and
   isolated half. Saying so now, in the controlling document, costs nothing; discovering it in an
   interview would cost everything.

**STOP. Phase 1 requires separate authorisation.**
