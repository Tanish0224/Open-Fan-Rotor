# VALIDATION AND VERIFICATION PLAN
### BA-OF-01 — what may be called verified, what may be called validated, and what may be called neither

**Created:** 22 August 2026 · **Phase:** 0 · **Decision:** ED-006

> **The principle this plan is built on.** A CFD workflow can be mesh-converged,
> turbulence-model-checked and geometrically perfect, and still miss a published reference value.
> When that happens the value of the work lies in reporting it, diagnosing it, and stating the
> consequence — not in hiding it or in retrospectively widening the band. **A plausible simulation
> is not a validated simulation.** This plan is written so that the discipline is structurally
> enforced rather than left to good intentions.

**The formal distinction, used strictly throughout:**
- **Verification** — *are we solving the equations right?* (numerics, meshes, consistency, conservation)
- **Validation** — *are we solving the right equations?* (comparison against **physical experiment**)

CFD-vs-CFD agreement is **never** validation. Agreement with an empirical correlation is **not**
validation. Only comparison with measured data validates.

---

## 1. THE FOUR-LEVEL HIERARCHY

| Level | What | Earns the right to say |
|---|---|---|
| **1. Analytical verification** | Closed-form relations the solution must obey | "Numerically consistent" |
| **2. CAD verification** | Geometry is what the design table specified | "Geometry verified" |
| **3. Numerical verification** | Mesh, convergence, conservation, sensitivity | "Numerically verified / mesh-independent in *X*" |
| **4. Benchmark validation** | Comparison against **published experimental** data | "Method validated against experiment for *this* regime" |

**No level may be skipped, and level 4 does not validate the open-fan design itself** — only the
method, and only within the regime the benchmark covers.

---

## 2. LEVEL 1 — ANALYTICAL VERIFICATION

| Check | Criterion | Gate |
|---|---|---|
| Actuator-disk closure: `T = ṁ·2v_i` reproduces input `T` | < 0.1 % | G0 |
| Two efficiency routes agree: `η_p,ideal` vs `C_T·J/C_P` | < 1 % | G0 |
| BEM radial-station independence (2× stations) | `T`, `Q` change < 0.1 % | Phase 1 |
| CFD thrust ≤ actuator-disk ideal ceiling | Must hold; a violation means a bookkeeping or reference-frame error | Phase 4 |
| CFD shaft power vs Euler work `∫ω·r·V_θ dṁ` | < 2 % | Phase 4 |
| Mass conservation across the CFD domain | < 0.1 % | Phase 4 |
| Axial momentum balance over a control volume enclosing the rotor vs integrated surface thrust | < 2 % | Phase 4 |

**The momentum-balance check is the single most important one**, because it independently confirms
the thrust integral. Two routes to the same force, from different data.

---

## 3. LEVEL 2 — CAD VERIFICATION

| Check | Criterion |
|---|---|
| Blade section coordinates match the design table at every station | Exact within CAD tolerance |
| Chord, twist, thickness, sweep re-measured from the solid vs the table | < 0.1 % |
| Blade count, hub radius, tip radius, rotor diameter | Exact |
| Solid body count; no stray bodies; rebuild state clean | Exact |
| Geometry validity check (self-intersection, zero-thickness) | Pass |
| Volume and bounding box vs independent calculation | Declared tolerance |
| **Save → close → reopen → re-measure** | All of the above reproduce |

**Inherited rule (Section 36.8 of the master context):** `SaveAs3` may return a falsy value even on
a successful write. Filesystem existence plus reopened re-measured geometry is the only proof.

**Inherited rule (Section 36.4):** no production sketch on a face without an explicitly verified
local-coordinate mapping. Reference planes only.

---

## 4. LEVEL 3 — NUMERICAL VERIFICATION

| Check | Criterion | Gate |
|---|---|---|
| **Mesh independence on `T` and `Q`** | ≥3 systematically refined meshes; < 2 % change between the two finest; GCI reported if the asymptotic range is reached | **G2** |
| Residual convergence | ≥4 orders, **and** — |
| **Integrated-quantity stationarity** | `T` and `Q` flat over the final 500+ iterations. **Residual drop alone is not convergence** | G2 |
| `y⁺` distribution over the blade | Reported as a map, within the range the wall treatment requires | G2 |
| Turbulence-model sensitivity | ≥2 closures; the spread is reported as model-form uncertainty, **not** averaged away | Phase 4 |
| Domain-size sensitivity | Far-field boundaries moved; `T` change < 1 % | Phase 3 |
| Sector-vs-full-annulus check (isolated case) | Periodic sector reproduces a full-annulus result | Phase 4 |

**Rule:** if G2 fails, **no performance number may be reported at all** — not "approximately", not
"indicatively". Report the failure.

---

## 5. LEVEL 4 — BENCHMARK VALIDATION

### 5.1 Candidates actually investigated

| Candidate | Geometry public? | Data public? | Conditions | Licence | Verdict |
|---|---|---|---|---|---|
| **Caradonna–Tung rotor** (NASA TM-81232 / NTRS 19820004169) | **Yes — and trivially reconstructable**: rectangular, untwisted, untapered, NACA 0012, AR 6, R = 1.143 m, c = 0.191 m | **Yes** — blade surface pressure at multiple radial stations, plus tip-vortex surveys | **Hover**; tip Mach up to **0.877** (transonic); Re_tip ≈ 3.9×10⁶ | US Government work, **public use** | **SELECTED — MANDATORY** |
| **UIUC Propeller Database** (Selig et al., ~250 propellers, Vols 1–4) | **Yes** — `r/R`, `c/R`, `β` tabulated | **Yes** — `C_T`, `C_P` vs `J` measured | **Axial flight**, `J` sweeps; **low Re (~10⁵)**, low Mach | **Freely downloadable**, no request | **SELECTED — RECOMMENDED** |
| **PANDORA open virtual test case** (*J. Turbomach.* 148(6):061019, 2026) | Released open-access per the paper | **RANS results, not experiment** | Open-fan, realistic | **Terms not verified** | **REJECTED as validation** — it is CFD, so at best solver *verification*; access terms unconfirmed |
| **TU Delft PROWIM / XPROP-3** | Yes, but **CC-BY-NC-ND, restricted, on request** | Yes (4TU repository) | Propeller–wing, low speed | Request required; approval not guaranteed | **REJECTED** — project must not depend on a request that may be refused *(user decision, 22 Aug 2026)* |
| **NASA F31/A31 open rotor** | **Data yes; blade geometry not established as public** | Yes, extensive | CROR, take-off to cruise | Geometry status unresolved | **REJECTED** — cannot reproduce a geometry that is not published |
| **NASA SR-2 / SR-3 propfan** | **Not established.** Reports describe parameters; full coordinate tables not confirmed obtainable | Yes | Transonic, M0.8 | — | **REJECTED for reproduction; retained as a qualitative literature cross-check only** |

**The SR-2/SR-3 correction.** The parent research proposed SR-2/SR-3 as the validation path. On
investigation, **the performance data is public but the blade coordinate geometry has not been
confirmed as obtainable.** Validation requires reproducing the geometry, so this route cannot be
relied upon. This is a **correction to the parent research's recommendation**, made here on evidence.
SR-3's published efficiency (78.7 % at M0.8, 45° tip sweep) remains valid as a *qualitative
literature anchor* for the sweep argument — but it is not a validation case.

### 5.2 The two-axis validation architecture

Neither benchmark alone covers the design condition. Together they **bracket** it, and the residual
gap is named rather than hidden.

```
                        COMPRESSIBLE
                             ▲
        Caradonna–Tung  ●    │    ○  ← BA-OF-01 design point
        (hover, M_tip 0.877) │       (axial flight, M_hel,tip 1.10)
                             │            ▲
        ─────────────────────┼────────────┼──────────►  AXIAL FLIGHT (J)
                             │            │
                  UIUC props ●────────────┘
                  (axial flight, low Mach, low Re)
```

| Axis | Benchmark | What it validates | What it does **not** cover |
|---|---|---|---|
| **A — compressible rotating blade** | Caradonna–Tung | Rotating reference frame / MRF implementation; compressible blade surface pressure; **transonic tip flow and shock capture**; tip-vortex behaviour | Axial flight (`J` = 0); no advance ratio |
| **B — axial-flight performance bookkeeping** | UIUC propeller | `C_T`, `C_P`, `η` vs `J` extraction; thrust/torque integration; BEM-vs-CFD comparison methodology | Compressibility; correct Reynolds number |
| **RESIDUAL GAP** | **none exists** | — | **Compressible *and* axial flight simultaneously — the actual design condition — is NOT covered by any available public benchmark** |

**This residual gap must be volunteered, not concealed.** It is the honest answer to "what did you
not validate?", and stating it unprompted is worth more than any additional figure.

### 5.3 Acceptance bands — declared in advance

Bands are fixed **before** the runs. Widening a band after seeing a result is forbidden.

| Benchmark | Quantity | Declared band |
|---|---|---|
| Caradonna–Tung | Sectional `Cp` at each published radial station, subcritical case | Qualitative shape match + suction-peak magnitude within **10 %** |
| Caradonna–Tung | Transonic case (`M_tip` 0.877): shock **location** on the upper surface | Within **5 % chord** |
| Caradonna–Tung | Integrated thrust coefficient | Within **10 %** |
| UIUC propeller | `C_T` and `C_P` across the `J` sweep | Within **10 %**; **trend and the `J` of peak efficiency must be reproduced** |

**If a band is missed:** report it, diagnose it, and state the consequence for the main study.
A missed band does **not** authorise proceeding as if it had passed.

---

## 6. WHAT IS AND IS NOT VALIDATED — THE HONEST SUMMARY

| Element | Highest status achievable in this project |
|---|---|
| Analytical design method (BEM) | **Numerically verified**, internally consistent |
| CAD geometry | **Verified** against the design table |
| CFD numerics | **Numerically verified** (mesh, convergence, conservation) |
| Compressible rotating-blade method | **Validated against experiment** — hover regime only |
| Axial-flight performance bookkeeping | **Validated against experiment** — low-Mach, low-Re regime only |
| **The open-fan rotor design itself** | **NOT VALIDATED.** No experimental data exists for it and none will be produced |
| **The installed configuration** | **NOT VALIDATED.** No public experimental data exists for an installed open fan |
| Compressible + axial-flight combined regime | **NOT VALIDATED** — the residual gap of §5.2 |

**Project-level classification, to be stated in the README and defended in interview:**

> *A first-principles rotor design study with a CFD workflow verified numerically and validated
> against two published experimental benchmarks that bracket — but do not jointly cover — the design
> condition. The rotor design and the installed configuration are numerically verified and
> **not experimentally validated**.*

---

## 7. WHAT SUBSTITUTES FOR THE VALIDATION THAT CANNOT EXIST

Where validation is impossible, **sensitivity replaces it** — and is labelled as a substitute, never
as an equivalent:

| Unvalidatable element | Substitute evidence |
|---|---|
| Open-fan design performance | Turbulence-model spread; mesh-convergence uncertainty; BEM-vs-CFD cross-check |
| Installed result *(Stage 3)* | Bookkeeping-convention sensitivity (BK-1 vs BK-2); geometric offset sensitivity |
| Transonic tip behaviour at `M_hel` 1.10 | Caradonna–Tung transonic case at `M_tip` 0.877 — the nearest validated point; the extrapolation is declared |
| Sectional data beyond polar validity | Reported as an explicit uncertainty in `Q`, hence in `η_p` |

**Uncertainty reporting rule:** every headline number is reported with its mesh-convergence
uncertainty and its turbulence-model spread. A number without an uncertainty is not a result.
