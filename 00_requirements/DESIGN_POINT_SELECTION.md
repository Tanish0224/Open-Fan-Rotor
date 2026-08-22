# DESIGN POINT SELECTION
### BA-OF-01 — every design parameter, with its evidence

**Created:** 22 August 2026 · **Phase:** 0 · **Decision:** ED-009

**Rule enforced throughout:** no parameter is chosen because it "sounds realistic". Each is either
traced to a source, calculated from other parameters, or explicitly marked **TBD — REQUIRES EVIDENCE
BEFORE FREEZING**. Plausible-looking numbers are not inserted to fill gaps.

---

## 1. THE FOUR CONSTRAINTS THAT ACTUALLY SET THE DESIGN POINT

Before any individual number, the logic that generates them:

1. **Flight Mach must be representative of open-fan cruise.** Below ~M0.7 the architecture stops
   being interesting (it becomes a turboprop); above ~M0.85 it is outside the stated operating range.
2. **Rotational tip Mach is capped by noise and compressibility**, not by structure. This is the
   binding constraint of the whole architecture.
3. **Diameter is capped by installation** (ground clearance, wing height) — the reason CFM reduced
   RISE's fan diameter to fit single-aisle aircraft.
4. **Disk loading follows** from thrust and diameter, and sets the propulsive-efficiency ceiling.

Everything else is derived.

---

## 2. PARAMETER-BY-PARAMETER EVALUATION

### 2.1 Flight Mach number

| | |
|---|---|
| **Possible source** | CFM public statement that open fan is designed for normal operation between **M0.75 and M0.85**; single-aisle cruise is conventionally M0.78–0.80 |
| **Physical importance** | Sets `V₀`, hence advance ratio, hence the entire velocity triangle. Combines with rotational Mach to give helical tip Mach |
| **Candidate values** | 0.75 · 0.78 · 0.80 |
| **Effect on computational cost** | **Strong.** Higher `M₀` ⇒ higher `M_hel,tip` ⇒ stronger tip shocks ⇒ finer mesh, harder convergence, more iterations |
| **Effect on credibility** | 0.75 sits at the bottom of the stated range but is unambiguously inside it. Going below 0.75 would look like avoiding the hard physics |
| **RECOMMENDED** | **M₀ = 0.75** |
| **Reason** | Lowest cost point that is still genuinely inside the publicly stated open-fan operating range, and still produces **supersonic helical tip Mach (1.10)** — so the defining physics of the architecture is fully retained, not dodged |
| **Confidence** | Medium-high |
| **Status** | **PROVISIONAL** |

### 2.2 Altitude and atmosphere

| | |
|---|---|
| **Source** | 35 000 ft is the conventional cruise altitude; independently, the SR-3 propfan design altitude is quoted as **10.68 km (35 000 ft)** |
| **Derived (ISA)** | `T∞` = 218.8 K · `a∞` = 296.5 m/s · `ρ∞` = 0.3795 kg/m³ · `p∞` = 23 834 Pa |
| **Importance** | Sets `ρ` (hence thrust for a given loading) and `a` (hence every Mach number) |
| **RECOMMENDED** | **35 000 ft, ISA** |
| **Confidence** | High |
| **Status** | **PROVISIONAL** (would be FROZEN but is held with the rest of the set) |

### 2.3 Rotor diameter

| | |
|---|---|
| **Source** | CFM states RISE blade length "over 1.6 m", implying **D ≈ 3.5–4 m**. Ground clearance caps this on a single-aisle aircraft |
| **Importance** | Sets swept area, hence disk loading, hence the `η_p` ceiling. The single most consequential number |
| **Candidates** | 3.5 m · 3.9 m |
| **Cost effect** | Weak on cell count (geometry is scaled), moderate on `Re` |
| **Credibility effect** | Must be *derived from the stated blade length*, never quoted as "RISE's diameter" — CFM has not published a diameter |
| **RECOMMENDED** | **D = 3.5 m** (R = 1.75 m) |
| **Reason** | Bottom of the inferred range; conservative with respect to a number that is inferred rather than stated |
| **Confidence** | Medium — the source gives blade length, not diameter |
| **Status** | **PROVISIONAL** |

### 2.4 Rotational tip Mach and shaft speed

| | |
|---|---|
| **Source** | Classical propfan practice keeps rotational tip Mach near **0.8** to limit compressibility loss and noise |
| **Importance** | **The binding architectural constraint.** Drives sweep, blade count, and diameter simultaneously |
| **Derived** | `U_tip` = 237.2 m/s · `Ω` = 135.5 rad/s · **`N` = 1294 rpm** · `n` = 21.57 rev/s |
| **Cost effect** | **Strong** — this sets `M_hel` and therefore tip shock strength |
| **RECOMMENDED** | **rotational tip Mach 0.80** |
| **Confidence** | High — it is the classical value and the physics behind it is explainable |
| **Status** | **PROVISIONAL** |

### 2.5 Helical tip Mach number — **the defining number of this design**

```
M_hel,tip = √(M₀² + M_rot,tip²) = √(0.75² + 0.80²) = √1.2025 = 1.0966 ≈ 1.10
```

| | |
|---|---|
| **Status** | **CALCULATED** |
| **Significance** | **Supersonic.** The blade tip operates above Mach 1 in the relative frame at the design point |
| **Consequence** | **Sweep is not optional — it is mandatory**, and the project can now *derive* that conclusion rather than copy it from a photograph of an engine |
| **Cross-check** | Consistent with the historical record: SR-3 ran ~M_hel 1.15 at M0.8 cruise and required 45° tip sweep to reach 78.7 % net efficiency |
| **CFD consequence** | The mesh **must** resolve a tip shock; the solver **must** be compressible. This single number drives the whole CFD methodology |

### 2.6 Advance ratio

```
J = V₀ / (n D) = 222.4 / (21.57 × 3.5) = 2.95
```

**CALCULATED.** Cross-check: quoted SR-3 test advance ratio is 3.6 — the same order, confirming the
design point sits in the propfan regime and not in a conventional propeller or fan regime.

### 2.7 Design thrust

| | |
|---|---|
| **Possible source** | Single-aisle cruise thrust per engine is of order 20–25 kN. **No primary source has been read for this project**, and Boeing's RFI figure (~30 000 lbf) is a **sea-level static** rating, which is not the same quantity |
| **Importance** | Sets disk loading, hence `η_p` ceiling, hence blade loading and chord |
| **Cost effect** | Weak |
| **Credibility effect** | **High risk.** Quoting a cruise thrust without a source, or confusing it with a static rating, is exactly the kind of error that is punished |
| **PROVISIONAL working value** | **20 kN**, used only to demonstrate that the design point closes |
| **Status** | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** |
| **Action required in Phase 1** | Either source a cruise thrust from a primary document, **or** invert the problem: prescribe a **disk loading** or a **power loading** as the design input and let thrust follow. The second route is cleaner because it removes the unsourced number entirely |

### 2.8 Disk loading and the efficiency ceiling

```
A          = π (1.75)²  = 9.621 m²
T/A        = 20 000 / 9.621 = 2079 Pa                    (follows from the provisional thrust)
η_p,ideal  = 2 / (1 + √(1 + 2(20 000)/(0.3795 × 9.621 × 222.4²))) = 0.950
```

**CALCULATED.** An ideal propulsive efficiency of **0.950** is the analytical ceiling this
architecture offers at this loading. It is **not** a result and must never be reported as one — it
is the number a real blade in a real installation will fall short of, and measuring that shortfall
is the project.

### 2.9 Blade count

| | |
|---|---|
| **Source** | **CFM has not disclosed RISE blade count.** Historical GE36 was 8+8 (contra-rotating). Public open-fan concepts commonly show ~12 |
| **Importance** | Sets solidity, hence per-blade loading, hence sectional `Cl` demand and tip Mach margin. Also sets the CFD **sector angle** (360°/B) and therefore cell count |
| **Cost effect** | **Strong and direct** — B = 12 gives a 30° sector; B = 8 gives 45°, i.e. ~50 % more cells for the same mesh density |
| **RECOMMENDED** | **B = 12 as a provisional working value** |
| **Reason** | Higher blade count reduces per-blade loading, which eases the sectional `Cl` demand at a Mach-limited tip. **But this must be an output of the Phase 1 solidity calculation, not an input** |
| **Confidence** | Low as an assumption; the *method* for setting it is sound |
| **Status** | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** (set by Phase 1 solidity) |

### 2.10 Hub/tip ratio

| | |
|---|---|
| **Importance** | Sets where useful blade span begins; affects hub blockage and root flow |
| **Typical propfan range** | ~0.25–0.35 |
| **Status** | **TBD — REQUIRES EVIDENCE BEFORE FREEZING.** Will be set in Phase 1 from spinner geometry and root structural allowance, and reported as a design decision |

### 2.11 Wing geometry and scale *(Stage 3)*

| | |
|---|---|
| **Importance** | Sets the strength of the upstream potential field on the rotor (M1) and the area exposed to the slipstream (M2, M3) |
| **Constraint** | Must be a **published, fully-specified section** so the geometry is reproducible and defensible — not an invented aerofoil |
| **Cost effect** | Strong — a transonic wing at M0.75 needs shock resolution of its own |
| **Status** | **TBD — REQUIRES EVIDENCE BEFORE FREEZING.** Deferred to Stage 3 scoping |

### 2.12 Rotor–wing relative position *(Stage 3)*

| | |
|---|---|
| **Importance** | The primary geometric variable of the installed study |
| **Status** | **TBD — REQUIRES EVIDENCE BEFORE FREEZING.** See [`INSTALLATION_CONFIGURATION_SELECTION.md`](INSTALLATION_CONFIGURATION_SELECTION.md) |

---

## 3. DECISION TABLE

| Parameter | Recommended | Evidence source | Reason | Confidence | Status |
|---|---|---|---|---|---|
| Flight Mach `M₀` | **0.75** | CFM: open fan operates M0.75–0.85 | Lowest-cost point inside the stated range that still gives supersonic `M_hel` | Med-High | **PROVISIONAL** |
| Altitude | **35 000 ft** | Conventional cruise; SR-3 design altitude 10.68 km | Standard, independently corroborated | High | **PROVISIONAL** |
| `T∞ / a∞ / ρ∞` | 218.8 K / 296.5 m/s / 0.3795 kg/m³ | ISA | Calculated | High | **CALCULATED** |
| `V₀` | 222.4 m/s | `M₀·a∞` | Calculated | High | **CALCULATED** |
| Diameter `D` | **3.5 m** | CFM: blade "over 1.6 m" ⇒ D ≈ 3.5–4 m | Conservative end of an *inferred* range | Medium | **PROVISIONAL** |
| Rotational tip Mach | **0.80** | Classical propfan practice | The architectural constraint | High | **PROVISIONAL** |
| `U_tip` / `N` / `n` | 237.2 m/s / 1294 rpm / 21.57 s⁻¹ | Derived | Calculated | High | **CALCULATED** |
| **`M_hel,tip`** | **1.10** | Derived | **Supersonic ⇒ sweep mandatory** | High | **CALCULATED** |
| Advance ratio `J` | 2.95 | Derived | Propfan regime, cross-checks vs SR-3 `J`≈3.6 | High | **CALCULATED** |
| Design thrust `T` | *(20 kN working only)* | **No primary source read** | Placeholder to demonstrate closure | **Low** | **TBD — REQUIRES EVIDENCE** |
| Disk loading `T/A` | *(2079 Pa)* | Derived from provisional `T` | Inherits the thrust uncertainty | Low | **TBD** (follows thrust) |
| `η_p,ideal` | **0.950** | Actuator-disk theory | Analytical ceiling, **not a result** | High | **CALCULATED** |
| Blade count `B` | *(12 working)* | Not disclosed by CFM | Must be an **output** of Phase 1 solidity | **Low** | **TBD — REQUIRES EVIDENCE** |
| Hub/tip ratio | — | — | Set in Phase 1 | — | **TBD — REQUIRES EVIDENCE** |
| Airfoil family | *(NACA 16-series candidate)* | Classical high-critical-Mach propeller family | Mach-limited blade needs high `M_crit` | Low | **TBD — REQUIRES EVIDENCE** |
| Sweep distribution `Λ(r)` | — | Derived from `M_hel(r)` in Phase 1 | Cannot come from BEM | — | **TBD — REQUIRES EVIDENCE** |
| Wing section / chord / span | — | — | Stage 3 | — | **TBD — REQUIRES EVIDENCE** |
| Rotor–wing position | — | — | Stage 3 | — | **TBD — REQUIRES EVIDENCE** |

**Count: 4 CALCULATED-and-stable, 5 PROVISIONAL, 7 TBD.** Nothing is marked FROZEN. Freezing happens
at the end of Phase 1, when the design closes on itself and the TBDs have been resolved by
calculation rather than by assertion.

---

## 4. CONSISTENCY CHECK — THE DESIGN POINT CLOSES

Two independent routes to propulsive efficiency must agree:

```
Route 1 — actuator disk:   η_p,ideal = 2/(1 + √(1 + 2T/ρAV₀²))            = 0.9500

Route 2 — non-dimensional: C_T = T/(ρ n² D⁴) = 0.7547
                           C_P = P/(ρ n³ D⁵) = 2.341     (P = T·V₀/η_p,ideal = 4.682 MW)
                           η   = C_T · J / C_P = 0.7547 × 2.946 / 2.341   = 0.9497

Agreement: 0.03 %   ✔  GATE G0 satisfied at the provisional design point
```

Momentum cross-check:
```
V_j = V₀(2/η − 1) = 245.8 m/s ;  v_i = 11.7 m/s
ṁ   = ρA(V₀ + v_i) = 854.7 kg/s
T   = ṁ · 2v_i     = 20 000 N     ✔ reproduces the input
```

**Interpretation:** the parameter set is arithmetically self-consistent. This proves the numbers are
compatible with each other — it proves **nothing** about whether a real blade can achieve them. That
is what Phase 1 and the CFD are for.

---

## 5. WHAT WOULD CHANGE THIS DESIGN POINT

| Trigger | Likely change |
|---|---|
| A primary source for cruise thrust is found | Freeze `T`; disk loading and `η_p,ideal` become firm |
| Phase 1 solidity shows `Cl_des` demand is unachievable at B = 12 | Raise `B`, or raise `D`, or accept higher `Cl` and report reduced stall margin |
| CFD shows an unmanageable tip shock at `M_hel` = 1.10 | Increase sweep first; reduce rotational tip Mach only as a last resort, **and record the trade** |
| Mesh cost at a 30° sector proves infeasible on the workstation | Revisit `B`; **do not** silently coarsen the near-blade mesh |
| Section polar data unavailable at the required Mach | Change airfoil family and record the decision; **do not** extrapolate polars beyond their stated validity |
