# First-Principles Aerodynamic Design and CFD Preprocessing of a Swept Open-Fan Rotor
### BA-OF-01 · Engineering Design Report · 22 August 2026

**Author's note on scope.** This report documents work that has genuinely been completed and
independently verified. It stops exactly where the verified work stops. No CFD solution exists
at the time of writing, and no statement below should be read as implying otherwise.

---

## 1. Executive Summary

**The engineering problem.** An open-fan (unducted) rotor removes the nacelle that a
conventional turbofan uses to shield its blades from the free-stream, trading nacelle
weight/drag for two reintroduced problems: the blade tip now operates in a compressible,
partially transonic relative-flow environment, and blade sweep — rather than a duct — becomes
the primary tool for managing it. This project designs, builds, and verifies a rotor around
exactly that problem, then prepares (but does not yet execute) a CFD analysis of it.

**Approach.** A rotor was sized at a stated flight condition using classical actuator-disk theory
and the Adkins–Liebeck minimum-induced-loss blade-element-momentum (BEM) method, with blade
count treated as an *output* of a solidity/aspect-ratio trade rather than an assumption, and
blade sweep *derived* from a leading-edge-normal Mach constraint rather than assumed or copied
from a reference design. The design was then built as fully parametric SolidWorks CAD, and a
CFD fluid domain and boundary topology were constructed and verified in preparation for an
isolated-rotor CFD study.

**Key completed outcomes:**
- A first-principles aerodynamic design, internally verified by seven independent closure checks
  (Gate G0 — PASS).
- A parametric CAD blade, recovered from a documented first-attempt construction failure and
  independently re-verified in a separate process (Gate G1 — PASS).
- A verified 22.5° periodic-sector CFD fluid domain, with boundary zones classified against
  analytic geometry and periodic topology independently confirmed.

**Current project maturity.** Design and CAD are complete and verified. CFD preprocessing
(geometry transfer, boundary classification, periodic pairing) is complete and verified. **Volume
meshing, solver execution, and all CFD results are not yet started.** §8 states this maturity
state in full; a companion status graphic (`figures/06_project_maturity.png`) presents the same
information visually in the project README.

---

## 2. Industrial and Engineering Motivation

Turbofan propulsive efficiency improves with bypass ratio, and conventional ducted-nacelle
architectures are approaching a practical ceiling on how far that ratio can be pushed before
nacelle weight and drag erode the gain. Open-fan (unducted) architectures remove that ceiling by
removing the duct — at the cost of reintroducing two problems 1980s advanced-turboprop research
already worked through once: a blade tip that sees a genuinely compressible, partly transonic
relative-flow environment even at a modest flight Mach number, and the resulting need for blade
sweep as the primary shock-management tool a duct would otherwise have made unnecessary.

This project is scoped deliberately narrower than "design and validate a full propulsion
system." It focuses on **first-principles rotor design and CFD preparation**: demonstrating that
a defensible aerodynamic design can be produced from governing equations rather than assumed
geometry, carried through independently-verified CAD, and staged into a CFD workflow whose
domain and boundary conditions are themselves verified before any solver time is spent. No
company-specific current program is referenced or implied anywhere in this project; historical,
published NASA advanced-turboprop data (SR-3) is used exactly once, in §5, as a plausibility
cross-check.

---

## 3. Problem Definition and Scope

**The project studies:** the aerodynamic design and CFD preprocessing of a single, isolated,
un-installed open-fan rotor blade, at one fixed design point (`M0 = 0.75`, 35,000 ft ISA), sized
by a non-dimensional loading parameter rather than an assumed aircraft thrust requirement.

**Explicitly included:**
- Actuator-disk sizing and Adkins–Liebeck minimum-induced-loss BEM design at the stated
  condition.
- A blade-count trade study.
- A helical-tip-Mach-driven sweep law.
- Parametric CAD construction and independent geometric verification.
- Construction and independent verification of a 22.5° periodic-sector CFD fluid domain and its
  boundary/periodic topology.

**Explicitly excluded from this project as it currently stands:**
- Volume meshing and any CFD solver execution.
- Any CFD-derived performance number (thrust, torque, power, efficiency).
- Experimental or published-benchmark validation.
- Any installed (wing-integrated) configuration or analysis.
- A full 16-blade rotor CAD assembly (deferred — a SolidWorks installation-level limitation, not
  required for the CFD domain, which uses one periodic sector).
- A spinner/hub fairing (the hub is currently modeled as a plain cylinder).

---

## 4. Design Methodology

Implemented in `01_design/openfan_design.py`, driven by `01_design/run_phase1_design.py`. Every
equation below is the equation actually implemented, not a general textbook restatement.

### 4.1 Design condition and non-dimensional loading

The rotor is sized by a prescribed **non-dimensional thrust loading**

```
τ = T / (ρ A V0²)
```

rather than an assumed absolute thrust — because no specific aircraft was specified for this
project, an absolute thrust value would have no defensible source. `τ = 0.08` was chosen as a
representative cruise-loading value (`[DESIGN DECISION]`); thrust, torque, and power are
**outputs** of the sizing calculation at this loading, not inputs. `A = πR²` is the rotor disk
area and `V0` the flight speed at the design Mach and altitude.

### 4.2 Actuator-disk sizing

Momentum theory gives the ideal (Froude) propulsive efficiency ceiling directly from `τ` via the
thrust coefficient `Tc = 2τ`:

```
η_ideal = 2 / (1 + √(1 + Tc))
```

This is an upper bound no real blade-element design can exceed — used in §5 as a sanity ceiling
on the BEM result, not as the design target itself.

### 4.3 Blade-count trade study

Local solidity `σ = Bc/(2πr)` is, in the Adkins–Liebeck formulation, **nearly independent of
blade count** at fixed loading, because chord `c` scales approximately as `1/B` to hold `τ`
constant — a structural finding established by inspecting the formulation, not assumed.
Solidity alone therefore cannot discriminate between candidate blade counts. Blade count was
instead selected via a **blade aspect-ratio** feasibility bound evaluated across candidate
counts (8, 10, 12, 14, 16, …) in `blade_count_trade` (`design_summary.json`); **16 blades**
satisfies this bound and is reported as the study's *output*, not an assumed input.

### 4.4 Adkins–Liebeck minimum-induced-loss BEM

For each radial station (normalized radius `x = r/R`, tip-speed ratio `λ = V0/(ΩR)`), the
method solves for the flow angle via

```
tan(φ) = λ(1 + ζ/2) / x        (helical inflow angle, with the displacement-velocity ratio ζ)
```

and the minimum-induced-loss circulation function `G` (Goldstein-type, evaluated with a Prandtl
tip/hub loss correction `F`), from which the chord follows via the Betz/Adkins relation

```
W·c = 4π λ G V0 R ζ / (Cl · B)
```

with axial and tangential induction factors

```
a_axial   = (ζ/2)·cos²φ·(1 − ε·tanφ)
a_tangential = (ζ/(2x))·cosφ·sinφ·(1 + ε/tanφ)
```

(`ε = Cd/Cl`, the local section drag-to-lift ratio). The single free parameter `ζ` is iterated
to convergence against the prescribed loading:

```
ζ_(n+1) = I1/(2·I2) − √[(I1/(2·I2))² − Tc/I2]
```

(`I1`, `I2` are span-integrated functions of the converged station solution), under-relaxed for
numerical stability. Convergence closes the design: `Tc`, `Pc = J1·ζ + J2·ζ²`, and
`η_BEM = Tc/Pc` follow directly.

**Physical meaning.** `ζ` represents how much axial/tangential velocity the rotor's wake carries
relative to freestream — it is the single scalar that, once found, fixes every station's chord
and twist simultaneously under the minimum-induced-loss constraint (Betz's condition: induced
losses are minimized when the local helical-wake pitch is constant across the span).

### 4.5 Airfoil parameterization

NACA 4-digit sections were used in **closed form** (camber line `m,p`, thickness `t` directly
parameterize the section) specifically because they are exactly reconstructable from four
published numbers, with thin-airfoil theory giving `Cl(α)` analytically — removing any
dependency on an external, unverifiable experimental polar database. A blunt trailing edge
(`0.006c`) was added purely for CAD/meshing practicality, not as an aerodynamic design choice.

### 4.6 Helical tip-Mach constraint and the aerodynamic rationale for sweep

A rotating blade section sees the **vector sum** of the axial flight velocity and the local
rotational (tangential) velocity — not one or the other in isolation:

```
M_helical(r) = √(M0² + M_rot(r)²)        M_rot(r) = Ω·r / a
```

At the design condition this is **supersonic at the tip** (`M_helical,tip = 1.0966`) even though
neither `M0 = 0.75` nor the rotational tip Mach `0.80` alone suggests anything beyond transonic
flow. This is the central compressibility problem an open (unducted) rotor reintroduces, and it
is what motivates sweep: sweeping the blade by angle `Λ(r)` reduces the Mach number **normal to
the leading edge** — the component that actually governs shock formation and wave drag, in
direct analogy to wing sweep — via

```
cos Λ(r) = M_n,limit / M_helical(r)        M_n(r) = M_helical(r)·cos Λ(r)
```

with the design cap `M_n,limit = 0.78` (`[DESIGN DECISION]`, inside the Prandtl–Glauert validity
range used elsewhere in the design). Sweep is therefore **zero** wherever `M_helical ≤ M_n,limit`
and grows monotonically outboard as the helical velocity rises — it is a **derived response** to
a computed constraint, not an assumed planform shape. Figure 7
(`07_why_swept_tip_mach_rationale.png`) plots this constraint explicitly across the span.

---

## 5. Design Results and Verification

### 5.1 Final design characteristics

| Quantity | Value | Class |
|---|---|---|
| Blade count `B` | **16** | output of §4.3 |
| Diameter `D` | 3.5 m | design decision |
| Rotational tip Mach | 0.80 | requirement |
| **Helical tip Mach** | **1.0966** (supersonic) | derived, §4.6 |
| **Tip sweep** | **44.66°** | derived, §4.6 |
| `C_T`, `C_P` | 0.5450, 1.9886 | derived |
| `η_BEM` | 0.8072 | derived **estimate**, `[CFD-TBD]` |
| `η_ideal` ceiling | 0.9629 | derived, §4.2 |

### 5.2 Spanwise distributions

Figure 3 (`03_spanwise_design_distributions.png`) presents chord, twist (blade angle `β` and
flow angle `φ`), and thickness ratio across the span, produced directly from
`design_table.csv` (41 radial stations, hub `r/R = 0.28` to tip). Chord peaks around `r/R ≈ 0.87`
and tapers sharply toward both hub and tip, consistent with the minimum-induced-loss loading
distribution; thickness ratio falls from 20% at the root to 2.5% at the tip, as expected for a
section family transitioning from structural (root) to aerodynamic (tip) sizing priority.

### 5.3 Sweep derivation and the SR-3 comparison

The 44.66° tip sweep (Figure 7) is the value the leading-edge-normal Mach constraint of §4.6
produces at this design point — nothing about NASA's SR-3 advanced-turboprop design (which used
approximately 45° of tip sweep) was used as an input anywhere in the derivation. **The
closeness of these two numbers is reported here only as an independent plausibility
comparison**: two independently-derived swept-rotor designs, motivated by the same underlying
physics (managing helical tip Mach), arriving at similar sweep magnitudes is evidence the
derivation is physically reasonable. **It is not validation** — no SR-3 performance data, wind
tunnel result, or geometry file was used to check, calibrate, or constrain this project's design
at any point.

### 5.4 Seven internal consistency checks (Gate G0)

| # | Check | Result | Tolerance |
|---|---|---|---|
| 1 | Two independent efficiency routes agree (`C_T·J/C_P` vs. `Tc/Pc`) | 1.4×10⁻¹⁴ % | < 1% |
| 2 | BEM `η` below the actuator-disk ideal ceiling | 0.8072 < 0.9629 | — |
| 3 | `∫(dT/dr)dr` vs. coefficient-derived thrust | 1.4×10⁻⁹ % | < 2% |
| 4 | `∫(dQ/dr)dr` vs. coefficient-derived torque | 2.0×10⁻⁹ % | < 3% |
| 5 | Prescribed `τ` recovered from the converged solution | 0% | < 0.1% |
| 6 | `ζ` iteration converged | yes | — |
| 7 | Radial-station independence, 41 → 81 stations | ΔT 0.0000%, ΔQ 0.0070%, Δη 0.0070% | < 0.1% |

All seven pass. **What this establishes:** the BEM solution satisfies its own governing
equations to near machine precision and is insensitive to radial discretization — the design is
**internally self-consistent**. **What it does not establish:** that `η = 0.8072` (or any other
BEM-derived quantity) is the value a real flow field would produce. That can only be known once
a CFD solution exists, which is why `η_BEM` is carried through this entire project labeled
`[CFD-TBD]`.

---

## 6. Parametric CAD Development and Verification

Fully scripted via SolidWorks COM automation — zero manual modeling. Every coordinate traces
through `02_cad/blade_geometry.py` to `design_table.csv`.

### 6.1 Section generation and placement

21 of the 41 aerodynamic radial stations (`r/R` 0.32 → 0.985 — a CAD-practicality subset, not a
re-derivation) were used for the CAD build. Each station's NACA 4-digit section (§4.5) was
resampled to a uniform 48-point arc-length distribution and placed on a plane offset along the
radial axis; twist was applied as the section's in-plane rotation (the local blade angle `β`
from §4.4); sweep was applied as a tangential (in-plane) offset of the section origin, following
the sweep law of §4.6.

### 6.2 Initial loft construction — the encountered failure

The first build (v01) represented each section as a 48-segment polyline and lofted all 21
profiles in one feature. The build completed and produced a solid, but independent verification
found `Check2() = 6` (every other known-good body in the project returns 0) and visible
chordwise rippling on inspection.

### 6.3 Root-cause investigation

Rather than accept "invalid geometry" as a final diagnosis, the value's actual meaning was
investigated first: SolidWorks' own type library exposes no symbolic bit table for `Check2`'s
return code, and its CHM help could not be locally extracted (a genuine tooling limitation,
reported as such rather than worked around with a guess). The decisive evidence instead came
from a **cross-document comparison**: every open SolidWorks body was checked, and `Check2 = 6`
appeared identically on a visually clean 3-section diagnostic loft — proving the code does not
specifically flag the rippling defect, only the *construction method* in general. Face-count
analysis then located the real cause: the 21-section polyline loft produced 50 faces (48
non-planar) across only 20 spanwise gaps — a faceted/ruled surface between straight segments,
not one smooth patch per span.

### 6.4 Recovery — segmented spline lofting (v02)

Each section was rebuilt as **two open smooth splines** (upper and lower surface, sharing exact
leading/trailing-edge endpoints) rather than one polyline. A single *closed* spline was tried
first and failed to loft at all, consistent with B-spline overshoot at the sharp blunt-TE
corner. A second, independent limitation then surfaced — lofting all 21 two-spline profiles in
one feature failed even though smaller sub-combinations succeeded, isolated by binary search to
a SolidWorks loft-engine limit on the highest-thickness root cluster. The final recovery used
**seven independent lofts of ≤4 profiles each** (one-station overlap, full span coverage),
combined into a single solid with the project's own previously-proven Boolean-ADD recipe.

`openfan_blade_v01.SLDPRT` is preserved as the documented failure the diagnosis is built on, not
deleted. `openfan_blade_v02_G1_VERIFIED.SLDPRT` is the authoritative CFD-master geometry.

### 6.5 Independent verification (Gate G1)

Verified in a **separate process** (the verification script reopens the saved file fresh, never
reusing in-memory state from the build):

| Criterion | Result |
|---|---|
| Exactly 1 solid body, 0 surface bodies | PASS |
| `Check2() = 0` | PASS |
| Volume vs. independent bracket (computed without SolidWorks, from the exact points sent to CAD) | PASS — 1600.60 cm³, inside [1594.01, 1611.19] cm³ |
| Radial root/tip extent vs. design | PASS — correct to ~1×10⁻⁵ m |
| No negative/degenerate bounding box | PASS |
| Save → close → reopen identical | PASS — 0.0% |

Figure 1 (`01_blade_isometric_verified.png`) and Figure 2 (`02_blade_sweep_planform.png`) show
this verified v02 master from two angles — the isometric construction view and a plan view
making the planform sweep of §5.3 directly visible.

---

## 7. CFD Domain and Boundary Preparation

**This section documents verified preprocessing only. It stops before meshing.**

### 7.1 Periodic-sector rationale

The isolated rotor configuration is axisymmetric: the flow any one of the 16 blades sees, in the
rotating frame, is identical to what every other blade sees. A single-blade 22.5° (`360°/16`)
periodic sector is therefore an **exact** representation of the isolated case, not an
approximation, at roughly 1/16th the cell count of a full-annulus mesh. A full 16-blade CAD
assembly is consequently not required for the CFD domain (it remains a separate, deferred,
presentation-only item).

### 7.2 Fluid-domain construction

Built as a SolidWorks **derivative** of the verified v02 blade master (never the master itself):
a 22.5° annular wedge — hub cylinder to a radial far-field, upstream to downstream — created by
revolving a meridional (R–Z) profile and Boolean-**subtracting** the blade solid to leave the
fluid cavity.

| Boundary | Type | Extent (this preliminary case) |
|---|---|---|
| Inlet | pressure-far-field | z = −7.0 m |
| Outlet | pressure-outlet | z = +10.5 m |
| Hub | wall | r = 0.49 m (plain cylinder — no spinner fairing yet) |
| Farfield | pressure-far-field | r = 7.0 m |
| Periodic-1 / Periodic-2 | periodic pair | θ = 0° / θ = 22.5° |
| Blade | wall | r ∈ [0.56, 1.72] m |

These extents are a documented, deliberate reduction from the frozen production-target domain
(8D/8D/15D), sized to keep a preliminary workstation-scale mesh tractable — they do not redefine
the production specification. Figure 5 (`05_cfd_domain_boundaries.png`) presents this domain as
a labeled schematic: the meridional cross-section (left) and the sector plan view (right). The
blade is shown only as a labeled radial-span footprint band in the left panel — its true
axial shape is not rendered there, since sweep in this project's coordinate system is a
tangential (visible in the right-hand plan view), not axial, quantity.

**Independent domain-volume verification.** The Boolean-subtracted domain's measured volume
matches the analytically computed wedge-volume-minus-blade-volume expectation to **0.0006%**.
This verifies the geometry construction was executed correctly; it predicts nothing about flow.

### 7.3 Geometry transfer to ANSYS Fluent

The domain's STEP export was confirmed to import cleanly via **ANSYS Fluent Meshing's own CAD
translator** — a different, independent translator from SolidWorks' own STEP reader (which
separately fails to reopen this export, an unrelated open item that does not block the CFD
path, since that path never uses SolidWorks' STEP reader). This establishes only that this
specific file, via this specific translator, is usable for meshing.

### 7.4 Boundary-zone classification against analytic geometry

CAD import initially produces the domain as one lumped face zone (a default behavior).
Feature-angle separation (40° threshold) split this into 10 raw zones, each then **classified
by direct measurement** — area-weighted centroid, mean surface normal, and total area, computed
from mesh node coordinates and compared against the domain's known analytic geometry — not by
zone name or assumption:

| Measured zone | Basis | Analytic area agreement |
|---|---|---|
| z = −7.0, normal −Z | inlet | 0.037% |
| z = +10.5, normal +Z | outlet | 0.037% |
| r = 0.49, radial-inward normal | hub | 0.161% |
| r = 7.0, radial-outward normal | farfield | 0.010% |
| θ = 0° / θ = 22.5°, planar | periodic-1 / periodic-2 | — (exact angular position) |
| r ∈ [0.56, 1.72], complex curved normals, 4 zones | blade (surface pieces) | r-range matches CAD span exactly |

The four blade "zones" are a tessellation artifact (feature-angle separation cutting the blade's
smooth spline surface at internal curvature breaks) — correctly identified as such and merged
into one `blade` wall zone, not left as four physically distinct walls.

### 7.5 Periodic pairing — independent verification

`boundary/make-periodic` (rotational, 22.5°, about the rotor axis) paired the two periodic
faces. This was verified **independently of Fluent's own console output**: the saved mesh
file's internal HDF5 zone topology was read directly with `h5py`, confirming
`periodic-1 ↔ shadow-14` (20 ↔ 20 faces) and `periodic-2 ↔ shadow-15` (2 ↔ 2 faces) — matching
face counts on both sides of each pair, strong evidence the periodic **topology** is
well-formed. This verifies topology only; it does not verify solver-side periodic behavior,
which can only be confirmed once a case actually runs.

**This is where verified CFD preprocessing currently ends.**

---

## 8. Current Limitations and Next Engineering Steps

**Stated explicitly, with no qualification:**
- No volume mesh exists.
- No prism (boundary-layer) mesh layers exist.
- No CFD solver solution exists.
- No thrust, torque, power, or efficiency value has been produced by CFD.
- No validation against any experimental or published performance dataset has been performed.
- No installed (wing-integrated) configuration or analysis exists.
- No HPC/cluster resource has been used at any point — all work to date has run on a single
  workstation (8 cores, 15.2 GB RAM).

**The correct future workflow, in order, not yet executed:**
1. Generate the preliminary surface, prism-layer, and tetrahedral volume mesh against the
   already-written mesh specification (targets only, not yet executed).
2. Run mesh-check and mesh-quality gates; do not proceed past a failing gate.
3. Establish a solver timing-calibration case before committing to a full run.
4. Run one preliminary isolated-rotor CFD case, explicitly labeled non-final.
5. Perform residual and integrated-quantity convergence checks.
6. Conduct a coarse/medium/fine mesh-independence study.
7. Compare, only where physically valid, against a public benchmark dataset (e.g.
   Caradonna–Tung or UIUC propeller data).
8. Only after isolated-rotor performance is established and reported honestly, revisit the
   wing-installed configuration question.

---

## 9. Engineering Lessons

**First-principles design vs. assumed geometry.** Treating blade count and sweep as *outputs* of
governing constraints (a solidity/aspect-ratio trade; a leading-edge-normal Mach cap),
rather than inputs chosen to resemble a reference design, produced a design defensible on its
own terms — including the ability to state precisely *why* it resembles a historical reference
(SR-3) without that resemblance being circular.

**Compressibility and tip-Mach constraints.** Reporting only rotational tip Mach — the more
commonly quoted figure — would have concealed the actual (supersonic, helical) compressibility
environment the tip experiences. Carrying both quantities separately, and never conflating them,
was essential to getting the sweep requirement right at all.

**CAD verification.** A geometry check's return code (`Check2`) is not self-interpreting;
without cross-comparing it against a known-clean body, its apparent failure would have been
attributed to the wrong cause. Independent, separate-process re-verification (not trusting
build-time self-checks) caught what an in-process check alone would have missed.

**Periodic CFD setup.** Boundary zones produced by automatic separation must be verified against
independently-known geometry, not trusted by name or by console message alone — the periodic
pairing claim here rests on a direct, independent read of the saved mesh file's own topology,
not on Fluent's reported success.

**Engineering claim discipline.** The single habit most responsible for this project remaining
defensible under scrutiny was maintaining, throughout, an explicit distinction between what is
*derived*, what is *assumed*, what is *verified*, and what is *[CFD-TBD]* — applied consistently
enough that this report could be written without discovering, while writing it, that an earlier
claim had quietly drifted ahead of its evidence.

---

## 10. Conclusion

This project has produced an internally self-consistent, first-principles aerodynamic design for
a swept open-fan rotor; realized that design as independently-verified parametric CAD, including
a documented recovery from a genuine construction failure; and constructed and independently
verified the CFD fluid domain and boundary/periodic topology required for an isolated-rotor CFD
study. Every claim above traces to a specific saved artifact and a stated verification method
(see `EVIDENCE_INDEX.md`). Volume meshing, solver execution, results, validation, and
installation analysis are the explicit, unstarted next stages of this work — not implied,
approximated, or partially claimed anywhere in this report.
