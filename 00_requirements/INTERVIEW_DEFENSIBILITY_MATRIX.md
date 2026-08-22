# INTERVIEW DEFENSIBILITY MATRIX
### BA-OF-01 — every major engineering decision, and the answer it obliges

**Created:** 22 August 2026 · **Phase:** 0

**Status markers**
- **READY** — answerable now from Phase 0 evidence
- **PENDING PHASE n** — the phase will produce the answer as a normal output; not a blocker
- **UNRESOLVED — BLOCKS IMPLEMENTATION** — information does not exist and the phase **cannot
  legitimately proceed** until it does

---

## A. PROJECT-LEVEL

| Question | Required answer | Evidence | Location | Status |
|---|---|---|---|---|
| **Why open fan?** | Because propulsive efficiency is bounded by disk loading: `η_p,ideal = 2/(1+√(1+2T/ρAV₀²))`. Removing the nacelle removes the constraint that made large swept area expensive. At the selected loading the ideal ceiling is 0.950 | Actuator-disk derivation; CFM public architecture | `DESIGN_POINT_SELECTION.md` §2.8 | **READY** |
| **Why this project question and not "ducted vs open"?** | Because the uninstalled advantage is not in dispute — it follows from momentum theory. What is disputed, and what is governing Boeing's decision, is how much survives installation. GE+Boeing+NASA+ORNL hold 840 000 INCITE node-hours on exactly this; Airbus had not chosen a mounting position as of Jul 2026; Boeing patented an architecture-agnostic strut in Aug 2026 | Parent research §2.3, §12 | `PROJECT_CHARTER.md` §6.5 | **READY** |
| **Why should GE or Boeing care?** | It is the same question at student scale, and it is the question that informs the architecture decision *whichever way that decision goes* | As above | `PROJECT_CHARTER.md` §6.5 | **READY** |
| **What is the single most important limitation?** | No public experimental benchmark covers **compressible *and* axial flight simultaneously** — the actual design condition. The two benchmarks bracket it; neither spans it | V&V two-axis diagram | `VALIDATION_AND_VERIFICATION_PLAN.md` §5.2 | **READY** |
| **What would you do with more time / more compute?** | Fully-resolved full-annulus installed case (≈60 M cells, currently infeasible); then URANS for blade-passing and 1P physics; then an OGV row | Feasibility audit §4 Level 3.7 | `COMPUTATIONAL_FEASIBILITY_AUDIT.md` | **READY** |

---

## B. DESIGN POINT AND GEOMETRY

| Question | Required answer | Evidence | Status |
|---|---|---|---|
| **Why this flight Mach (0.75)?** | Inside CFM's stated M0.75–0.85 open-fan operating range; lowest-cost point in that range that **still produces supersonic helical tip Mach**, so the defining physics is retained rather than dodged | CFM statement; `M_hel` calculation | **READY** |
| **Why 35 000 ft?** | Conventional cruise; independently corroborated by the quoted SR-3 design altitude of 10.68 km | ISA + NASA source | **READY** |
| **Why this rotor diameter (3.5 m)?** | Derived from CFM's stated blade length "over 1.6 m", giving D ≈ 3.5–4 m; the conservative end is taken because the diameter is **inferred, not published** | CFM statement | **READY** — *and the inference must be stated as an inference* |
| **Why this tip Mach (rotational 0.80)?** | Classical propfan practice; it is set by noise and compressibility, not by structure. It is the binding architectural constraint | Propfan literature | **READY** |
| **Why does the helical tip Mach matter more than RPM?** | Because the blade sees the vector sum: `M_hel = √(M₀² + (ωr/a)²)` = 1.10 here. It is supersonic, which is *why* sweep is mandatory | Calculation | **READY** |
| **Why this blade count?** | Must be the **output** of the Phase 1 solidity calculation at the Mach-limited loading, not an input. 12 is a working placeholder only | — | **PENDING PHASE 1** |
| **Why this chord distribution?** | It follows from the Adkins–Liebeck minimum-induced-loss condition with a prescribed `Cl_des`, not from a shape choice | BEM formulation | **PENDING PHASE 1** |
| **Why twist, and why is it non-linear?** | Because `tan φ = V_a/V_t` and `V_t = Ωr` grows linearly with radius while `V_a` barely changes — so `φ` falls steeply outboard. Twist holds each section near its design incidence | Velocity triangle | **READY** (derivation) / **PENDING PHASE 1** (the numbers) |
| **Why this airfoil family?** | The blade is **Mach-limited, not lift-limited**, so the family must have a high critical Mach number. NACA 16-series is the classical propeller family for exactly this reason | — | **UNRESOLVED — BLOCKS IMPLEMENTATION**: usable polar data across the required Mach range has **not been confirmed to exist**. Phase 1 cannot close without it |
| **Why is the blade swept?** | Because `M_n ≈ M_hel·cos Λ` — sweep reduces the leading-edge-normal Mach. **Derived from the computed `M_hel(r)` distribution, not copied from a photograph.** BEM cannot produce sweep, so it is a separate, explicitly justified decision | `ROTOR_DESIGN_METHODOLOGY.md` §6 L2 | **READY** (reasoning) / **PENDING PHASE 1** (distribution) |
| **What is the design thrust and where is it from?** | — | — | **UNRESOLVED — BLOCKS IMPLEMENTATION**: no primary source has been read. Must either be sourced, or the problem inverted to prescribe disk loading instead. The Boeing RFI figure (~30 000 lbf) is **sea-level static** and is not this quantity |
| **Why this wing?** | Must be a published, fully-specified section so it is reproducible | — | **PENDING STAGE 3** |
| **Why this installation location?** | Tractor ahead of a wing — chosen because it is the **only** candidate in which the rotor operating point can be genuinely held constant while the airframe is added, and because the wing's influence is a smooth potential perturbation rather than a wake cut, which is what makes a steady method legitimate | `INSTALLATION_CONFIGURATION_SELECTION.md` §4 | **READY** |
| **Why not over-wing, given Boeing's patent?** | It requires simultaneous credibility in transonic wing design and propulsor aerodynamics — two theses — and no validation data exists for it. Rejected on method and scope, not on relevance | Same doc §2C | **READY** |
| **Why no OGV?** | Swirl recovery is a **+0.2–3 %** effect on which the literature does not agree, it carries a ~+20 dB acoustic penalty that cannot be modelled here, and it doubles the CFD cost without addressing the research question | `PHYSICS_AND_METRICS_MAP.md` §3 | **READY** |

---

## C. CFD METHOD

| Question | Required answer | Evidence | Status |
|---|---|---|---|
| **Why RANS, and why steady?** | Steady is **exact** for an isolated rotor in uniform axial inflow in the rotating frame. For the installed case it is a declared approximation, legitimate because the tractor configuration was chosen so the perturbation is smooth. **This is also why the pusher configuration was rejected** — the method must match the physics | `CFD_METHODOLOGY_ROADMAP.md` §1 | **READY** |
| **What does steady RANS throw away, and does it affect the headline number?** | Blade-passing unsteadiness, wake-cutting, 1P loads, all tonal sources. It does not affect the isolated time-mean forces (exact); for the installed delta it is an approximation whose uncertainty is bounded by the blade-clocking spread | §1, §2 | **READY** |
| **Why MRF, and what is the frozen-rotor weakness?** | Follows from steady. The weakness is dependence on the frozen circumferential position — mitigated by running ≥2 clocking positions and **reporting the spread as method uncertainty** | §2 | **READY** |
| **Why a periodic sector? Isn't that a shortcut?** | It is **exact** for an axisymmetric isolated configuration, and it cuts cost by a factor of B. It is verified by one full-annulus run. It is explicitly **not** available for the installed case, which is why that case is expensive | §3 | **READY** |
| **Why k-ω SST?** | Adverse-pressure-gradient and separation behaviour; robust wall treatment; the de-facto standard for transonic external and turbomachinery flow, so results are comparable with the literature | §6 | **READY** |
| **Where will SST be wrong here?** | Linear eddy-viscosity models under-predict streamline-curvature and rotation effects and are **over-diffusive in vortex cores** — so the tip vortex decays too fast, which biases slipstream swirl reaching the wing | §6 | **READY** |
| **Why compressible?** | `M_hel,tip` = 1.10. The tip is supersonic in the relative frame; an incompressible solution would be meaningless | §5 | **READY** |
| **Why this mesh / what is your `y⁺` strategy?** | Target `y⁺ ≈ 1` wall-resolved for the reported cases, because torque carries a large viscous component and `η_p` divides by torque — wall-shear error propagates straight into the headline efficiency | §7 | **READY** (strategy) / **PENDING PHASE 4** (the maps) |
| **What does mesh independence mean here — independence in what?** | In **integrated thrust and torque**, the quantities actually reported. Not in a contour plot. Criterion declared in advance: < 2 % between the two finest meshes | Gate G2 | **READY** |
| **Why body-force for the installed rotor? Isn't that lower fidelity?** | Yes, and it is declared as such. A fully-resolved full-annulus installed case is ≈60 M cells and 100–330 h — not workstation-feasible. The body-force disk is **calibrated against the resolved isolated result** before use, and **blade-level installed claims are withdrawn**, not softened | Feasibility audit §2–4 | **READY** |

---

## D. VERIFICATION AND VALIDATION

| Question | Required answer | Status |
|---|---|---|
| **What was actually verified?** | Design-point closure; BEM radial-station independence; CAD geometry against the design table with save/reopen re-verification; mesh independence on `T` and `Q`; residual **and** integrated-quantity stationarity; mass and axial-momentum conservation; Euler-work cross-check | **PENDING PHASES 1–4** |
| **What was benchmarked, and against what?** | Two published **experimental** benchmarks, both fully public with no access request: **Caradonna–Tung** (NASA TM-81232) for compressible rotating-blade aerodynamics with a transonic tip (`M_tip` 0.877), and the **UIUC Propeller Database** for axial-flight `C_T`/`C_P`/`η` vs `J` bookkeeping | **READY** (selection) / **PENDING PHASE 3** (results) |
| **Why not the NASA SR-2/SR-3 propfan, the obvious choice?** | Its *performance data* is public but its *blade coordinate geometry* has not been confirmed obtainable, and validation requires reproducing the geometry. **This corrected the parent research's own recommendation.** SR-3's 78.7 % at M0.8 with 45° tip sweep is retained as a qualitative anchor for the sweep argument only | **READY** |
| **Why not the F31/A31 open rotor data?** | Same reason — extensive public data, but the blade geometry is not established as public | **READY** |
| **Why not the TU Delft propeller–wing data, which would validate your installed case?** | It is CC-BY-NC-ND and released only on request with approval. The project was deliberately designed **not to depend on a request that could be refused**. If it were later granted it would upgrade the validation tier | **READY** *(user decision, 22 Aug 2026)* |
| **What was NOT validated?** | The open-fan rotor design itself; the installed configuration; and — most importantly — **the combined compressible + axial-flight regime**, which no available public benchmark covers. Also: no acoustic, structural, or aircraft-level quantity was validated because none was computed | **READY** |
| **Is agreement with your BEM design a validation?** | **No.** It is a consistency check between two of my own models. Validation requires experiment | **READY** |
| **What if the CFD disagrees with your BEM design?** | Expected at the tip, and it is a **finding rather than a failure**: BEM's sectional aerodynamics uses a Prandtl–Glauert correction valid to `M_n ≈ 0.7`, while the tip runs at `M_hel` 1.10. I would investigate the BEM tip treatment before touching the mesh | **READY** |

---

## E. RESULTS AND CLAIMS

| Question | Required answer | Status |
|---|---|---|
| **What efficiency, exactly?** | Propulsive efficiency `η_p = T·V₀/(Qω)`, stated as isolated or installed, at a named operating point. Never an unqualified "efficiency" | **READY** |
| **Where did you draw the line between thrust and drag?** | Convention **BK-1**, declared in advance: thrust = axial force on rotating surfaces; drag = axial force on stationary surfaces; scrubbing therefore lands on the airframe. **Its weakness is that it flatters the propulsor**, so net propulsive force is reported rather than thrust alone, and the result is repeated under convention BK-2 as a sensitivity | **READY** |
| **Would a different bookkeeping convention change your conclusion?** | That is exactly what the BK-1/BK-2 sensitivity tests. If the sign flips, **that is the headline finding** | **READY** |
| **Can you claim installation effects today?** | **No.** Stage 3 does not exist. Until it does, the project is "design and isolated characterisation, with installation assessment in progress" | **READY** |
| **Did you use institutional HPC?** | **No.** The project is workstation-only by design, and claiming institutional HPC is a Tier-3 violation unless separately authorised | **READY** |
| **Is this optimised?** | **No.** No optimisation was run. Adkins–Liebeck is a *minimum-induced-loss* formulation — it does not minimise profile or wave drag, so "optimum" in that narrow sense is not "optimal blade" | **READY** |

---

## BLOCKING ITEMS SUMMARY

Two items are marked **UNRESOLVED — BLOCKS IMPLEMENTATION**. Phase 1 cannot legitimately close
until both are resolved:

| # | Item | Resolution route |
|---|---|---|
| **B1** | **Design thrust has no source.** The Boeing RFI ~30 000 lbf figure is sea-level static, not cruise | Either source a cruise thrust from a primary document, **or invert the problem** and prescribe disk loading / power loading as the design input — which removes the unsourced number entirely. **The second route is preferred** |
| **B2** | **Airfoil section polar data has not been confirmed to exist** across the required Mach range for any candidate family | Confirm data availability before selecting a family. If no family has data at the required Mach, the tip sections must be treated as an explicit uncertainty and the limitation stated — **polars may not be extrapolated beyond their stated validity** |

Neither blocks Phase 0. Both block Phase 1 closure, and B1 additionally propagates into every
disk-loading and efficiency-ceiling number.
