# PHYSICS AND METRICS MAP
### BA-OF-01 — geometry → flow physics → measurable quantity → engineering interpretation

**Created:** 22 August 2026 · **Phase:** 0
**Purpose:** establish, before any simulation exists, exactly which quantities the project will
report and why — so that no metric can be selected after the fact to flatter a result.

---

## 1. THE CHAIN

Read left to right. Every row is a complete argument from a geometric decision to an engineering
conclusion. If a row cannot be completed, the geometry decision behind it has no justification.

| Geometry decision | Flow physics it controls | Measurable quantity | Engineering interpretation |
|---|---|---|---|
| **Rotor diameter `D`** | Swept area → mass flow → induced velocity for a given thrust | `T/A`, `η_p` | The entire open-fan argument. Larger `D` lowers `T/A`, lowers `Δv`, raises the `η_p` ceiling |
| **Shaft speed / tip speed** | Rotational Mach; combined with `M₀` gives helical tip Mach | `M_hel(r)`, tip-region `Cp`, shock location | The binding constraint. Above `M_hel ≈ 1`, tip shocks form and efficiency falls |
| **Blade count `B`** | Solidity → per-blade loading → blade circulation | `σ(r)`, `dT/dr`, blade `Cp` | More blades spread the load, easing tip Mach and stall margin, at a solidity/weight cost |
| **Radial twist `β(r)`** | Local incidence at each radius given the local velocity triangle | Local `α(r)`, `dT/dr`, `dQ/dr` | Twist exists to hold each section near its design incidence as `U = ωr` varies. Wrong twist → root stall or tip unloading |
| **Chord `c(r)`** | Local blade loading and Reynolds number | `dT/dr`, sectional `Cl`, `Re(r)` | Chord distributes the loading radially; it is the designer's control over *where* thrust is produced |
| **Thickness `t/c (r)`** | Sectional critical Mach and drag rise | Tip `Cp`, shock strength | Thin at the tip because `M_hel` is highest there; thick at the root for structure where Mach is low |
| **Sweep `Λ(r)`** | Mach component normal to the leading edge, `M_n ≈ M_hel·cos Λ` | Tip `Cp`, shock presence/absence | The mechanism that makes supersonic helical tip Mach survivable. Not styling |
| **Spinner / hub geometry** | Root boundary condition, hub blockage, root flow turning | Hub-region streamlines, root `dT/dr` | Prevents an unphysical root and sets where useful thrust begins |
| *(Stage 3)* **Rotor–wing axial and vertical offset** | Slipstream development length before the wing; wing upstream potential field at the disk | Circumferential inflow variation; wing spanwise loading | Controls both M1 (inflow non-uniformity) and M2 (slipstream on wing) |
| *(Stage 3)* **Wing section and incidence** | Wing loading, and hence the strength of its upstream influence | `Cl(y)`, `Cd(y)`, `q_scrub/q_∞` | Determines how much the wing perturbs the rotor and how much the slipstream perturbs the wing |

---

## 2. METRIC RANKING

Every candidate metric is ranked **Primary / Secondary / Diagnostic / Rejected**. A rejected metric
carries a reason. Metrics may not be promoted after results are seen.

### 2.1 PRIMARY — the project reports these, and stands or falls on them

| Metric | Definition | Why primary | How measured |
|---|---|---|---|
| **Net axial force (thrust) `T`** | Axial component of pressure + viscous force on all rotor surfaces | The output of a propulsor; the quantity the design targeted | Surface force integral over blades + spinner |
| **Shaft torque `Q`** and power `P = Qω` | Moment about the shaft axis | The input. Without it, efficiency is undefined | Moment integral about the axis |
| **Propulsive efficiency `η_p = T·V₀ / (Qω)`** | Useful propulsive power / shaft power | The single number that expresses the open-fan argument | Derived from `T` and `Q` |
| **Radial thrust distribution `dT/dr`** | Sectional axial force per unit span | The direct test of whether the BEM design intent was realised in 3-D. **This is the metric that makes the project a design study rather than a black box** | Radial binning of blade surface forces |
| **Helical Mach distribution `M_hel(r)`** | `√(M₀² + (ωr/a)²)` | The controlling constraint; must be reported to justify sweep | Geometric + flow field |
| *(Stage 3)* **Installed − isolated delta** | `ΔT`, `Δη_p` between CFG-INST and CFG-ISO | The primary research question | Difference of two controlled runs |

### 2.2 SECONDARY — reported, supporting, but not load-bearing

| Metric | Definition | Role |
|---|---|---|
| `C_T = T/(ρn²D⁴)` | Non-dimensional thrust | The language of published propeller data; required for any benchmark comparison |
| `C_P = P/(ρn³D⁵)` | Non-dimensional power | As above |
| `J = V₀/(nD)` | Advance ratio | The operating-point parameter for a sweep |
| Radial torque `dQ/dr` | Sectional torque | Pairs with `dT/dr` to give sectional efficiency |
| Blade surface `Cp` at hub / mid / tip | Pressure coefficient | Shows shock presence and loading shape; the direct link to sectional aerodynamics |
| *(Stage 3)* Wing spanwise `Cl(y)`, `Cd(y)` | Sectional wing loading | Measures M2 (slipstream on wing) |
| *(Stage 3)* Interference force | `F_INST − (F_ISO + F_WING)` | Measures M5 (non-linearity) |
| *(Stage 3)* `q_scrub/q_∞` | Slipstream dynamic-pressure ratio at the wing | Measures M3 (scrubbing) |
| *(Stage 3)* Circumferential inflow variation at the disk | `V_x(θ)` at the rotor plane | Measures M1 (inflow non-uniformity) |

### 2.3 DIAGNOSTIC — used to understand and to check, not to headline

Slipstream contraction ratio · wake total-pressure deficit · tip-vortex trajectory and strength ·
swirl angle and residual swirl kinetic energy · separation extent and location · `y⁺` distribution ·
mesh skewness and orthogonal quality · residual histories · mass-flow and momentum conservation
checks · sectional `Re(r)`.

**These may appear in figures. They may not appear in a conclusion or a resume line.**

### 2.4 REJECTED — with reasons

| Rejected metric | Why rejected |
|---|---|
| **Swirl recovery efficiency / swirl-recovery gain** | **The specifically-required evaluation.** See §3 below — a full treatment, because this was deliberately considered and rejected |
| Any sound pressure level, EPNdB, tone level, OASPL | No acoustic model exists. Reporting any acoustic quantity would be fabrication |
| Fuel burn, SFC, block fuel, CO₂ | Requires an engine cycle and a mission model, both excluded |
| Bypass ratio (including "effective BPR") | Meaningful only for a full engine with a defined core flow. Quoting an effective BPR for a bare rotor would be a category error |
| Thrust specific fuel consumption | No cycle model |
| Blade stress, natural frequency, flutter margin, 1P load | No structural solver; excluded discipline |
| Figure of Merit (FoM) | A **hover** metric. This rotor operates at `J ≈ 3`. Using a hover figure of merit in axial flight is a known misuse and is exactly the error the "Universal Method for Comparing Open Rotors and Ducted Fans in Hover" literature warns about |
| Isentropic / polytropic efficiency | Turbomachinery stage metrics that presuppose a defined inlet and exit annulus. An unducted rotor has neither |
| Fan pressure ratio | Requires a duct to define the stations |
| Lift-to-drag ratio of the *aircraft* | No aircraft exists in this project |
| Any ducted-fan comparison metric | The ducted comparison is permanently excluded (parent research, C1) |
| Wall `y⁺` **as a result** | It is a mesh-quality diagnostic, never an outcome |

---

## 3. SWIRL RECOVERY — REQUIRED EXPLICIT EVALUATION

Swirl recovery was raised in the parent research and deliberately rejected as the central metric.
Because that rejection was a real decision, it is re-evaluated here inside the metrics framework
rather than simply inherited.

**What it is.** A rotor delivers work partly as axial momentum (useful thrust) and partly as
tangential momentum (swirl). Swirl kinetic energy left in the slipstream is work the shaft supplied
that produced no thrust. A downstream stationary row (OGV / swirl-recovery vane) can turn some
tangential momentum back into axial momentum.

**Evidence on magnitude** (TU Delft body of work, from the parent research):

| Study result | Gain |
|---|---|
| Two optimised SRV designs, cruise | **+0.39 %**, **+0.20 %** |
| Same designs, high-thrust condition | **+2.62 %**, **+3.07 %** |
| Separate study, measured, 48 % near-wake swirl reduction | **+2.4 %** |
| Another design, predicted | **+0.7 %** |
| Acoustic penalty | **+20 dB** in the axial direction |

**Evaluation against this project's criteria:**

| Criterion | Verdict |
|---|---|
| Is it physically real? | **Yes.** Not disputed |
| Is it first-order? | **No.** 0.2–3 % — smaller than the installation effects the project is about |
| Does the literature agree on a value? | **No.** The spread is an order of magnitude. Quoting any single number would misrepresent the field |
| Can this project measure it credibly? | Only by adding an OGV row — doubling CFD cost and adding a full second design task |
| Does it come bundled with something we cannot model? | **Yes** — a large acoustic penalty, and acoustics is excluded |
| Would it improve the answer to the research question? | **No.** The question is about installation, not swirl |

**Decision (ED-008): REJECTED as a metric and as a component.**

**But retained in one specific role:** residual **swirl angle** and **swirl kinetic energy** in the
slipstream are kept as **Diagnostic** quantities (§2.3), because:
1. they quantify the loss the rotor-only architecture accepts, which is part of honestly describing
   what the baseline is;
2. the swirling slipstream is the *cause* of mechanism M2 — the up-going/down-going asymmetry in
   wing loading — so swirl must be measured to explain the installed result even though recovering
   it is out of scope.

This is the defensible position: **measure the swirl, explain what it does, do not build a vane to
recover it, and do not claim a recovery benefit.**

---

## 4. THRUST–DRAG BOOKKEEPING CONVENTION (Stage 3, declared now)

An open rotor has no nacelle, so there is **no natural surface** dividing thrust from drag. The
convention below is **declared in advance** and must be stated wherever an installed number appears.

**Convention BK-1 (adopted):**
- **Thrust** = axial force on **rotating surfaces only** (blades + spinner).
- **Drag** = axial force on **all non-rotating surfaces** (wing, pylon/support).
- **Net propulsive force** `NPF = T_rotating − D_stationary`.
- Scrubbing drag therefore appears on the **airframe** side, not as a thrust debit.

**Why this convention:** it maps onto a physically identifiable surface (what rotates), so it is
unambiguous and reproducible by a third party. It matches how installed open-rotor systems studies
charge scrubbing to the airframe.

**Its weakness, stated up front:** it flatters the propulsor. A rotor whose slipstream badly
scrubs the wing shows no thrust penalty under BK-1 — the penalty lands entirely on the airframe.

**Required mitigation:** report `NPF` — never `T` alone — for the installed case, and additionally
report the result under one alternative convention (**BK-2**: control-volume momentum balance around
the propulsor streamtube) as a **sensitivity**. If the sign of the conclusion changes between BK-1
and BK-2, that fact is itself the headline finding and must be reported as such.

---

## 5. WHAT WOULD FALSIFY THE PROJECT'S CONCLUSIONS

Stated in advance, so the project is falsifiable rather than merely descriptive:

| Finding | Consequence |
|---|---|
| CFD thrust departs from BEM design intent by more than the declared band | The design method, not the CFD, is under suspicion — investigate BEM assumptions (tip loss, compressibility correction) before touching the mesh |
| Thrust and torque have not converged between the two finest meshes | **No performance number may be reported.** Report as not mesh-independent |
| Benchmark case misses published data outside the declared band | Method verification **fails**; report it and do not proceed to claim isolated performance as trustworthy |
| Installed delta is smaller than mesh-convergence uncertainty | **The result is null and must be reported as null** — the effect is below the resolution of the method |
| Conclusion sign flips between bookkeeping conventions BK-1 and BK-2 | The bookkeeping, not the aerodynamics, is driving the answer — report prominently |
