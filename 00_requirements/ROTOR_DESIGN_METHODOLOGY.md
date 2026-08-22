# ROTOR DESIGN METHODOLOGY
### BA-OF-01 — how the blade will be designed, decided before any blade exists

**Created:** 22 August 2026 · **Phase:** 0 · **Decision:** ED-004

**Governing constraint on this choice:** the method must be one the author can **derive and explain
on a whiteboard**. A method that produces a better blade but cannot be defended is worse than a
method that produces a defensible blade.

---

## 1. OPTIONS EVALUATED

| Option | Method | Verdict |
|---|---|---|
| **A** | Actuator-disk / simple momentum sizing, then ad-hoc blade shaping | **Insufficient alone** — actuator-disk theory has no blade in it. It gives the ideal ceiling and the required area, but cannot produce chord or twist. **Retained as the sizing step only** |
| **B** | Classical blade-element momentum theory, no corrections | **Insufficient** — without Prandtl tip loss, BEM over-predicts tip thrust badly, exactly where this rotor is most loaded and most Mach-critical. Would corrupt the primary metric `dT/dr` |
| **C** | **BEM with practical corrections** (Prandtl tip and hub loss; compressibility correction), using the **Adkins–Liebeck minimum-induced-loss** design formulation | **SELECTED** |
| **D** | Lifting-line / vortex-lattice, or CFD-in-the-loop inverse design | **Rejected** — heavier, slower, and for a single design point it buys accuracy the project cannot validate anyway. CFD-in-the-loop would also make the CFD a *design* tool, destroying its role as an *independent check* |

### Why C, specifically

1. **Adkins & Liebeck (1983), "Design of Optimum Propellers"** is a published, closed-form,
   textbook-level formulation of Betz minimum-induced-loss propeller design. Every equation is
   derivable. It is not a black box and not somebody's code.
2. It produces **chord and twist simultaneously** from a physically-motivated optimality condition,
   rather than from an arbitrary prescription.
3. Prandtl tip/hub loss is a closed-form correction with a clear physical meaning (finite blade
   number ⇒ the disk is not a uniform actuator).
4. It is cheap — the whole design runs in seconds in Python, so the design space can be explored
   analytically before any mesh exists.
5. **It has a known, statable weakness at the transonic tip** (§6), which makes the subsequent CFD a
   genuine test rather than a formality.

---

## 2. REQUIRED INPUTS

| Input | Source | Status |
|---|---|---|
| Flight speed `V₀`, density `ρ`, speed of sound `a` | Design point (ISA at altitude) | CALCULATED |
| Rotational speed `Ω` | Design point, set by the tip-Mach constraint | PROVISIONAL |
| Radius `R`, hub radius `R_hub` | Design point | PROVISIONAL / TBD |
| Blade count `B` | Solidity outcome — **set by this method, not assumed** | TBD |
| Design thrust `T` (or design power) | Design point | TBD |
| Sectional `Cl(α, M, Re)` and `Cd(α, M, Re)` | Airfoil family — see §5 | TBD |
| Design sectional lift coefficient `Cl_des(r)` | Design choice, at or near max `L/D` | DESIGN DECISION |

---

## 3. EQUATIONS

### 3.1 Actuator-disk sizing (the pre-step)

```
A          = π R²
η_p,ideal  = 2 / (1 + √(1 + 2T/(ρ A V₀²)))
V_j        = V₀ (2/η_p,ideal − 1)
v_i        = (V_j − V₀)/2
ṁ          = ρ A (V₀ + v_i)
T_check    = ṁ · 2 v_i          ← must reproduce the input T
```

This fixes the **ceiling** the blade design may approach but never exceed, and gives the induced
velocity scale the BEM solution must be consistent with. **Gate G0** checks closure.

### 3.2 Local velocity triangle at radius `r`

With `a` the axial induction factor and `a'` the tangential induction factor, and `φ` measured from
the **rotor plane**:

```
V_a = V₀ (1 + a)                axial velocity at the disk
V_t = Ω r (1 − a')              tangential velocity seen by the blade
W   = √(V_a² + V_t²)            relative velocity magnitude
tan φ = V_a / V_t               inflow angle
α   = β − φ                     local incidence
β   = φ + α                     ⇒ blade (pitch) angle — this is the twist definition
```

**This triangle is the heart of the project.** It must be drawable at hub, mid-span and tip, and it
explains why twist is non-linear: `V_t = Ωr` grows linearly with radius while `V_a` barely changes,
so `φ` falls steeply toward the tip.

### 3.3 Blade-element forces (propeller sign convention)

```
σ(r)   = B c(r) / (2π r)                                   local solidity
dT/dr  = ½ ρ W² B c (Cl cos φ − Cd sin φ)
dQ/dr  = ½ ρ W² B c (Cl sin φ + Cd cos φ) · r
```

### 3.4 Momentum side, with Prandtl loss factor `F`

```
dT/dr  = 4π r ρ V₀² (1 + a) a  · F
dQ/dr  = 4π r³ ρ V₀ (1 + a) a' Ω · F
```

### 3.5 Prandtl tip and hub loss

```
f_tip = (B/2)·(R − r)/(r sin φ)        F_tip = (2/π) arccos( e^(−f_tip) )
f_hub = (B/2)·(r − R_hub)/(R_hub sin φ) F_hub = (2/π) arccos( e^(−f_hub) )
F     = F_tip · F_hub
```

`F → 0` at the tip, correctly driving the loading to zero there. **Without this the design is
wrong in exactly the region that matters most.**

### 3.6 Compressibility correction

```
M_rel(r) = W(r) / a                       local relative Mach
M_n(r)   = M_rel(r) · cos Λ(r)            leading-edge-normal Mach with sweep Λ
Cl_comp  = Cl_inc / √(1 − M_n²)           Prandtl–Glauert
```

**Validity is limited to `M_n ≲ 0.7`.** See §6 — this is the method's principal weakness and it is
not hidden.

### 3.7 Closure

`a` and `a'` are obtained by equating the blade-element and momentum expressions at each radius and
iterating to convergence. Chord follows from the required loading once `Cl_des` is prescribed:

```
c(r) = (dT/dr)_target / [ ½ ρ W² B (Cl_des cos φ − Cd sin φ) ]
```

---

## 4. RADIAL DISCRETISATION

- **Stations:** 30–50 from `r/R = R_hub/R` to 1.0, **cosine-clustered toward the tip**, because
  loading gradients and `F` vary most sharply there.
- **Convergence:** `|Δa|`, `|Δa'| < 1e-6` per station.
- **Independence check:** re-run at 2× station count; integrated `T` and `Q` must change by <0.1 %.
  This is the analytical analogue of a mesh-independence study and is a required Phase 1 artifact.

---

## 5. AIRFOIL SECTIONS

**Requirement:** sectional `Cl` and `Cd` as functions of `α`, local Mach and local Reynolds number,
for a family with a **high critical Mach number** — because this blade is Mach-limited, not
lift-limited.

**Candidate family: NACA 16-series** — the classical propeller section family, designed specifically
for high critical Mach, with published data. **Status: TBD** pending confirmation of usable polar
data across the required Mach range.

**Radial thickness policy (design decision, not assumption):**
- thick at the root (structure, low local Mach),
- thin at the tip (`M_hel` is highest there),
- thickness varied monotonically and reported as `t/c (r)`.

**Honest limitation:** whatever family is chosen, published 2-D section data will not cover the
transonic tip conditions of this rotor. See §6.

---

## 6. THE METHOD'S KNOWN LIMITATIONS — STATED BEFORE USE

| # | Limitation | Consequence | How the project handles it |
|---|---|---|---|
| **L1** | **BEM sectional aerodynamics is invalid at the transonic tip.** At the design point `M_hel,tip ≈ 1.10`; Prandtl–Glauert fails well below this | The tip region of the BEM design is the **least trustworthy** part of the blade | This is precisely what the 3-D CFD tests. A CFD/BEM disagreement at the tip is an **expected finding**, not a bug |
| **L2** | **BEM cannot design sweep.** It is a strip theory with no spanwise geometric awareness | Sweep must come from elsewhere | Sweep is layered on as a **separate, explicitly justified geometric decision** driven by the `M_hel(r)` distribution: choose `Λ(r)` so `M_n = M_hel cos Λ` stays below a declared limit. It is **verified** by CFD, not designed by BEM |
| **L3** | **No radial equilibrium.** Strip theory assumes radially independent streamtubes | Real spanwise pressure gradients and radial flow migration are absent | CFD `dT/dr` vs BEM `dT/dr` is the direct measurement of this error — a **primary metric** |
| **L4** | **No 3-D tip-vortex physics** beyond the Prandtl correction | Tip loading approximate | Same as L3 |
| **L5** | **Minimum-induced-loss is an *induced* optimum only** — it does not minimise profile or wave drag | "Optimum" in the Adkins–Liebeck sense ≠ optimal blade | **The word "optimised" is forbidden** (requirements Tier 3). The blade is "designed by a minimum-induced-loss formulation", nothing more |
| **L6** | **Single design point.** No off-design shaping | Off-design behaviour is an outcome, not a design intent | The `J`/tip-Mach sweep reports off-design behaviour honestly |
| **L7** | **Reynolds number** at full scale is high; section data may not extend there | Sectional `Cd` uncertainty | Report `Re(r)`; treat `Cd` as an acknowledged uncertainty in `Q`, hence in `η_p` |

---

## 7. WHAT THIS METHOD OUTPUTS

A machine-readable radial table — the **single source of truth** for all downstream geometry:

```
r/R , chord c(r) , blade angle β(r) , thickness t/c(r) , sweep Λ(r) ,
      Cl_des(r) , M_rel(r) , M_hel(r) , M_n(r) , Re(r) ,
      a(r) , a'(r) , F(r) , dT/dr , dQ/dr
```

plus integrated `T`, `Q`, `P`, `η_p`, `C_T`, `C_P`, `J`, and the G0 closure check.

**No CAD dimension may be typed by hand.** Every geometric feature in SolidWorks must trace to a row
of this table. That is what makes "designed from first principles" a Tier-1 claim rather than a
slogan.

---

## 8. INTERVIEW OBLIGATIONS CREATED BY THIS CHOICE

Selecting this method commits the author to being able to:

1. Derive the local velocity triangle and explain each term.
2. Explain why twist is non-linear from `tan φ = V_a/V_t`.
3. State what `a` and `a'` physically are, and why `a' ≠ 0`.
4. Explain what Prandtl tip loss corrects and why `F → 0` at the tip.
5. State the Betz minimum-induced-loss condition and what it does **not** optimise.
6. Explain why Prandtl–Glauert fails at this rotor's tip, and what is done about it.
7. Explain why sweep is not, and cannot be, an output of BEM.
8. Say what a CFD-vs-BEM `dT/dr` disagreement would mean and where to look first.

**If any of these cannot be answered, Phase 1 is not complete regardless of what the code produced.**
