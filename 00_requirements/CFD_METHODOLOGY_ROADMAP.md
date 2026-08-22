# CFD METHODOLOGY ROADMAP
### BA-OF-01 — the numerical method, and what each choice costs in physics

**Created:** 22 August 2026 · **Phase:** 0 · **Decision:** ED-007
**Solver:** ANSYS Fluent *(user decision, 22 Aug 2026)*
**Platform constraint:** personal workstation; **institutional HPC is not a dependency and may not be claimed**

**Rule applied throughout:** the most sophisticated method is not automatically the right one. Every
decision below states what physics it **captures**, what it **misses**, and why the missing physics
is acceptable *for this project's stated scope* — or, where it is not acceptable, the claim is
withdrawn instead.

---

## 1. STEADY vs UNSTEADY

| | |
|---|---|
| **Decision** | **Steady RANS** for all baseline cases |
| **Captures** | Time-averaged blade loading, thrust, torque, radial distributions, slipstream mean structure, shock position |
| **Misses** | Blade-passing unsteadiness, wake-cutting, 1P loading, vortex shedding, any tonal source |
| **Why acceptable — isolated case** | An isolated rotor in **uniform axial inflow is genuinely steady in the rotating frame**. Steady is not an approximation here; it is exact for the modelled configuration |
| **Why acceptable — installed case** | The selected tractor configuration was chosen *precisely because* the wing's influence on the rotor is a **smooth upstream potential perturbation**, not a viscous wake cut. Time-averaging a smooth perturbation is defensible; time-averaging a wake cut is not |
| **Where it would NOT be acceptable** | Pusher/pylon-wake configurations, and angle-of-attack/1P studies. **Both are excluded from this project on exactly this basis** — see the installation selection document |

**The honest sentence for interview:** *"Steady RANS is exact for my isolated case and a declared
approximation for my installed case. It is why I rejected the pusher configuration — the method
must match the physics, not the other way round."*

---

## 2. FRAME TREATMENT — MRF vs SLIDING MESH

| | |
|---|---|
| **Decision** | **Isolated:** single rotating reference frame over the whole (periodic sector) domain. **Installed:** MRF — rotating cell zone around the rotor, stationary elsewhere |
| **Sliding mesh** | **Rejected** — it is inherently transient, and §1 selected steady |
| **Captures** | Correct Coriolis and centrifugal source terms; correct relative-frame flow |
| **Misses** | With MRF (frozen rotor), the solution depends on the **frozen circumferential position** of the blades relative to the wing |
| **Required mitigation** | The installed case must be run at **≥2 blade clocking positions**, and the spread reported as a **method uncertainty on the installed result**. Reporting a single clocking position as *the* installed answer is forbidden |

---

## 3. DOMAIN EXTENT — PERIODIC SECTOR vs FULL ANNULUS

| Case | Decision | Justification |
|---|---|---|
| **Isolated (CFG-ISO)** | **Periodic sector, 360°/B** | The configuration is axisymmetric. A sector is exact, not an approximation. Cuts cost by a factor of `B` |
| **Installed (CFG-INST)** | **Full annulus is unavoidable** | The wing destroys axisymmetry. There is no periodic sector of an installed rotor |

**Required verification:** one full-annulus isolated run must reproduce the sector result before the
sector is trusted. Cheap insurance against a periodic-boundary error.

**This single row is the project's cost cliff.** The installed case cannot use the sector trick, and
that is what drives §4 and the feasibility audit.

---

## 4. ROTOR REPRESENTATION — RESOLVED BLADES vs BODY FORCE

| | Resolved blades | Body force / blade-element (Fluent VBM) |
|---|---|---|
| Physics | Full 3-D blade boundary layer, tip vortex, shocks | Radially and azimuthally distributed momentum source from BEM data |
| Isolated sector cost | ~3–5 M cells — **feasible** | n/a |
| Installed full-annulus cost | ~50–60 M cells — **not workstation-feasible** | ~5–10 M cells — **feasible** |
| Captures | Everything at blade level | Slipstream momentum and swirl; the wing's response; the disk's response to non-uniform inflow |
| Misses | — | Blade boundary layer, tip vortex detail, shock structure, blade `Cp` |

**Decision:**
- **CFG-ISO: fully resolved blades.** This is where the design is verified and where blade `Cp` and
  `dT/dr` come from. Nothing may replace it.
- **CFG-INST (workstation path): body-force representation**, its inputs taken from the BEM design
  and **calibrated against the resolved CFG-ISO result** (the body-force disk must reproduce the
  resolved isolated thrust, torque and slipstream swirl before it is used installed).
- **CFG-INST (external-compute stretch): fully resolved full annulus**, if compute becomes available.

**The consequence, stated plainly:** on the workstation path the installed study measures the
**slipstream-and-wing** half of the problem (M2, M3, M5) at good fidelity and the **rotor-inflow**
half (M1) at reduced fidelity. Blade-level installed effects — circumferential `Cp` variation —
**cannot** be claimed from a body-force run. Secondary question **S3 is therefore downgraded to
disk-plane inflow non-uniformity**, not blade loading, unless the resolved stretch case is run.

**This is a real limitation and it is recorded, not hidden.** The calibration step is what makes the
body-force route defensible rather than a shortcut.

---

## 5. COMPRESSIBILITY

| | |
|---|---|
| **Decision** | **Compressible, ideal gas, energy equation ON. Non-negotiable** |
| **Reason** | `M_hel,tip = 1.10` at the design point. The tip is **supersonic in the relative frame**. An incompressible solution would be physically meaningless |
| **Solver** | **Pressure-based coupled** — robust through transonic and well-behaved for the rotating frame. Density-based is the fallback if tip shocks prove difficult |
| **Scheme** | Second-order upwind on momentum, energy and turbulence. **First order is for start-up only and no result may be reported from it** |
| **Mesh consequence** | The tip region must resolve a shock. Local refinement in the outer 20 % span is mandatory |

---

## 6. TURBULENCE MODELLING

| | |
|---|---|
| **Baseline** | **k-ω SST** |
| **Why** | Adverse-pressure-gradient and separation behaviour better than k-ε; robust wall treatment; the de facto standard for transonic external and turbomachinery aerodynamics — so results are comparable with the literature |
| **Sensitivity closure** | **Spalart–Allmaras** — a genuinely different formulation (one-equation, built for aerospace external flow), not a variant of the same model |
| **Known weaknesses to state before use** | Both are linear eddy-viscosity models: they under-predict the effect of **streamline curvature and system rotation**, and are **over-diffusive in vortex cores** — so the tip vortex will decay too fast. In the installed case this means slipstream swirl decay is under-resolved, which biases the wing's response |
| **Rule** | The two-closure spread is **reported as model-form uncertainty**. It is never averaged, and the more favourable closure is never selected after the fact |

---

## 7. WALL TREATMENT

| | |
|---|---|
| **Target** | **`y⁺ ≈ 1`, wall-resolved**, for the final isolated case |
| **Why it matters here** | Torque has a large viscous component, and `η_p = TV₀/(Qω)` divides by torque. **Errors in wall shear propagate straight into the headline efficiency number** |
| **Preliminary / Stage-1 runs** | May use coarser `y⁺` with scalable wall functions to obtain a result within the Day-1 budget — **explicitly labelled PRELIMINARY, grounding no performance claim** |
| **Required check** | A **`y⁺` sensitivity study** comparing wall-resolved against wall-function meshes on `T` and `Q` |
| **Project rule** | A `y⁺` claim that holds for some cases but not others is not a `y⁺` claim. The `y⁺` map is therefore reported up front for **every** case, never asserted once and generalised |

---

## 8. MESH STRATEGY

| Element | Approach |
|---|---|
| Topology | Unstructured poly-hexcore (Fluent Mosaic), or hex-dominant if it converges better |
| Blade surface | Curvature and proximity sizing; clustering at leading edge, trailing edge and tip |
| Boundary layer | Prism layers sized to the `y⁺` target with a growth rate ≤ 1.2 and enough layers to contain the boundary layer |
| Refinement regions | (i) outer 20 % span — shock; (ii) tip-vortex path; (iii) slipstream cylinder to the downstream boundary; (iv) *(installed)* wing leading edge and the slipstream–wing impingement region |
| Far field | ≥ 10 `D` upstream and radially, ≥ 20 `D` downstream — **verified by a domain-sensitivity study**, not assumed |
| Quality gates | Max skewness < 0.85; min orthogonal quality > 0.15; reported for every mesh |

---

## 9. BOUNDARY CONDITIONS

| Boundary | Condition |
|---|---|
| Inlet / far field | Pressure far-field at `M₀` = 0.75, ISA 35 000 ft |
| Outlet | Pressure outlet, static pressure, radial equilibrium where appropriate |
| Blade, spinner, wing | No-slip, adiabatic |
| Sector sides *(isolated)* | Rotational periodicity |
| Root plane *(installed)* | Symmetry |

---

## 10. WHAT THIS METHODOLOGY CANNOT DELIVER — STATED UP FRONT

| Cannot deliver | Because |
|---|---|
| Any acoustic quantity | No acoustic model; excluded |
| Blade-passing or wake-interaction unsteadiness | Steady formulation |
| 1P loads / incidence effects | Steady, and zero AoA |
| Accurate far-field tip-vortex persistence | Linear eddy-viscosity models are over-diffusive in vortex cores |
| Transition location | Fully turbulent assumption |
| Installed **blade-level** loading on the workstation path | Body-force rotor representation (§4) |
| Any structural or aeroelastic response | No structural solver |

---

## 11. DECISION SUMMARY

| Decision | Choice | Primary reason |
|---|---|---|
| Time treatment | Steady RANS | Exact for isolated; matches the deliberately-chosen installed configuration |
| Frame | Rotating frame / MRF | Follows from steady |
| Isolated domain | Periodic sector 360°/B | Axisymmetric — exact, and `B`× cheaper |
| Installed domain | Full annulus | Wing breaks axisymmetry — unavoidable |
| Isolated rotor | Fully resolved | Where the design is verified |
| Installed rotor (workstation) | Body force, calibrated to resolved isolated | Only workstation-feasible route |
| Compressibility | Compressible, ideal gas | `M_hel,tip` = 1.10 |
| Turbulence | k-ω SST + SA sensitivity | Standard, with an honest uncertainty band |
| Wall treatment | `y⁺` ≈ 1 target | Torque accuracy drives efficiency |
| Order | Second order | First order reports nothing |
