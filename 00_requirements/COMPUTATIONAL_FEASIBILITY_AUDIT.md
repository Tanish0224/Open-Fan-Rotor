# COMPUTATIONAL FEASIBILITY AUDIT
### BA-OF-01 — what actually fits on the available machine, decided before geometry exists

**Created:** 22 August 2026 · **Phase:** 0 · **Decision:** ED-010

**Platform policy (user decision, 22 Aug 2026):**
> The baseline project **must be completable on a personal workstation**. Institutional HPC is **not
> a dependency**, is not assumed available, and **may not be claimed in portfolio material** unless
> separately authorised. External or publicly accessible compute is permitted only as an *optional
> acceleration path for a small number of expensive cases*.

**Platform status — MEASURED 22 Aug 2026. Open item O1 is CLOSED.**

| Property | Measured value |
|---|---|
| CPU | AMD Ryzen 7 6800H |
| Physical cores | **8** (16 logical) |
| Max clock | 3.2 GHz |
| **Total RAM** | **15.2 GB** |
| GPU | NVIDIA RTX 3050 Ti Laptop, 4 GB (not used for CFD) |
| Free disk (D:) | 242 GB |
| Solver | **ANSYS Fluent 2025 R1**, `D:\ANSYS Inc251luent
tbin\win64luent.exe` |

> **CONSEQUENCE — THIS INVALIDATES THE ORIGINAL FINE MESH.**
> At ~1.5–2.5 GB per million cells for a coupled compressible solve, and with roughly **12 GB
> usable** once the OS and pre/post are accounted for, the practical ceiling is **≈5 M cells**.
> The 6.5–8.5 M-cell "fine" mesh assumed in the first draft of this audit is **NOT achievable on
> this machine** and has been withdrawn. The mesh-independence triplet is re-cut in §4.
> This is precisely the failure the calibration gate exists to catch, and it was caught before
> any expensive case was launched rather than after.

**Licence note:** Fluent's usable parallel core count under the available licence has **not** been
confirmed and must be checked on the first run. If it is limited to 4 cores, every runtime figure
below roughly doubles.

---

## 1. STATUS OF THE NUMBERS BELOW

All cell counts and runtimes are **ESTIMATED**, not measured. They are order-of-magnitude sizing
figures derived from mesh topology and standard solver-throughput heuristics.

> **MANDATORY GATE — CALIBRATION BEFORE COMMITMENT.**
> Before any expensive simulation phase begins, a **timing calibration run** must be performed: one
> coarse mesh, 200 iterations, wall-clock recorded, cells-per-second-per-core extracted. Every
> estimate in this document is then **replaced by a measured value**, and the level structure in §4
> is re-checked against reality. **No expensive case may be launched against an estimate.**

Core count and RAM are marked **TBD — REQUIRES CONFIRMATION**; 8 cores is inferred, not confirmed.

---

## 2. ESTIMATED MESH SIZES

| Case | Domain | Wall treatment | Estimated cells |
|---|---|---|---|
| Preliminary isolated (Stage 1) | 30° sector, 1 blade | Wall functions, `y⁺` 30–100 | **1.0–1.8 M** |
| Isolated coarse | 22.5° sector | `y⁺` ≈ 1 | **~0.9 M** |
| Isolated medium | 22.5° sector | `y⁺` ≈ 1 | **~2.0 M** |
| Isolated fine | 22.5° sector | `y⁺` ≈ 1 | **~4.3 M** ← RAM-capped, was 6.5–8.5 M |
| Isolated full annulus (periodicity check) | 360°, 12 blades | wall functions | **15–25 M** |
| Caradonna–Tung validation | 180° sector, 1 of 2 blades | `y⁺` ≈ 1 | **2.0–3.0 M** |
| UIUC propeller validation | 180°/120° sector | `y⁺` ≈ 1 | **1.5–2.5 M** |
| **Installed, body-force rotor** | Full annulus + wing | `y⁺` ≈ 1 on wing | **5–10 M** |
| **Installed, fully resolved** | Full annulus, 12 blades + wing | `y⁺` ≈ 1 | **50–65 M** |

**Basis for the sector estimate:** the Phase 1 design selected **B = 16 blades**, so the periodic
sector is **22.5°**, not the 30° assumed when B = 12 was a placeholder. That alone cuts cell count
by ~25 % relative to the first draft.

**Mesh-independence triplet (revised):** 0.9 M → 2.0 M → 4.3 M, a constant linear refinement ratio
of **r ≈ 1.30**, which is the minimum for a meaningful GCI. The fine mesh at ~4.3 M cells needs
roughly **8–9 GB**, which fits 12 GB usable with margin.

---

## 3. ESTIMATED RUNTIMES (8 cores, steady compressible RANS, second order)

| Cells | Est. s/iteration | Iterations to converge | **Est. wall-clock per case** |
|---|---|---|---|
| 1.5 M | 1.5–3 | 2500–4000 | **1–3 h** |
| 3 M | 3–6 | 3000–5000 | **3–8 h** |
| 4 M | 4–8 | 3000–5000 | **4–11 h** |
| 8 M | 8–16 | 4000–6000 | **9–27 h** |
| 20 M | 20–40 | 5000–8000 | **28–89 h** |
| 60 M | 60–120 | 6000–10000 | **100–330 h** — *infeasible* |

**Memory:** roughly 1.5–2.5 GB per million cells for a coupled compressible solve.
8 M cells ⇒ **~12–20 GB**. 60 M cells ⇒ **~90–150 GB — almost certainly exceeds the workstation.**
**RAM must be confirmed before the fine mesh is attempted.**

### Conclusions that follow directly

1. **A 60 M-cell fully-resolved installed case is not workstation-feasible** — on runtime *and*
   probably on memory. This is the single hardest constraint in the project.
2. **The 8 M fine isolated mesh is feasible but is an overnight-and-into-the-next-day run.** It must
   be launched early and only once.
3. **Sector cases are comfortable.** The isolated study is genuinely workstation-scale.
4. **The body-force installed case is feasible** at 5–10 M cells — confirming the §4 methodology
   decision was the right one, and confirming it was made for the right reason.

---

## 4. LEVEL STRUCTURE

Designed so that **no single expensive simulation can block the project**.

### LEVEL 1 — MANDATORY (minimum defensible project)

*Everything here fits the workstation comfortably.*

| # | Item | Est. cost |
|---|---|---|
| 1.1 | BEM design code + radial distribution table + G0 closure | minutes |
| 1.2 | Parametric SolidWorks CAD + geometric verification | hours (no CFD) |
| 1.3 | Timing calibration run | ~1 h |
| 1.4 | Isolated rotor, medium mesh, design point, k-ω SST | 4–11 h |
| 1.5 | **Caradonna–Tung validation case** | 3–8 h |
| 1.6 | Analytical cross-checks (momentum balance, Euler work, conservation) | minutes |

**Claims unlocked:** first-principles design; verified CAD; a compressible rotating-blade method
validated against published experiment; isolated performance **reported with the caveat that mesh
independence is not yet established**.

**Total ≈ 8–20 h of solver time.** Achievable inside the 5-day budget using overnight runs.

### LEVEL 2 — RECOMMENDED (the approved target for the authorised effort)

| # | Item | Est. cost |
|---|---|---|
| 2.1 | Mesh independence: coarse + fine added to Level 1's medium | 5–14 h |
| 2.2 | Turbulence sensitivity: Spalart–Allmaras on the medium mesh | 4–11 h |
| 2.3 | `y⁺` sensitivity: wall-function vs wall-resolved | 2–5 h |
| 2.4 | Domain-size sensitivity | 4–11 h |
| 2.5 | Helical-tip-Mach / `J` sweep, 4–5 points on the medium mesh | 16–55 h |
| 2.6 | UIUC propeller validation | 2–6 h |

**Claims unlocked:** mesh-independent isolated performance with a stated model-form uncertainty; the
tip-Mach trade quantified; a second experimental validation on the axial-flight axis.

**Total ≈ 33–102 h.** **This exceeds the 5-day budget if run serially.** Level 2 must be
**prioritised**: 2.1 (mesh independence) is the highest value because it gates every performance
claim; 2.5 (the sweep) is the most expensive and the most compressible into fewer points.

### LEVEL 3 — STRETCH (only after Levels 1 and 2 pass)

| # | Item | Est. cost | Feasible on workstation? |
|---|---|---|---|
| 3.1 | CFG-WING (wing alone) | 5–15 h | Yes |
| 3.2 | Body-force disk calibration against resolved CFG-ISO | 3–8 h | Yes |
| 3.3 | CFG-INST, body-force rotor | 10–30 h | Yes, slow |
| 3.4 | Second blade-clocking position (MRF uncertainty) | 10–30 h | Yes, slow |
| 3.5 | Bookkeeping-convention sensitivity (BK-1 vs BK-2) | post-processing | Yes |
| 3.6 | Geometric offset sensitivity, 2–3 positions | 20–90 h | Marginal |
| 3.7 | **Fully-resolved full-annulus installed** | 100–330 h | **NO — external compute only** |

**Level 3 is NOT achievable within the authorised 5 days.** It is the natural continuation.

---

## 5. THE HONEST VERDICT ON SCOPE vs BUDGET

**Authorised effort: ~5 working days on a personal workstation.**

| | Level 1 | Level 2 | Level 3 |
|---|---|---|---|
| Solver time | 8–20 h | +33–102 h | +50–500 h |
| Fits 5 days? | **Yes** | **Partially** — prioritised subset only | **No** |

**Realistic 5-day outcome:** Level 1 complete, plus the highest-value parts of Level 2 (mesh
independence and turbulence sensitivity, and a reduced 3-point sweep). Roughly **10–14 CFD runs**,
mostly overnight.

**Therefore, and this must be said plainly:**

> The approved project title promises **installation-effect assessment**. That is **Level 3**, and it
> is **not deliverable in the authorised effort**. The five-day project delivers the *design* and
> *isolated characterisation* half. Until Level 3 exists on disk, the project must be described as
> **"aerodynamic design and isolated characterisation of an open-fan rotor, with installation
> assessment in progress"** — never as a completed installation study.

This is not a de-scoping of ambition; it is a refusal to let the claim outrun the evidence, which
the requirements document makes a Tier-3 violation.

---

## 6. SCHEDULING STRATEGY

The binding resource is **wall-clock**, not effort. Therefore:

1. **Launch the longest run first, overnight, every night.** Four nights ≈ 40 h of otherwise-idle
   solver time — comparable to all of Level 2.
2. **Calibrate before committing** (§1 gate).
3. **Fine mesh once.** No exploratory runs on the fine mesh.
4. **Script every case.** Journal files, not GUI clicks — required for reproducibility, and it makes
   an overnight queue possible. This also protects the GitHub story.
5. **Checkpoint frequently.** A crash at hour 9 of an 11-hour run must not cost the run.
6. **Never coarsen the near-blade mesh to save time.** If a case does not fit, reduce the *number* of
   cases, never the quality of one. Silently degrading mesh quality to hit a deadline is the exact
   failure mode this audit exists to prevent.

---

## 7. WHAT WOULD CHANGE THIS AUDIT

| Trigger | Consequence |
|---|---|
| Calibration shows throughput materially better or worse than estimated | **All of §3 is replaced by measured values** and the levels are re-cut |
| Core count / RAM confirmed different from the inferred 8 cores | Re-cut §3 and §4 |
| Fine mesh exceeds available RAM | Drop to a 3-mesh study capped at the largest mesh that fits; report the reduced refinement ratio honestly |
| Transonic tip convergence proves difficult | Switch to density-based; add iterations; **do not** relax convergence criteria to declare a run finished |
| External compute genuinely becomes available and authorised | Level 3.7 becomes possible — **and only then may a fully-resolved installed result be claimed** |
