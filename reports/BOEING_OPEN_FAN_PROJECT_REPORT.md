# BOEING OPEN-FAN ROTOR PROJECT — AUTHORITATIVE TECHNICAL REPORT
### BA-OF-01 · Status as of 22 August 2026 · Written to establish an exact, honest continuation point

**This report documents what has genuinely been completed and what has not.** It is written
before any CFD solution exists. Every claim below is traced to a saved artifact. Where a value is
an output of the method rather than an input, that is stated explicitly.

---

## 1. Executive Summary

**Motivation.** Open-fan (unducted, high-bypass) propulsion has returned to serious industry
consideration because turbofan bypass ratio is approaching a practical ceiling for further
propulsive-efficiency gains within a conventional nacelle. Removing the nacelle raises propulsive
efficiency further but reintroduces problems the ducted-fan era had designed away: transonic tip
relative velocities, blade sweep as a shock-management tool, and installation/integration effects
that a duct used to shield the airframe from.

**Objective.** Build an aerospace-aerodynamics portfolio project that demonstrates genuine
first-principles engineering — not a downloaded CAD model — covering rotor aerodynamic design,
parametric CAD construction, independent geometric verification, and a preliminary CFD workflow
for an isolated open-fan rotor.

**Engineering question this project is built to answer:** *does a rotor sized by classical
minimum-induced-loss blade-element momentum theory (BEM), with sweep derived from a helical tip
Mach constraint rather than assumed, produce a self-consistent design that can be carried through
CAD and into a real CFD workflow without hidden shortcuts?*

**What has genuinely been completed** (each independently verified, see §13):
- A closed-form, internally-verified BEM aerodynamic design (Gate G0 — PASS).
- A parametric SolidWorks CAD blade, recovered from a documented first-attempt failure, and
  independently verified (Gate G1 — PASS).
- A CFD fluid-domain derivative (22.5° periodic sector) with independently verified geometry.
- A fully classified, boundary-typed, periodically-paired CFD mesh topology (verified against
  analytic domain geometry and by direct HDF5 inspection).

**What remains unfinished, stated plainly:**
- **No volume mesh exists.**
- **No Fluent solver case has been run.**
- **No thrust, torque, power, or efficiency number has been produced by CFD.**
- No mesh-independence study, no validation against any benchmark, no installed configuration.

---

## 2. Industry and Engineering Motivation

The renewed interest in open-fan (also called "unducted fan" / "open rotor") architectures in
current turboprop/turbofan research is driven by the propulsive-efficiency argument: efficiency
rises with bypass ratio / disk loading reduction, and removing the nacelle removes the largest
remaining source of parasitic weight and drag standing in the way of very-high-bypass designs.
This is well-established propulsion theory (actuator-disk / Froude efficiency), not a claim
specific to any one manufacturer's current program.

The two classical engineering problems this reintroduces, and that this project explicitly
engages with, are:

1. **Tip Mach management.** An unducted blade tip operates in a compressible relative-flow
   environment where the flight Mach number and the rotational tip speed combine vectorially
   (the *helical* tip Mach, §6). A duct constrains this; an open rotor does not.
2. **Blade sweep as a shock-management response**, historically explored in open-rotor programs
   from the 1980s (e.g., NASA's advanced-turboprop research, of which SR-3 is one published
   dataset) precisely because of problem (1).

Industry and installation challenges (pylon interaction, cabin noise, gearbox/counter-rotation
architecture choices) are acknowledged here as the reason an *eventual* installed-configuration
study is the long-run target of this line of work — **not** because this project has performed
that study. §14 states the future scope explicitly, separated from current scope.

No claim in this report is attributed to any specific current company program. Historical NASA
open-rotor data (SR-3) is used once, narrowly, in §6, as a plausibility cross-check — not as a
design input and not as validation.

---

## 3. Project Scope

### Current completed scope
- First-principles aerodynamic rotor design (actuator-disk sizing + Adkins–Liebeck minimum-induced-loss BEM)
- Blade-count selection via a structural/solidity trade study
- Radial geometry generation (41-station design table, later independence-checked at 81 stations)
- Swept-blade design, with sweep **derived** from a helical-Mach constraint, not assumed
- Parametric SolidWorks CAD construction, fully scripted (no manual modeling)
- Independent CAD geometric verification (Gate G1)
- CFD periodic-sector fluid-domain construction (22.5°, one of 16 blades)
- CFD boundary-zone classification, naming, typing, and periodic-interface pairing

### Not yet completed
- Volume meshing (prism boundary layer + tetrahedral fill)
- Mesh-independence / convergence study
- Any Fluent solver run
- Thrust, torque, power, or efficiency prediction from CFD
- Validation against any experimental or published performance dataset
- Wing-installed configuration or any installation-effect study

### Explicit future scope
The eventual direction of this work is (a) a converged, mesh-independent preliminary CFD
characterization of the **isolated** rotor, cross-checked where possible against public
open-rotor data (e.g. Caradonna–Tung, UIUC propeller data — chosen because they are public,
not because they match this exact configuration), and only after that, (b) a wing-installed
configuration to study integration effects. **No installed-configuration result exists today,
and none is implied by anything in this repository.**

---

## 4. Design Requirements and Operating Condition

All values below are read directly from `01_design/results/design_summary.json`, produced by
`01_design/run_phase1_design.py`. Each is labeled by its evidence class.

| Quantity | Value | Class |
|---|---|---|
| Flight Mach `M0` | 0.75 | `[REQUIREMENT]` |
| Altitude | 10,668 m (35,000 ft, ISA) | `[REQUIREMENT]` |
| Rotor diameter `D` | 3.5 m | `[DESIGN DECISION]` |
| Hub/tip ratio | 0.28 | `[DESIGN DECISION]` |
| Rotational tip Mach | 0.80 | `[REQUIREMENT]` |
| Non-dimensional loading `τ = T/(ρAV₀²)` | 0.08 | `[DESIGN DECISION]` |
| Blade count `B` | **16** | `[DERIVED]` — output of the solidity/aspect-ratio trade, §5 |
| Root/tip design `Cl` | 0.7 / 0.4 | `[DESIGN DECISION]` |
| Airfoil family | NACA 4-digit, closed-form, blunt TE (0.006c) | `[DESIGN DECISION]` |
| Resulting flight speed `V0` | 222.40 m/s | `[DERIVED]` |
| Rotor angular speed `ω` | 135.559 rad/s (1294.5 rpm) | `[DERIVED]` |
| Advance ratio `J` | 2.945 | `[DERIVED]` |
| **Helical tip Mach** | **1.0966** (supersonic, relative frame) | `[DERIVED]` — §6 |
| Tip sweep | **44.66°** | `[DERIVED]` — §6 |
| `C_T`, `C_P` (BEM) | 0.5450, 1.9886 | `[DERIVED]` |
| `η` (BEM, minimum-induced-loss) | 0.8072 | `[DERIVED]`, **estimate**, bounded above by the actuator-disk ideal ceiling 0.9629 |

**On the removed fixed-thrust requirement.** An earlier framing of this project assumed a
specific aircraft-level thrust requirement. That value had no defensible source (no aircraft
was specified) and was explicitly removed per the Phase 0 authorization. The design is instead
driven by the **non-dimensional loading `τ`**, a standard propeller/rotor sizing parameter that
does not require assuming an aircraft. Thrust, torque, and power are consequently **outputs** of
the sizing calculation at the stated flight condition, not inputs — this is stated explicitly
here because it is easy to misread a `C_T` value as a requirement when it is actually a result.

---

## 5. First-Principles Aerodynamic Design Methodology

Implemented in `01_design/openfan_design.py`; driven by `01_design/run_phase1_design.py`.

**Chain:**
1. **Actuator-disk sizing.** `V0`, `D`, `τ` fix the disk loading and, via momentum theory, the
   induced velocity and ideal (Froude) efficiency ceiling.
2. **Blade-count trade study** (`blade_count_trade` in `design_summary.json`, 8/10/12/14/16/…
   blades evaluated). **Finding, established by inspection of the formulation, not assumed:**
   local solidity `σ = Bc/(2πr)` is *nearly independent* of blade count in this formulation,
   because Adkins–Liebeck chord scales as `1/B` at fixed loading — so solidity constraints alone
   cannot select `B`. Blade count is instead selected by a **blade aspect-ratio** feasibility
   bound (structural/manufacturing plausibility), which **16** satisfies. Blade count is
   therefore reported as an **output** of the trade study, not an assumed input.
3. **Radial discretization.** 41 stations from hub (`r/R = 0.28`) to tip, later re-run at 81
   stations for the independence check (§ below).
4. **Airfoil selection.** NACA 4-digit closed-form sections (exactly reconstructable from four
   published parameters — chosen specifically so no external, unverifiable polar database is
   needed), thin-airfoil theory for `Cl(α)`, a blunt trailing edge (0.006c) added for CAD/meshing
   practicality (not an aerodynamic design choice).
5. **Chord and twist distribution** from the Adkins–Liebeck minimum-induced-loss formulation
   with Prandtl tip/hub loss correction, iterated on the displacement-velocity ratio `ζ` to
   convergence.
6. **Sweep methodology** — see §6, the major technical departure from a naive design.
7. **Tip-Mach constraint** enforced via the sweep law (§6), not by reducing rotational speed.

**Internal consistency checks (Gate G0 — PASS, all seven):**

| Check | Result | Tolerance |
|---|---|---|
| Two independent efficiency routes agree (`C_T·J/C_P` vs `Tc/Pc`) | 1.4×10⁻¹⁴ % | < 1% |
| BEM `η` below the actuator-disk ideal ceiling | 0.8072 < 0.9629 | — |
| `∫(dT/dr)dr` vs coefficient-derived thrust | 1.4×10⁻⁹ % | < 2% |
| `∫(dQ/dr)dr` vs coefficient-derived torque | 2.0×10⁻⁹ % | < 3% |
| Prescribed `τ` recovered from the converged solution | 0% | < 0.1% |
| `ζ` iteration converged | yes | — |
| Radial-station independence, 41 → 81 stations | ΔT 0.0000%, ΔQ 0.0070%, Δη 0.0070% | < 0.1% |

**What this establishes, and what it does not.** These checks prove the design is
**internally self-consistent** — the BEM solution satisfies its own governing equations to near
machine precision, and is insensitive to the chosen radial discretization. **This is not
experimental validation and is not a CFD result.** The achieved efficiency, thrust, and power
will only be independently known once a CFD solution exists — the `η = 0.8072` figure is
explicitly flagged `[CFD-TBD]` in the design output itself.

---

## 6. Tip Mach and Blade Sweep

This is the central aerodynamic design decision in the project and is documented in detail
because it is the part most likely to be mis-stated casually.

**Why flight Mach or rotational tip Mach alone is insufficient.** A propeller/open-fan blade tip
sees two velocity components simultaneously: the axial flight velocity `V0` and the rotational
velocity `U_tip = ω·R_tip`. These are **perpendicular** components of the same relative-velocity
vector seen by the blade section, not alternatives. Reporting only one of them materially
understates the compressibility environment the tip actually experiences.

**The three distinct Mach numbers, never interchanged in this project:**

| Quantity | Value | Meaning |
|---|---|---|
| Flight Mach `M0` | 0.75 | axial free-stream only |
| **Rotational** tip Mach | 0.80 | `U_tip / a`, tangential component only — this is what a "tip Mach = 0.8" claim usually means, and it *understates* the environment |
| **Helical** tip Mach | **1.0966** | `sqrt(V0² + U_tip²) / a` — the actual **vector-sum** relative Mach the tip section experiences |

**Consequence.** At the initial design condition, the helical tip Mach is **supersonic in the
relative frame** (1.0966), even though neither the flight Mach nor the rotational tip Mach alone
suggests anything more than high-subsonic/transonic flow. This is precisely the situation that
made 1980s advanced-turboprop programs adopt swept blades: sweeping the blade reduces the
Mach number normal to the leading edge (the component that actually governs shock formation and
wave drag), in the same way wing sweep manages transonic flow on a swept wing.

**Sweep as a derived response, not an assumption.** The project's sweep law computes, at each
radial station, the sweep angle required to hold the **leading-edge-normal Mach number** at or
below a specified limit (`mn_limit = 0.78`, `[DESIGN DECISION]`), given the local helical
velocity. Sweep therefore **increases with radius**, reaching its maximum at the tip where the
helical velocity is largest:

**Calculated tip sweep: 44.66°** (`design_table.csv`, `r/R = 1.0` row).

**On the NASA SR-3 comparison.** NASA's SR-3 advanced-turboprop design (a published, historical
dataset) used approximately 45° of tip sweep. This project's independently-derived tip sweep of
44.66° is close to that figure. **This is reported only as contextual corroboration that the
independently derived sweep magnitude is physically plausible** — it is a cross-check after the
fact, not an input, and the design was **not** reverse-engineered from SR-3's geometry. The
sweep law here was derived from the leading-edge-normal Mach constraint alone; SR-3's number
was never used as a target.

---

## 7. SolidWorks CAD Development

Fully scripted via SolidWorks COM automation (`pywin32`/`win32com`), zero manual modeling steps.
Every coordinate traces to `01_design/results/design_table.csv` through `02_cad/blade_geometry.py`.

**21 design stations** (`r/R` 0.32 → 0.985) were selected from the 41-station design table for
the CAD build — a CAD-practicality subset of the full aerodynamic radial table, not a
re-derivation.

### v01 — first attempt, preserved as historical evidence, superseded

Each of the 21 sections was represented as a **48-point polyline** sketch, lofted through all 21
profiles in a single feature. The build completed and produced a solid, but independent
verification found:

- `Check2() = 6` where every other known-good body in the project returns 0.
- Visible **chordwise rippling** on inspection.

**Diagnosis (not assumption).** The precise meaning of the `Check2` bitmask could not be
extracted from SolidWorks' own type library or help files (a genuine, reported tooling
limitation — see `02_cad/CAD_CHECK2_DIAGNOSTIC.md`). Rather than guess, every open SolidWorks
document was cross-compared: `Check2 = 6` appeared identically on a **visually clean** 3-section
diagnostic loft, proving the code does not specifically flag the rippling defect — it is common
to the *construction method*. Face-count evidence then located the real cause: the 21-section
polyline loft produced 50 faces (48 non-planar) across only 20 spanwise gaps — a
**faceted/ruled** surface between straight polyline segments on adjacent profiles, rather than a
smooth patch per span.

**Fix (v02):** each section rebuilt as **two open smooth splines** (upper and lower surface,
sharing exact leading/trailing-edge endpoints) instead of one polyline. A single *closed* spline
was tried first and failed outright — consistent with B-spline overshoot at the sharp blunt-TE
corner. A **second, unrelated problem** then surfaced: lofting all 21 two-spline profiles in one
feature failed even though smaller sub-combinations succeeded — isolated by binary search to a
SolidWorks loft-engine limit on the exact 5-station root cluster (highest thickness/chord).
**Fix:** 7 independent lofts of ≤4 profiles each (1-station overlap, full coverage), combined
into one solid via the project's own proven Boolean-ADD recipe.

`openfan_blade_v01.SLDPRT` is **preserved, not deleted** — it is the documented failure that
the diagnosis and fix are built on, and remains part of the verification history.
`openfan_blade_v02_G1_VERIFIED.SLDPRT` is the **authoritative CFD-master geometry** — the only
blade geometry any downstream CFD work should reference.

---

## 8. CAD Verification

**Gate G1, independently verified in a separate process** (`02_cad/verify_cad_v02.py` reopens
the saved file fresh — it does not reuse in-memory state from the build script):

| Criterion | Result |
|---|---|
| Exactly 1 solid body, 0 surface bodies | PASS |
| `Check2() = 0` | PASS — matches every other known-good body in the project |
| Volume vs. **independent** bracket | PASS — 1600.60 cm³, inside [1594.01, 1611.19] cm³ |
| Radial root/tip extent vs. design | PASS — correct to ~1×10⁻⁵ m |
| No negative/degenerate bounding box | PASS |
| Save → close → reopen identical | PASS — 0.0% |

**On the independent volume bracket.** The comparison value was **not** reused from an old
target computed against a different geometry definition. `02_cad/blade_geometry_reference.py`
computes, entirely without SolidWorks, two bounds from the exact same point data sent to CAD:
a smooth closed-form upper bound (1611.19 cm³) and a polygon lower bound from the literal
48-point resampled data (1594.01 cm³) — a bracket, not a single target, because a spline surface
through a set of points bulges slightly outward relative to the polyline through the same points.
The measured CAD volume falls inside this bracket, close to the lower bound, exactly as expected
for a fine discretization.

**On STEP export — distinguish two separate claims.** The v02 master exports to STEP
successfully (477,222 bytes). Reopening that STEP file **inside SolidWorks itself** fails with a
decoded (not guessed) `swFileRequiresRepairError`. This SolidWorks-side reimport is **unverified**
and is documented as an open item. **Separately, and successfully**, the same STEP file was
imported by **ANSYS Fluent Meshing's own CAD translator** (§10) — a different translator,
independent of the SolidWorks-side failure. These are two distinct claims: SolidWorks-native
geometry verification (native `.SLDPRT`, fully verified, §8 above) is complete;
SolidWorks-side STEP reimport is not; ANSYS-side STEP import is verified working.

---

## 9. CFD Domain Construction

**Why a single blade, and why 22.5°.** The isolated rotor configuration is axisymmetric — flow
seen by any one of the 16 blades is, in the rotating frame, identical to that seen by any other.
A single-blade periodic sector (`360°/16 = 22.5°`) is therefore an **exact** representation of
the isolated case, not an approximation, and reduces the required cell count by roughly a factor
of 16 relative to a full-annulus mesh. A full 16-blade CAD assembly was consequently **not
required** for the CFD domain (it remains a separate, deferred presentation-only item, §12/O8).

**Domain construction.** Built as a SolidWorks **derivative** of the verified v02 blade master
(never the master itself — `03_cfd/geometry_transfer/build_fluid_domain.py`): a 22.5° annular
wedge (hub cylinder to a radial far-field, upstream to downstream), created by sketching the
meridional (R–Z) cross-section plus a construction centerline, revolving 22.5°, then Boolean
**SUBTRACT**ing the blade solid to leave the fluid cavity.

| Boundary | Extent used (this preliminary case) |
|---|---|
| Upstream | 2D = 7.0 m |
| Downstream | 3D = 10.5 m |
| Radial far-field | 2D = 7.0 m |
| Hub | plain cylinder, R = 0.49 m (no spinner fairing — deferred, item O9) |

These extents are a **deliberate, documented reduction** from the frozen production-target
domain in `03_cfd/CFD_SETUP_SPECIFICATION.md` (8D/8D/15D), sized specifically to keep a
preliminary workstation-scale mesh tractable. They do not redefine the production specification.

**Independent domain-volume verification.** The Boolean-subtracted fluid domain's measured
volume matches the analytically computed wedge-volume-minus-blade-volume expectation to
**0.0006%** (`03_cfd/geometry/domain_verification_v01.json`). **This verifies the geometry
construction was executed correctly — it is not a CFD result and predicts nothing about the
flow field.**

---

## 10. CAD-to-Fluent Geometry Transfer

- SolidWorks `SaveAs3` STEP export of the fluid-domain derivative: succeeds, 489,553 bytes.
- **ANSYS Fluent Meshing's own CAD import** (`file/import/cad-geometry`) reads this STEP file
  cleanly: confirmed by a successful import producing a valid boundary mesh (1153 nodes / 1467
  boundary faces for the blade-only test; the full domain import is documented in
  `03_cfd/geometry_transfer/`).
- The **only** thing this establishes is that this specific STEP file, via this specific
  translator, is usable for meshing. It does **not** establish general SolidWorks↔ANSYS
  interoperability, and it does **not** resolve the separate, still-open SolidWorks-side STEP
  reimport failure noted in §8 — that failure is in a different translator entirely and remains
  an open item (O10) that simply does not block the CFD path, since the CFD path never goes
  through SolidWorks' own STEP reader.

---

## 11. Boundary Zone Definition and Periodic Topology

CAD import into Fluent Meshing initially produces the domain as **one lumped face zone**
(a default import behavior, not a defect). `boundary/separate/sep-face-zone-by-angle` (40°
feature-angle threshold) splits this into **10 raw zones**, each then **classified by
measurement**, not by name or assumption: for every zone, the area-weighted centroid, mean
surface normal, and total area were computed directly from mesh node coordinates and compared
against the domain's known analytic geometry.

| Zone (measured) | Classification basis | Analytic cross-check |
|---|---|---|
| z = −7.0, normal −Z | inlet | area matches analytic cap area to 0.037% |
| z = +10.5, normal +Z | outlet | 0.037% |
| r = 0.49, radial-inward normal | hub | 0.161% |
| r = 7.0, radial-outward normal | farfield | 0.010% |
| θ = 0°, planar | periodic-1 | — (angular position, exact) |
| θ = 22.5°, planar | periodic-2 | — (angular position, exact) |
| 4 zones, r ∈ [0.56, 1.72], complex curved normals | blade (surface pieces) | r-range matches the CAD blade span exactly |

**Naming, merge, and typing.** The 6 non-blade zones were renamed (`inlet`, `outlet`, `hub`,
`farfield`, `periodic-1`, `periodic-2`); the 4 blade surface pieces (an artifact of the
feature-angle separation cutting the blade's smooth spline surface at internal curvature breaks,
**not** 4 physically distinct walls) were merged into one `blade` zone. Boundary types were then
assigned: `inlet`/`farfield` → pressure-far-field, `outlet` → pressure-outlet, `hub`/`blade` →
wall.

**Periodic pairing.** `boundary/make-periodic` (rotational, 22.5°, about the +Z axis through the
origin) paired `periodic-1` and `periodic-2`.

**Independent verification, not just console output.** The saved mesh file
(`03_cfd/zone_definition/domain_9zones_typed_periodic.msh.h5`) was reopened and its internal
HDF5 zone topology read directly with `h5py`, independent of anything Fluent printed to its own
log:

```
periodic-1 (20 faces)  <-> shadow-14 (20 faces)   -- matching face counts
periodic-2 (2 faces)   <-> shadow-15 (2 faces)    -- matching face counts
```

**What this verifies, and what it does not.** Matching face counts on both sides of each
periodic pair is strong evidence the periodic **topology** is well-formed (every face on one
side has a corresponding face on the other). It does **not** verify that the periodic boundary
condition behaves correctly inside an actual solve — that can only be confirmed once a case
runs and a periodic-consistency check is performed on the solution itself, which has not
happened.

---

## 12. CFD Status

**Completed:**
- CFD geometry import (STEP → Fluent Meshing)
- Boundary face-zone separation (feature-angle method)
- Analytical, measurement-based zone classification (not name-based, not assumed)
- Zone naming, blade-surface merge (4 pieces → 1)
- Boundary-type assignment (pressure-far-field ×2, pressure-outlet, wall ×2)
- Periodic pairing, independently verified via direct HDF5 inspection

**Blocked / not started:**
- Prism boundary-layer generation
- Volume (tetrahedral) mesh generation
- Mesh quality/check gate
- Solver setup and any solver run
- Any preliminary CFD solution

**On the meshing stall — stated factually, not speculatively.** Across repeated attempts to
progress from the verified boundary topology into `mesh/prism/create`, the Fluent Meshing
process hung at an identical point during process startup (after graphics-driver
initialization, before journal execution begins) on multiple independent, clean-process
attempts (confirmed ≥4.7 GB free RAM before each attempt, all prior Fluent/MPI processes
terminated). The zone-selection portion of the prism-creation command was confirmed reachable
and working in one successful attempt. **The specific cause of the startup stall was not
diagnosed** — candidate explanations include license-server round-trip latency (the license
server is a remote host) or accumulated resource contention from repeated same-session
restarts, but neither was confirmed, and no unsupported claim is made about which it is.

---

## 13. Current Verification Hierarchy

| Claim | Status | Evidence |
|---|---|---|
| Aerodynamic design internally consistent | **VERIFIED** | Gate G0, 7/7 checks pass, `design_summary.json` |
| Blade geometry (native CAD) verified | **VERIFIED** | Gate G1, 6/6 checks pass, `cad_verification_v02_G1_independent.json` |
| CAD topology verified | **VERIFIED** | `Check2()=0`, face/topology diagnostics, `CAD_CHECK2_DIAGNOSTIC.md` |
| CFD fluid-domain geometry verified | **VERIFIED** | volume vs. analytic, 0.0006% delta, `domain_verification_v01.json` |
| CFD periodic/boundary topology verified | **VERIFIED** | HDF5 zone inspection, matching face-pair counts |
| CFD mesh (volume) verified | **NOT STARTED** | no mesh file exists |
| CFD solution converged | **NOT STARTED** | no solver run has occurred |
| CFD aerodynamic performance predicted | **NOT STARTED** | no CFD-derived thrust/torque/power/η exists |
| Experimental validation | **NOT STARTED** | no experimental or published-benchmark comparison performed |
| Installed-configuration comparison | **NOT STARTED** | no installed geometry or simulation exists |

---

## 14. Resume-Safe Claims

### SAFE NOW
- Designed a swept open-fan rotor using first-principles aerodynamic sizing (actuator-disk +
  Adkins–Liebeck minimum-induced-loss BEM), with sweep derived from a helical tip-Mach
  constraint and internally verified by seven independent closure checks.
- Developed and independently verified parametric SolidWorks blade geometry, including
  diagnosing and recovering from a documented first-attempt CAD failure.
- Constructed and independently verified a periodic CFD sector fluid domain for the isolated
  rotor.
- Established and independently verified CFD boundary-zone classification and periodic
  interface topology.

### DO NOT CLAIM YET
- Completed CFD analysis of any kind.
- Predicted rotor thrust, torque, power, or efficiency from CFD.
- Validated the design against experimental or published performance data.
- Compared isolated vs. installed performance.
- Optimized the rotor (a single design point has been evaluated, not a design space).

---

## 15. Continuation Plan (not executed — sequence only)

1. Resolve the Fluent meshing startup stall in a fresh ANSYS session (reboot or a session not
   preceded by many rapid restarts); re-run `03_cfd/setup/boundary_zone_setup.jou`
   (reproduces today's verified boundary mesh in ~2 minutes) as the starting point.
2. Discover the remaining `mesh/prism/create` prompt sequence (offset method, first height,
   growth rate, layer count) the same way the periodic-pairing sequence was discovered this
   session — one clean, isolated probe at a time.
3. Generate the preliminary surface + prism + tetrahedral volume mesh per
   `03_cfd/mesh/MESH_SPECIFICATION.md`.
4. Run `mesh/check` and `mesh/quality`; gate against §7 of the mesh specification before
   proceeding.
5. Establish a solver timing-calibration case (per `00_requirements/COMPUTATIONAL_FEASIBILITY_AUDIT.md`)
   before committing to a full run.
6. Run one preliminary isolated-rotor CFD case, explicitly labeled non-final.
7. Perform solution-convergence checks (residuals + integrated-quantity stationarity, per
   `03_cfd/CFD_SETUP_SPECIFICATION.md` §10).
8. Conduct the planned mesh-refinement / independence study (coarse → medium → fine triplet).
9. Compare, where physically valid, against a public benchmark (Caradonna–Tung or UIUC
   propeller data) — dimensional/physical validity checked before any comparison is drawn.
10. Perform design-sensitivity studies only after isolated performance is established.
11. Only after isolated-rotor performance is established and reported honestly, revisit the
    wing-installed scope.
