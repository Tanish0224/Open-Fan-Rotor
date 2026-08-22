# INSTALLATION CONFIGURATION SELECTION
### BA-OF-01 — which installation architecture, and why

**Created:** 22 August 2026 · **Phase:** 0 · **Decision:** ED-005
**Applies to:** Stage 3 (installed configurations CFG-WING and CFG-INST)

**Why this is decided in Phase 0 even though it is executed in Stage 3:** the installation choice
constrains the rotor design (hub geometry, spinner, support), the CFD domain topology, and the
bookkeeping convention. Deciding it late would mean rebuilding the isolated case.

---

## 1. THE DECISIVE QUESTION IS NOT "WHICH IS MOST RELEVANT"

It is: **which installation produces physics that a steady, workstation-feasible method can
legitimately represent?**

A configuration whose defining mechanism is inherently unsteady cannot be studied with steady RANS.
Running it anyway produces a result that looks fine and is wrong — the failure mode the parent
research rejected candidates C6 and C8 for. This criterion is applied first, before relevance.

---

## 2. CANDIDATE ARCHITECTURES

### A — Tractor rotor ahead of a wing (conventional under-wing)

| Aspect | Assessment |
|---|---|
| **Physics available** | All five target mechanisms: M1 (wing upstream potential field perturbs rotor inflow), M2 (swirling slipstream over wing), M3 (scrubbing), M4 (bookkeeping), M5 (interference) |
| **Industrial relevance** | **Direct.** The GE/Boeing/NASA/ORNL INCITE study is explicitly "an Open Fan mounted on an aircraft wing". Airbus's A380 candidate position is the inboard No. 3 **wing** station |
| **Public evidence** | Extensive — classical propeller–wing interaction literature transfers directly; slipstream/upwash/downwash effects well documented |
| **CFD complexity** | Moderate-high. Rotor inflow is *close to* uniform, so the rotor operating point is well-defined. Wing is transonic at M0.75 and needs shock resolution |
| **CAD complexity** | Moderate — rotor + spinner + support + wing segment |
| **Controlled comparison** | **Excellent.** Rotor geometry, pitch, RPM and freestream can all be held identical; only the wing is added |
| **Artificiality risk** | Low-moderate. A wing *segment* rather than a real planform is an idealisation and must be declared |
| **Interview explainability** | **High.** "The slipstream swirls; one side of the wing sees upwash, the other downwash" is derivable at the whiteboard |

### B — Pusher rotor behind a wing or pylon

| Aspect | Assessment |
|---|---|
| **Physics available** | Dominated by the rotor **cutting the viscous wake** of the upstream body |
| **Industrial relevance** | High — rear-fuselage pusher is a live A380 demonstrator option; Whittle Lab studied exactly this |
| **CFD complexity** | **DISQUALIFYING.** The defining mechanism — a blade passing through a sharp momentum deficit — is **inherently unsteady**. The published work requires **full-annulus URANS**. Steady RANS/MRF time-averages away the very phenomenon being studied |
| **Controlled comparison** | Poor — the rotor's inflow, and hence its operating point, changes substantially, so "same operating condition" becomes hard to hold |
| **Verdict** | **REJECTED on method.** Same reasoning that rejected C6/C8 in the parent research. Not rejected for lack of interest — it is the more interesting physics, and it is listed as future work |

### C — Over-wing tractor (Boeing patent architecture)

| Aspect | Assessment |
|---|---|
| **Physics available** | Slipstream interacting with the wing **upper surface**, where the transonic suction peak and shock live |
| **Industrial relevance** | **Very high** — Boeing US 12,698,086 (issued 4 Aug 2026) is exactly this, and NASA's installation-acoustics work showed over-wing placement gives substantial noise shielding |
| **CFD complexity** | **Very high.** Requires simultaneously credible transonic wing shock capture *and* rotor aerodynamics. The interaction is shock/slipstream, which is the hardest case in the set |
| **Public evidence for validation** | None for this configuration |
| **Artificiality risk** | **High** — the result would be dominated by choices about the supercritical section and pylon shaping that the author has no basis to make well |
| **Verdict** | **REJECTED for baseline** — it is two theses (transonic wing design + propulsor). Retained as future work; the parent research reached the same conclusion for candidate C9 |

### D — Over-wing pusher

Combines the unsteady wake-ingestion problem of B with the transonic upper-surface problem of C.
**REJECTED** — strictly dominated by both.

### E — Rear-fuselage mounted (aft pusher)

| Aspect | Assessment |
|---|---|
| **Industrial relevance** | High — a live A380 demonstrator option |
| **Physics** | Fuselage boundary-layer ingestion + pylon wake — unsteady, and adds a boundary-layer-ingestion problem that is a research field in its own right |
| **CAD/CFD** | Requires a fuselage; pushes toward full-aircraft CFD, which is excluded |
| **Verdict** | **REJECTED** — scope and method |

### F — Wingtip-mounted tractor

| Aspect | Assessment |
|---|---|
| **Physics** | Slipstream swirl opposing and attenuating the wingtip vortex — a genuinely interesting induced-drag mechanism |
| **Public evidence** | **Best of any option** — TU Delft PROWIM-TIP is precisely this, with experimental data |
| **Industrial relevance to open fan** | **Low.** No open-fan concept is wingtip-mounted. It is a distributed-propulsion / regional-turboprop architecture |
| **Verdict** | **REJECTED** — it would optimise for validation availability at the cost of the project's entire industrial premise. Choosing the configuration because data exists, rather than because it is the right question, is a real temptation and is refused here explicitly |

---

## 3. SCORING

| Criterion | A Tractor/wing | B Pusher | C Over-wing | E Rear fuselage | F Wingtip |
|---|---|---|---|---|---|
| Physics available | 9 | 9 | 8 | 8 | 7 |
| Industrial relevance | **10** | 8 | 9 | 7 | 2 |
| Public evidence | 8 | 6 | 3 | 2 | **10** |
| **Steady-method validity** | **9** | **1** | 6 | 2 | 8 |
| CFD feasibility (workstation) | 6 | 1 | 2 | 1 | 6 |
| CAD complexity (lower better) | 7 | 6 | 4 | 2 | 7 |
| Controlled comparison | **10** | 4 | 7 | 4 | 8 |
| Artificiality risk (lower better) | 7 | 6 | 3 | 3 | 7 |
| Interview explainability | 9 | 6 | 6 | 5 | 8 |

**Steady-method validity and controlled comparison are treated as gates, not weights.** B, D and E
fail the first. F fails on premise.

---

## 4. SELECTED CONFIGURATION

> ### **Tractor open-fan rotor mounted ahead of a wing segment (Configuration A)**

### The physical reason — not a score

The selection is justified by a **specific mechanism the configuration makes accessible**, as
required:

**A tractor installation is the only candidate in which the rotor operating point can be held
genuinely constant while the airframe is added.** Because the wing lies *downstream*, the rotor's
inflow remains close to the free stream; the wing's influence on the rotor is a **smooth potential
perturbation**, not a viscous wake. This has three consequences that no other configuration offers
together:

1. **The controlled comparison is real.** Same blade, same pitch, same RPM, same freestream — and
   the rotor is genuinely operating at the same condition, not merely nominally.
2. **Steady MRF is a defensible approximation**, because the perturbation the blades experience is
   smooth and weak rather than a sharp wake cut. The method matches the physics.
3. **All five target mechanisms remain present and separable** — M1 upstream at the disk, M2 and M3
   downstream at the wing, M5 by three-run decomposition.

### Geometry simplifications, declared now

| Simplification | Justification | Risk |
|---|---|---|
| **Wing segment, not a full planform** | Full-aircraft CFD is excluded; the slipstream footprint is local | Absolute installed numbers are not aircraft-transferable — already forbidden by Tier 3 |
| **Semi-span segment with symmetry at the root** | Halves the domain | Suppresses any root/fuselage interaction — declared, not hidden |
| **Simplified support/pylon, or none in the first installed case** | Isolates the wing effect from the pylon-wake effect | A pylon would reintroduce wake-cutting, i.e. configuration B's unsteady problem, through the back door. **Deliberately excluded from the baseline installed case** |
| **Zero aircraft angle of attack in the baseline installed case** | Preserves the cleanest possible control | Removes the 1P/incidence mechanism — already future work |

**The no-pylon decision is important and deliberate.** Adding a pylon upstream of the rotor would
convert this into the configuration the project just rejected on method. The support structure, if
modelled at all, is placed **downstream** of the rotor disk.

---

## 5. WHAT REMAINS TBD

| Item | Status |
|---|---|
| Wing section (must be a published, fully-specified section) | **TBD — REQUIRES EVIDENCE BEFORE FREEZING** |
| Wing chord, span, and slipstream-to-chord ratio | **TBD — REQUIRES EVIDENCE** |
| Axial offset from rotor plane to wing leading edge | **TBD — REQUIRES EVIDENCE** |
| Vertical offset of rotor axis relative to the wing | **TBD — REQUIRES EVIDENCE** |
| Whether a downstream support is modelled at all | **TBD** |
| Rotor rotation direction (up-inboard vs up-outboard) | **TBD** — it changes the sign of the spanwise asymmetry and is a genuine result-affecting choice that must be recorded |

**The rotation-direction item is not a detail.** Whether the up-going blade is inboard or outboard
determines which side of the wing gains incidence. It must be stated with every installed result.

---

## 6. HONEST STATEMENT OF WHAT THIS CONFIGURATION CANNOT SHOW

Required so that no reader over-reads the Stage 3 result:

- **No unsteady blade-passing physics.** Steady MRF gives a time-averaged field only.
- **No 1P loads**, because incidence is zero and the method is steady.
- **No pylon-wake ingestion**, deliberately excluded.
- **No acoustic consequence** of any of it.
- **No aircraft-level drag or fuel-burn implication** — there is no aircraft.
- **No claim about over-wing versus under-wing**, because only one position is studied.
