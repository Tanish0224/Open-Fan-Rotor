# PROJECT REQUIREMENTS AND CLAIM HIERARCHY
### BA-OF-01 — Open-Fan Rotor Aerodynamic Design and Installation-Effect Assessment

**Authority:** This is the **controlling document** for the project. Every later phase must obey it.
Where any other document conflicts with this one, **this one wins**.
**Created:** 22 August 2026 · **Phase:** 0 · **Status:** ACTIVE

**Modification rule:** No requirement in §7.1 may be changed without a Decision Log entry recording
the old value, the new value, the evidence, and the date. No claim may be promoted between tiers in
§7.2 without the evidence artifact existing on disk.

---

# 7.1 FROZEN PROJECT SCOPE

## 7.1.1 Baseline architecture

| Element | Specification | Status |
|---|---|---|
| Propulsor type | **Single-rotation open (unducted) rotor** | **FROZEN** |
| Rotating rows | **One** | **FROZEN** |
| Stationary rows (OGV) | **None in baseline** — see ED-008 | **FROZEN for baseline**; OGV is FUTURE WORK |
| Duct / nacelle / casing | **None** | **FROZEN** |
| Spinner / hub fairing | Present — required to close the geometry and set the root boundary | **FROZEN** |
| Pitch control | Fixed pitch at the analysed condition. Variable pitch is a real-engine feature but is **not modelled**; each operating point is a separately-set fixed pitch | **FROZEN** |
| Blade sweep | Present, and **justified from the helical-Mach distribution**, not copied | **FROZEN** in principle; distribution TBD in Phase 1 |
| Scale | **Full engine scale.** No model-scale reduction | **FROZEN** |

**Naming precision (important).** Without an OGV this is an open-fan **rotor**, not a complete
open-fan **propulsor**. All project text, the README, and the resume line must say **"rotor"**.
Writing "propulsor" or "stage" would imply a rotor+OGV system that does not exist here. The approved
resume statement already says "rotor" — that wording is correct and must be preserved.

## 7.1.2 Design condition

Every value below is **PROVISIONAL** — self-consistent and evidence-anchored, but not frozen until
Phase 1 closes. Full reasoning and sources: [`DESIGN_POINT_SELECTION.md`](DESIGN_POINT_SELECTION.md).

| Parameter | Provisional value | Basis | Status |
|---|---|---|---|
| Flight Mach `M₀` | **0.75** | Within the M0.75–0.85 open-fan operating range stated by CFM | PROVISIONAL |
| Altitude | **35 000 ft (10 668 m)** | Standard cruise; matches the stated SR-3 design altitude | PROVISIONAL |
| `T∞`, `a∞`, `ρ∞` | 218.8 K, 296.5 m/s, 0.3795 kg/m³ | ISA, **CALCULATED** | CALCULATED |
| `V₀` | 222.4 m/s | `M₀·a∞`, **CALCULATED** | CALCULATED |
| Rotor diameter `D` | **3.5 m** | RISE blade stated "over 1.6 m" ⇒ D ≈ 3.5–4 m | PROVISIONAL |
| Rotational tip Mach | **0.80** | Classical propfan practice | PROVISIONAL |
| Tip speed `U_tip` | 237.2 m/s | **CALCULATED** | CALCULATED |
| Shaft speed `N` | 1294 rpm (`n` = 21.57 rev/s) | **CALCULATED** | CALCULATED |
| **Helical tip Mach** | **1.10** | **CALCULATED** — supersonic; this is why sweep is mandatory | CALCULATED |
| Advance ratio `J` | 2.95 | **CALCULATED** | CALCULATED |
| Design thrust `T` | **20 kN** | Single-aisle cruise thrust per engine, order-of-magnitude | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** |
| Disk loading `T/A` | 2079 Pa | **CALCULATED** (A = 9.621 m²) | CALCULATED |
| Ideal `η_p` | **0.950** | **CALCULATED** from actuator-disk theory | CALCULATED |
| Blade count `B` | **12** | Set in Phase 1 by required solidity at tip-Mach-limited loading | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** |
| Hub/tip ratio | — | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** | TBD |
| Airfoil section family | — | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** | TBD |
| Wing section, chord, span | — | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** (Stage 3) | TBD |
| Rotor–wing relative position | — | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** (Stage 3) | TBD |

**The design point closes on itself.** `η = C_T·J/C_P` returns 0.9497 against the 0.9500 from the
actuator-disk relation — a consistency check, not a result. Any Phase 1 change must re-close it.

## 7.1.3 Comparison configurations

| ID | Configuration | Purpose | Stage |
|---|---|---|---|
| **CFG-ISO** | Rotor alone, uniform free stream | Baseline; design verification | Stage 2 |
| **CFG-WING** | Wing segment alone, no rotor | Linear reference for decomposition | Stage 3 |
| **CFG-INST** | Rotor + wing, same rotor, same operating point | The installed case | Stage 3 |

**The control.** Between CFG-ISO and CFG-INST the following are held **identical**: blade geometry,
blade count, diameter, pitch setting, shaft speed, flight Mach, altitude, fluid properties,
turbulence model, near-blade mesh topology and near-blade cell sizing. **Only the presence of the
wing changes.** Any deviation from this list invalidates the comparison and must be recorded.

## 7.1.4 Primary outputs

1. A reproducible **BEM design code** producing the radial chord, twist and thickness distribution.
2. **Parametric SolidWorks CAD** in which no dimension is typed by hand, with verification evidence.
3. **Isolated rotor CFD**: thrust, torque, `η_p`, `C_T`, `C_P`, radial loading, compared to design intent.
4. A **mesh-independence study on integrated thrust and torque** — not on a contour plot.
5. A **compressible rotating-blade validation case** with published experimental comparison.
6. *(Stage 3)* **Installed-vs-isolated delta** with a declared thrust–drag bookkeeping convention.

## 7.1.5 Minimum required analyses (project is not defensible without these)

- [ ] Analytical actuator-disk sizing with closure check
- [ ] BEM design with the local velocity triangle documented at ≥3 radii
- [ ] Helical Mach distribution along the span, with the sweep justification derived from it
- [ ] CAD geometric verification (volume, bounding box, rebuild state, save/reopen re-verification)
- [ ] CFD mesh-independence on thrust **and** torque
- [ ] Residual + integrated-quantity stationarity evidence
- [ ] `y⁺` distribution reported over the blade
- [ ] One external validation case with published experimental data
- [ ] Explicit statement of what was **not** validated

---

# 7.2 CLAIM HIERARCHY

> **If a statement is not in Tier 1 or Tier 2, it may not be made — anywhere.**

## TIER 1 — VERIFIED CLAIMS (require a named evidence artifact on disk)

None yet. **Phase 0 has produced no computational or geometric evidence.** This table is the
*template*; a row may only be filled once its artifact exists.

| Planned claim | Evidence artifact required before this may be claimed | Status |
|---|---|---|
| "Designed an open-fan rotor from first principles" | BEM design script + radial distribution table + closure check vs actuator disk | **PENDING** |
| "Parametric CAD with no hand-typed dimensions" | Geometry generator + SolidWorks build script + verification JSON | **PENDING** |
| "CAD verified against independent calculation" | Volume/bbox/rebuild/reopen verification with stated tolerance | **PENDING** |
| "Mesh-independent thrust and torque" | ≥3-mesh study with the reported quantity converging; GCI if achievable | **PENDING** |
| "Validated the compressible rotating-blade method against published experiment" | Benchmark case run + quantitative comparison to published data | **PENDING** |
| "Quantified the installed-vs-isolated performance change" | CFG-ISO, CFG-WING, CFG-INST results + declared bookkeeping convention | **PENDING — STAGE 3** |
| "Decomposed the installation effect into inflow / wing / interference" | Three-run decomposition table | **PENDING — STAGE 3** |

## TIER 2 — DESIGN AND MODELLING CLAIMS (true as statements of *choice*, not of *achievement*)

These are safe to state **only in the "was designed for / was modelled as" form**. The distinction
is not cosmetic: it is the difference between a defensible statement and a false one.

| ✅ Permitted form | ❌ Forbidden form of the same thing |
|---|---|
| "The rotor was **designed for** a helical tip Mach of 1.10 under a stated tip-speed constraint" | "The rotor **achieves** M_hel 1.10 performance" |
| "Sweep was **selected** to reduce the leading-edge-normal Mach number" | "Sweep **reduced** losses by X %" *(unless measured)* |
| "The blade was **sized by** blade-element momentum theory for 20 kN at cruise" | "The blade **produces** 20 kN" *(until CFD confirms it)* |
| "Modelled with the k-ω SST turbulence closure" | "Accurately captured the tip vortex" |
| "A steady multiple-reference-frame formulation **was used**" | "Unsteady blade-passing effects **were shown to be** negligible" |
| "Wall functions were used with `y⁺` in the range …" | "The boundary layer **was resolved**" |
| "The design point **was selected as** representative of open-fan cruise" | "The design point **matches** CFM RISE" |

**Mandatory qualifiers.** Where a Tier-1 claim is made, these qualifiers are **not optional**:

| Claim | Required qualifier |
|---|---|
| Any efficiency number | must state **which** efficiency (propulsive, isolated or installed) and the operating point |
| Any thrust number | must state what was held fixed (pitch, RPM, `J`) |
| Any benchmark comparison | must say **"verification/validation of the method"**, never "validation of the open-fan design" |
| Any installed result | must state the **thrust–drag bookkeeping convention** used |
| Any low-speed benchmark used for a transonic design | must state that **compressibility was not covered by that benchmark** |
| Any mesh-independence claim | must name the quantity that converged |

## TIER 3 — FORBIDDEN CLAIMS

**None of these may appear in any document, README, commit message, resume line, or interview
answer.**

**Performance and validation**
- ❌ "Validated open fan" / "validated open-fan design" / "experimentally validated"
- ❌ "GE-like performance", "RISE-comparable", "matches CFM RISE", "industry-equivalent"
- ❌ "Boeing-compatible", "Boeing-relevant design", "designed to Boeing requirements"
- ❌ "Industry-optimised", "optimised rotor", "optimal blade" — **no optimisation is being run**
- ❌ "Production-ready", "flight-ready", "certifiable"
- ❌ Any **fuel-burn** or **CO₂** claim — there is no mission or cycle model
- ❌ Any **noise** or **acoustic** claim, including "quieter" — **no acoustic model exists**
- ❌ Any **structural**, **fatigue**, **1P-load** or **aeroelastic** claim
- ❌ "Higher efficiency than a ducted fan" — the ducted comparison is permanently excluded
- ❌ Any absolute installed number presented as transferable to a real aircraft

**Provenance**
- ❌ Any use, tracing, or visual approximation of CFM RISE or other proprietary geometry
- ❌ Presenting the PANDORA / TU Delft / NASA geometries as the author's own design
- ❌ Any claim of institutional HPC use — **IIT Kanpur HPC is not authorised for this project**

**Method**
- ❌ Calling CFD-vs-CFD agreement "validation" — it is verification at most
- ❌ Calling a single-mesh result "mesh-independent"
- ❌ Presenting a steady RANS result as evidence about an unsteady phenomenon
- ❌ "Converged" used to mean "residuals dropped", without integrated-quantity stationarity

### The specific traps for this project

| ❌ NOT SAFE | ✅ SAFE |
|---|---|
| "Designed and validated an open-fan propulsor" | "Designed an open-fan **rotor** from first principles and **verified** it against its analytical design intent" |
| "Quantified installation effects on an open fan" *(before Stage 3)* | "Characterised the **isolated** rotor and established the installed-case methodology" |
| "CFD validated against NASA data" | "CFD **method** verified against a published experimental rotor benchmark; the open-fan design itself is **not** experimentally validated" |
| "20 % efficiency improvement" | "Actuator-disk theory gives an **ideal** propulsive efficiency of 0.950 at the selected disk loading — an analytical ceiling, not a computed result" |
| "Open fan is more efficient" | "Low disk loading raises the propulsive-efficiency **ceiling**; what this project measures is how much of it a real blade in a real installation retains" |

---

# 7.3 SCOPE GUARDRAIL — TIME AND STAGING

Authorised effort is approximately **five working days on a personal workstation**. This is far
shorter than the full research question requires, and the requirement is therefore **staged
maturity**, not reduced rigour.

| Stage | Effort | Delivers | Claimable on completion |
|---|---|---|---|
| **Stage 1** | Day 1 | Repo, Phase 0 docs, BEM design, parametric CAD + verification, **one preliminary Fluent run** | Design + CAD claims only. The Fluent run is **PRELIMINARY** and grounds **no** performance claim |
| **Stage 2** | Days 2–5 | Mesh independence, benchmark validation case, isolated performance, tip-Mach sweep | Isolated rotor performance, method verification |
| **Stage 3** | Unscheduled | CFG-WING, CFG-INST, decomposition, sensitivity | Installation-effect claims — **and only then** |

**Hard rule.** Until Stage 3 exists on disk, the project is described as *"aerodynamic design and
isolated characterisation of an open-fan rotor, with installation assessment in progress."* The
approved title may remain the project's *target*; it may not be used as a *completed* description.

---

# 7.4 REQUIREMENT COMPLIANCE GATES

| Gate | Condition | Consequence if failed |
|---|---|---|
| **G0** | Design point closes: `η = C_T·J/C_P` matches actuator-disk `η_p,ideal` to <1 % | Phase 1 cannot close |
| **G1** | CAD volume/bbox verified; survives save→close→reopen | Phase 2 cannot close |
| **G2** | Thrust and torque change <2 % between the two finest meshes | Report as **NOT mesh-independent**; do not claim it |
| **G3** | Benchmark case reproduces published data within a **pre-declared** band | Report the miss honestly; do not widen the band after the fact |
| **G4** | CFD thrust within a pre-declared band of BEM design intent | A miss is a **finding**, not a failure — investigate and report |
| **G5** *(Stage 3)* | CFG-ISO and CFG-INST differ **only** by the wing | Comparison void; must be rebuilt |

**Gate philosophy:** a failed gate that is reported honestly is
worth more than a passed gate that was engineered by loosening the criterion. Bands are declared
**before** the run, never after.
