# CFD SETUP SPECIFICATION — ISOLATED OPEN-FAN ROTOR
### BA-OF-01 · CFG-ISO · ANSYS Fluent 2025 R1

**Created:** 22 August 2026 · **Phase:** 3/4 preparation
**Status:** SPECIFICATION — written and frozen **before** the production mesh is generated,
as required by the Phase 1 authorisation (item E).

**Solver:** ANSYS Fluent 2025 R1 — `D:\ANSYS Inc\v251\fluent\ntbin\win64\fluent.exe`
**Platform:** AMD Ryzen 7 6800H, 8 physical cores, **15.2 GB RAM** (measured 22 Aug 2026)

**Evidence labels:** `[REQUIREMENT]` `[PUBLISHED INPUT]` `[DESIGN DECISION]` `[DERIVED]`
`[ASSUMPTION]` `[CFD-TBD]`

---

## 1. WHAT THIS CASE IS FOR

To measure the Phase 1 rotor and test whether the 3-D compressible flow reproduces the 1-D
blade-element design intent. It is **not** an installed case, and no installed quantity may be
inferred from it.

**The primary question this case answers:** does the designed rotor produce the thrust, torque and
**radial loading distribution** that BEM predicted, and where does 3-D reality depart from strip
theory?

---

## 2. GEOMETRY AND DOMAIN

### 2.1 Rotor (from Phase 1 — no value typed by hand)

| Quantity | Value | Source |
|---|---|---|
| Blades `B` | **16** | `[DERIVED]` Phase 1 blade-count trade |
| Diameter `D` | 3.5 m | `[DESIGN DECISION]` |
| Hub radius | 0.49 m (hub/tip 0.28) | `[DESIGN DECISION]` |
| CAD blade span | r/R 0.32 → 0.985 | `[DESIGN DECISION]` |
| Tip sweep | 44.2° | `[DERIVED]` from the helical-Mach field |

### 2.2 Periodic sector — **22.5°**

`[DERIVED]` 360°/16. The isolated configuration is axisymmetric, so a single-blade sector with
rotational periodicity is **exact, not an approximation**. It reduces cell count by a factor of 16.

> **Note on the change from Phase 0:** the Phase 0 audit assumed a 30° sector (B = 12 placeholder).
> Phase 1 selected B = 16, so the sector is 22.5° and the cell count falls by ~25 %.

**Verification required:** one full-annulus run must reproduce the sector result before the sector
is trusted. `[REQUIREMENT]` Phase 4.

### 2.3 Domain extent `[DESIGN DECISION]`, to be confirmed by sensitivity study

| Boundary | Distance | Rationale |
|---|---|---|
| Upstream inlet | 8 `D` = 28 m | far enough that the rotor's upstream influence has decayed |
| Radial far field | 8 `D` = 28 m | contains the streamtube contraction |
| Downstream outlet | 15 `D` = 52.5 m | lets the slipstream develop without outlet reflection |

**Gate:** move each boundary out by 50 %; thrust must change < 1 %. If it does not, the domain is
too small and must be enlarged. `[REQUIREMENT]`

---

## 3. REFERENCE FRAME — decision and its consequences

| | |
|---|---|
| **Decision** | **Single rotating reference frame (SRF)** over the entire sector domain |
| **Why not MRF** | MRF exists to couple rotating and stationary zones. In the *isolated* case there is no stationary body — the whole domain can rotate with the blade. SRF is therefore **simpler and exact** here |
| **Why not sliding mesh** | Sliding mesh is inherently transient; §4 selects steady |
| **Captures** | Coriolis and centrifugal source terms; the correct relative-frame flow field |
| **Misses** | Nothing, for this configuration — the isolated rotor in uniform axial inflow is genuinely steady in the rotating frame |
| **Rotational speed** | ω = 135.5 rad/s (**1294 rpm**) about +Z `[DERIVED]` |

> **This is the one place in the project where the cheap method is also the exact one.** It will not
> be true for the installed case, where MRF becomes a declared approximation.

---

## 4. TIME TREATMENT

**Steady RANS.** `[DESIGN DECISION]`

For an isolated rotor in uniform axial inflow, the flow is steady in the rotating frame — this is
**exact**, not an approximation. Unsteadiness (blade passing, wake interaction, 1P loading) requires
a second body to exist, and there is none in CFG-ISO.

**Not run:** URANS, LES, DES. Excluded by the project scope, and unnecessary here.

---

## 5. COMPRESSIBLE FORMULATION — mandatory

| Setting | Choice | Reason |
|---|---|---|
| Density | **Ideal gas** | `M_hel,tip` = **1.0966** — the tip is **supersonic in the relative frame** |
| Energy equation | **ON** | required with ideal gas |
| Viscosity | **Sutherland** | consistent with the design model |
| Solver | **Pressure-based coupled** | robust through transonic; density-based is the fallback if tip shocks resist convergence |
| Discretisation | **2nd order upwind** on momentum, energy, turbulence; 2nd order pressure | 1st order is start-up only and **no result may be reported from it** `[REQUIREMENT]` |
| Gradient | Least-squares cell-based | |

**A pressure-based incompressible solve would be physically meaningless for this rotor** and is
forbidden.

---

## 6. TURBULENCE MODEL

| | |
|---|---|
| **Baseline** | **k-ω SST** `[DESIGN DECISION]` |
| **Why** | Adverse-pressure-gradient and separation behaviour; robust automatic wall treatment; the de-facto standard for transonic external and turbomachinery flow, so results are comparable with the literature |
| **Sensitivity closure** | **Spalart–Allmaras** — a genuinely different formulation, not an SST variant |
| **Transition** | **None — fully turbulent** `[ASSUMPTION]`. Chord Reynolds number is 0.6–2.2 × 10⁶, so a real blade would have some laminar run. Assuming fully turbulent **over-predicts drag and therefore under-predicts efficiency** — a conservative bias, and it is stated rather than hidden |
| **Known weaknesses to state up front** | Linear eddy-viscosity models under-predict streamline-curvature and rotation effects, and are **over-diffusive in vortex cores** — the tip vortex will decay too quickly |

The two-closure spread is **reported as model-form uncertainty**. It is never averaged, and the
more favourable closure is never selected after the fact. `[REQUIREMENT]`

---

## 7. WALL TREATMENT AND `y⁺`

**Target: `y⁺` ≈ 1, wall-resolved.** `[DESIGN DECISION]`

**Why it matters here specifically:** torque carries a large viscous component and
`η_p = T·V₀/(Q·ω)` **divides by torque**. Wall-shear error propagates directly into the headline
efficiency number.

### First-cell height, computed not guessed `[DERIVED]`

At mid-span (r/R ≈ 0.70), using the Phase 1 design values:

```
W      ≈ 290 m/s        relative velocity
c      ≈ 0.25 m         chord
rho    = 0.3795 kg/m^3  ISA 35 000 ft
mu     = 1.4334e-5 Pa s Sutherland

Re_c   = rho*W*c/mu                     = 1.92e6
Cf     = 0.026 / Re_c^(1/7)             = 3.29e-3
tau_w  = 0.5*rho*W^2*Cf                 = 52.5 Pa
u_tau  = sqrt(tau_w/rho)                = 11.8 m/s
y1     = y+ * mu / (rho * u_tau)        = 3.2e-6 m   for y+ = 1
delta  ~ 0.37*c/Re_c^0.2                = 5.1e-3 m
```

**Prism layer stack:** first cell **3.2 µm**, growth rate **1.2**, **≈32 layers** to contain the
5.1 mm boundary layer. `[DERIVED]`

**Required evidence:** a `y⁺` **map over the whole blade**, reported for every case — never a single
asserted value. `[REQUIREMENT]`

---

## 8. MESH STRATEGY

| Element | Approach |
|---|---|
| Topology | Poly-hexcore (Fluent Mosaic); hex-dominant fallback if convergence is poor |
| Blade surface | Curvature + proximity sizing; clustering at LE, TE and tip |
| Boundary layer | Per §7: 3.2 µm first cell, growth 1.2, ~32 layers |
| Refinement zone 1 | **Outer 20 % span** — the transonic tip shock |
| Refinement zone 2 | **Tip-vortex path**, a helical region trailing the tip |
| Refinement zone 3 | **Slipstream cylinder** to the outlet |
| Quality gates | max skewness < 0.85; min orthogonal quality > 0.15 — **reported for every mesh** |

### Mesh-independence triplet — RAM-capped

| Mesh | Cells | Memory estimate |
|---|---|---|
| Coarse | ~0.9 M | ~2 GB |
| Medium | ~2.0 M | ~4 GB |
| Fine | **~4.3 M** | ~8–9 GB |

Constant linear refinement ratio **r ≈ 1.30** — the minimum for a meaningful GCI.

> **The fine mesh is capped by the machine, not chosen for convenience.** With 15.2 GB total RAM and
> ~12 GB usable, ~5 M cells is the practical ceiling. The 6.5–8.5 M mesh assumed before the hardware
> was measured has been **withdrawn**. Reported honestly rather than quietly attempted and abandoned.

---

## 9. BOUNDARY CONDITIONS

| Boundary | Type | Value |
|---|---|---|
| Inlet / radial far field | **Pressure far-field** | M = 0.75, p = 23 834 Pa, T = 218.8 K, axial direction `[DERIVED]` |
| Outlet | **Pressure outlet** | p = 23 834 Pa, radial equilibrium ON |
| Blade, spinner | **No-slip, adiabatic**, moving with the rotating frame |
| Sector sides | **Rotational periodicity** about +Z, 22.5° |
| Turbulence inlet | I = 0.1 %, µt/µ = 5 `[ASSUMPTION]` — free-stream cruise values |

**Operating pressure:** 0 Pa, with absolute pressures specified — standard practice for compressible
external flow, avoids round-off in the pressure field.

---

## 10. CONVERGENCE CRITERIA

Convergence is **not** "residuals dropped". Both conditions must hold: `[REQUIREMENT]`

1. **Scaled residuals ≥ 4 orders** below their initial value, continuity included.
2. **Integrated-quantity stationarity** — thrust and torque flat within **±0.1 %** over the final
   **500 iterations**, monitored live.

**Additional physical checks, all mandatory:**

| Check | Criterion |
|---|---|
| Mass imbalance inlet vs outlet | < 0.1 % |
| Axial momentum balance over a control volume vs integrated surface force | < 2 % |
| Thrust ≤ actuator-disk ideal ceiling | must hold — a violation means a bookkeeping or frame error |

A case that meets the residual criterion but not the stationarity criterion is **not converged** and
its numbers may not be reported.

---

## 11. FORCE, TORQUE AND PERFORMANCE EXTRACTION

### 11.1 What is integrated

| Quantity | Method | Surfaces |
|---|---|---|
| **Thrust `T`** | Force report, **axial (Z)** component, pressure + viscous separately | blade + spinner, ×16 for the full rotor |
| **Torque `Q`** | Moment report about the **Z axis** through the origin | same surfaces |
| **Power** | `P = Q·ω` | — |

**Pressure and viscous contributions are reported separately.** `[REQUIREMENT]` The viscous share of
torque is the part most exposed to the `y⁺` and turbulence-model choices, so it must be visible.

### 11.2 Sector-to-full-rotor scaling

The sector carries one blade. Full-rotor `T` and `Q` = sector values × 16. `[DERIVED]`
Valid **only** because the configuration is axisymmetric.

### 11.3 Derived performance

```
eta_p = T*V0 / (Q*omega)
C_T   = T / (rho * n^2 * D^4)          n = 21.57 rev/s
C_P   = P / (rho * n^3 * D^5)
J     = V0 / (n*D) = 2.945
```

Cross-check: `C_T·J/C_P` must equal `η_p`. `[REQUIREMENT]`

### 11.4 Radial loading — the metric that makes this a design study

`dT/dr` and `dQ/dr` extracted by **binning blade surface forces into radial bands**, then compared
directly against the Phase 1 BEM prediction.

> **This is the single most important output of CFG-ISO.** It is the direct measurement of strip
> theory's error, and the tip is where it is expected to fail — the BEM design there uses sectional
> aerodynamics outside Prandtl–Glauert validity. **A disagreement at the tip is a predicted finding,
> not a bug.** Gate G4 sends the investigation to the BEM first, not to the mesh.

### 11.5 Diagnostics

Blade `Cp` at r/R = 0.35, 0.70, 0.98 · shock location on the outer span · slipstream swirl angle and
total-pressure survey at 0.5 `D` and 1 `D` downstream · tip-vortex trajectory · `y⁺` map ·
separation extent.

---

## 12. WHAT THIS CASE CANNOT DELIVER

| Cannot deliver | Because |
|---|---|
| Any acoustic quantity | No acoustic model — excluded from the project |
| Installed performance | No airframe present |
| Blade-passing or 1P unsteadiness | Steady formulation, single isolated rotor |
| Transition location | Fully turbulent assumption |
| Far-field tip-vortex persistence | Linear eddy-viscosity models are over-diffusive in vortex cores |
| Structural or aeroelastic response | No structural solver |

---

## 13. RUN ORDER

| # | Case | Purpose | Est. wall-clock |
|---|---|---|---|
| 0 | **Timing calibration**, coarse, 200 iterations | replace every runtime estimate with a measurement | ~30 min |
| 1 | Coarse (0.9 M), SST, design point | first result; start-up robustness | 1–3 h |
| 2 | Medium (2.0 M), SST | the reference case | 3–6 h |
| 3 | Fine (4.3 M), SST | mesh independence, gate G2 | 6–12 h |
| 4 | Medium, Spalart–Allmaras | model-form uncertainty | 3–6 h |
| 5 | Medium, enlarged domain | domain sensitivity | 3–6 h |
| 6 | Full annulus, coarse | periodicity verification | 6–12 h |

**Run 0 is a hard gate.** No case beyond it may be launched against an estimate rather than a
measurement. `[REQUIREMENT]`

**Preliminary Day-1 run:** a coarser, wall-function case may be run to prove the workflow end to
end. It is labelled **PRELIMINARY**, it is **not** mesh-independent, and it grounds **no**
performance claim.
