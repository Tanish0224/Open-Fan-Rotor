# ENGINEERING DECISION LOG
### BA-OF-01

**Created:** 22 August 2026
**Status values:** `PROPOSED` · `INVESTIGATING` · `CONFIRMED` · `REFUTED` · `BLOCKED`
**Rule:** a decision is marked `CONFIRMED` only when the evidence genuinely supports it. A decision
that is merely *chosen* — with no evidence yet — stays `PROPOSED`. Refuted decisions are **preserved
intact**, never deleted.

---

## ED-001 — Project architecture

**Status:** `CONFIRMED`
**Decision:** A **single-rotation open (unducted) rotor**, full engine scale, no duct, no OGV in the
baseline, analysed isolated and (Stage 3) wing-installed.
**Evidence:** CFM public architecture (single rotating variable-pitch fan + stationary OGV, geared);
parent research §11–13 candidate analysis.
**Reasoning:** Matches the architecture actually under development, and is the minimum configuration
that supports the research question.
**Consequence:** Naming must say **"rotor"**, not "propulsor" or "stage" — see ED-008.

---

## ED-002 — Primary research question

**Status:** `CONFIRMED`
**Decision:** *For a single-rotation open-fan rotor at a fixed design point and fixed operating
condition, what is the change in net propulsive force and propulsive efficiency between isolated and
wing-installed configurations, and how does it decompose into altered rotor inflow, altered wing
forces, and non-linear interference?*
**Evidence:** GE+Boeing+NASA+ORNL 840 000 INCITE node-hours on installed open-fan simulation (Nov
2024); Airbus mounting position undecided as of Jul 2026; Boeing US 12,698,086 (Aug 2026); A380
test objectives naming "thrust, drag, loads".
**Reasoning:** The uninstalled advantage follows from momentum theory and is not disputed. The
installed retention is disputed and is what governs the architecture decision.
**Explicitly rejected alternative:** a generic ducted-vs-open comparison — lowest-scoring candidate
(3.95/10) in the parent research; uncontrollable and industry-settled. **Permanently excluded.**

---

## ED-003 — Primary comparison and its control

**Status:** `CONFIRMED`
**Decision:** CFG-ISO vs CFG-INST, with CFG-WING as the linear reference. Held identical: blade
geometry, blade count, diameter, pitch, shaft speed, flight Mach, altitude, fluid properties,
turbulence model, near-blade mesh topology and sizing. **Only the wing changes.**
**Reasoning:** A single-variable comparison is the one thing candidate C1 could never achieve, and
it is what makes the result defensible.
**Gate:** G5. Any deviation voids the comparison.

---

## ED-004 — Rotor design methodology

**Status:** `CONFIRMED`
**Decision:** Actuator-disk sizing → **Adkins–Liebeck minimum-induced-loss BEM** with Prandtl
tip/hub loss and a compressibility correction → **sweep layered on separately**, derived from the
computed `M_hel(r)` distribution.
**Options rejected:** momentum-only (no blade); uncorrected BEM (over-predicts tip loading exactly
where this rotor is most critical); lifting-line / CFD-in-the-loop inverse design (would make CFD a
design tool and destroy its role as an independent check).
**Reasoning:** Published, closed-form, fully derivable. Interview-defensible line by line.
**Known weakness, accepted and recorded:** BEM sectional aerodynamics is invalid at the transonic
tip (`M_hel` 1.10 vs Prandtl–Glauert validity `M_n ≲ 0.7`). **This is why the CFD comparison is a
genuine test rather than a formality.**

---

## ED-005 — Installation configuration

**Status:** `CONFIRMED`
**Decision:** **Tractor rotor ahead of a wing segment**, no upstream pylon, zero aircraft AoA in the
baseline installed case.
**Options rejected and why:**
- *Pusher / upstream pylon* — **rejected on method.** Its defining mechanism (a blade cutting a
  viscous wake) is inherently unsteady and requires full-annulus URANS.
- *Over-wing (Boeing patent architecture)* — **rejected on scope.** Requires simultaneous credibility
  in transonic wing design and propulsor aerodynamics; no validation data.
- *Rear fuselage* — rejected; needs a fuselage and boundary-layer ingestion.
- *Wingtip-mounted* — **rejected on premise**, despite having the best available validation data.
  Choosing a configuration because data exists rather than because it is the right question was
  explicitly refused.
**Deciding reason:** the tractor is the **only** candidate in which the rotor's operating point can
be genuinely held constant while the airframe is added, and in which the wing's influence is a
smooth potential perturbation rather than a wake cut — which is what makes a steady method
legitimate.
**Deliberate consequence:** no upstream pylon in the baseline, because adding one would reintroduce
the very mechanism just rejected.

---

## ED-006 — Benchmark and verification approach

**Status:** `CONFIRMED`
**Decision:** Two-axis validation on **fully public, no-request** benchmarks:
- **Axis A (mandatory):** Caradonna–Tung (NASA TM-81232) — compressible rotating blade, transonic
  tip `M_tip` 0.877.
- **Axis B (recommended):** UIUC Propeller Database — axial-flight `C_T`/`C_P`/`η` vs `J`.
**Rejected:** PANDORA (CFD, not experiment; terms unverified); TU Delft PROWIM/XPROP (restricted,
request could be refused — user decision); F31/A31 and SR-2/SR-3 (**geometry not confirmed public**,
so the case cannot be reproduced).
**Recorded correction:** this **overturns the parent research's recommendation** of SR-2/SR-3 and
F31/A31 as the validation path. The parent research is preserved unedited; the correction lives here
and in the evidence index.
**Accepted residual gap, to be stated unprompted:** no public benchmark covers **compressible *and*
axial flight simultaneously** — the actual design condition. The two benchmarks bracket it.

---

## ED-007 — CFD modelling approach

**Status:** `CONFIRMED`
**Decision:** ANSYS Fluent; steady RANS; rotating frame / MRF; **periodic sector for isolated**
(exact, `B`× cheaper) and **full annulus for installed** (unavoidable); **fully resolved blades
isolated**, **body-force rotor installed** on the workstation path, calibrated against the resolved
isolated result; compressible ideal gas, pressure-based coupled, second order; k-ω SST with
Spalart–Allmaras sensitivity; `y⁺` ≈ 1 target for reported cases.
**Reasoning:** Steady is *exact* for the isolated case and a declared approximation for the
deliberately-chosen installed configuration. The body-force choice is forced by the feasibility
audit, not preferred.
**Accepted consequence:** blade-level installed claims are **withdrawn**, not softened — secondary
question S3 is downgraded to disk-plane inflow non-uniformity unless the resolved stretch case runs.

---

## ED-008 — No outlet guide vane in the baseline

**Status:** `CONFIRMED`
**Decision:** **No OGV.** Swirl recovery is not a project metric. Residual swirl is retained as a
**diagnostic** only.
**Evidence:** TU Delft swirl-recovery results span **+0.20 %, +0.39 %, +0.7 %, +2.4 %, +2.62 %,
+3.07 %** depending on design and condition, with a **+20 dB** axial noise penalty.
**Reasoning:** (a) second-order relative to the installation effects under study; (b) the literature
spread is an order of magnitude, so no single number could be honestly quoted; (c) the benefit is
bundled with an acoustic penalty this project cannot model; (d) it doubles CFD cost without
addressing the research question.
**Consequence:** the object of study is an open-fan **rotor**, not a complete propulsor or stage.
All project text, README and resume wording must say "rotor". The approved resume statement already
does.
**Reclassified as:** FUTURE WORK.

---

## ED-009 — Design point

**Status:** `PROPOSED` — *not confirmed; several parameters unsourced*
**Decision (provisional):** `M₀` = 0.75, 35 000 ft ISA, `D` = 3.5 m, rotational tip Mach 0.80 ⇒
`N` = 1294 rpm, `M_hel,tip` = **1.10**, `J` = 2.95.
**Closure check:** actuator-disk `η_p,ideal` = 0.9500 vs `C_T·J/C_P` = 0.9497 — **0.03 % agreement**,
so the set is arithmetically self-consistent.
**Why not CONFIRMED:** design thrust (**B1**) has no primary source, blade count is a placeholder,
hub/tip ratio and airfoil family are unset. **The set is consistent, not sourced.**
**Blocking items:** B1 (thrust — preferred fix is to invert to a prescribed disk loading), B2
(airfoil polar data availability).

---

## ED-010 — Computational scope and staging

**Status:** `CONFIRMED`
**Decision:** Workstation-only baseline; three feasibility levels; **mandatory timing-calibration
run before any expensive phase**; institutional HPC is not a dependency and **may not be claimed**.
**Evidence:** this project's cases are 3-D at 10⁶–10⁷ cells. Estimated fully-resolved installed
case: **50–65 M cells, 100–330 h, ~90–150 GB**. Machine core count and RAM are **unconfirmed**
(open item O1), so the estimates must be replaced by a measured calibration before commitment.
**Consequence, recorded plainly:** the approved title's **installation half is Level 3 and is not
deliverable in the authorised ~5 days.** Until it exists, the project is described as *"aerodynamic
design and isolated characterisation of an open-fan rotor, with installation assessment in
progress."*

---

## ED-011 — Thrust–drag bookkeeping convention

**Status:** `CONFIRMED`
**Decision:** **BK-1** — thrust = axial force on rotating surfaces (blades + spinner); drag = axial
force on stationary surfaces; scrubbing drag lands on the **airframe**. Net propulsive force
`NPF = T_rot − D_stat` is the reported quantity.
**Reasoning:** maps onto a physically identifiable surface (what rotates), so it is unambiguous and
third-party reproducible.
**Declared weakness:** it **flatters the propulsor** — a rotor that badly scrubs the wing shows no
thrust penalty.
**Mandatory mitigation:** report `NPF`, never `T` alone, for installed cases; repeat under **BK-2**
(control-volume momentum balance) as a sensitivity. **If the conclusion's sign changes between
conventions, that becomes the headline finding.**

---

## ED-012 — Claim discipline

**Status:** `CONFIRMED`
**Decision:** Adopt the three-tier claim hierarchy of `PROJECT_REQUIREMENTS.md` §7.2. No claim may
be promoted between tiers without the evidence artifact existing on disk.
**Reasoning:** An honestly-reported gate failure is a stronger portfolio asset than an engineered
pass, because it demonstrates verification discipline. Structural enforcement, not good intentions.
**Specific standing prohibitions:** no acoustic claim; no fuel-burn claim; no "optimised"; no
RISE comparison; no institutional-HPC claim; no installation claim before Stage 3 exists.


---

## ED-009-R1 - Design point REVISED: non-dimensional loading replaces design thrust

**Status:** `CONFIRMED` - **Supersedes:** the thrust-based part of ED-009 (22 Aug 2026)
**Decision:** the design input is the non-dimensional loading
`tau = T/(rho*A*V0^2) = 0.08` `[DESIGN DECISION]`. Thrust in newtons is now an **output**,
obtained by dimensional interpretation at the end of the chain.
**Reason:** blocking item **B1** could not be closed by sourcing a cruise thrust - no primary
source was available, and the Boeing RFI ~30 klbf figure is a **sea-level static** rating, a
different quantity. Rather than carry an unsourced number, the requirement was removed from the
chain entirely, per the Phase 1 authorisation.
**Consequence:** the 20 kN placeholder is **deleted from the project**. `tau` sets the
actuator-disk efficiency ceiling directly (0.9629), a cleaner and fully-owned design input.
**B1 is CLOSED.**

---

## ED-013 - Airfoil section family

**Status:** `CONFIRMED` - **Closes:** blocking item **B2**
**Decision:** **NACA 4-digit series**, with a **blunt trailing edge** of 0.006 c.
**Reason:** its geometry is defined by published closed-form equations, so it is reconstructable to
machine precision with **no request-only data** - the criterion set by the Phase 1 authorisation.
Sectional Cl comes from thin-airfoil theory at the ideal (shock-free entry) angle; camber is solved
analytically to deliver the design Cl.
**Recorded limitation:** NACA 4-digit is **not** a high-critical-Mach propeller family (NACA
16-series would be). Exact public reconstructability was traded for aerodynamic optimality,
deliberately. CFD will quantify the penalty. **No polar has been extrapolated into the transonic
regime.**
**Blunt TE reason:** the zero-thickness TE of the closed polynomial produced invalid solid geometry
after resampling, and cannot carry CFD prism layers. A finite TE is also what a real composite blade
has. **B2 is CLOSED.**

---

## ED-014 - Blade count = 16, and two selection criteria that were wrong

**Status:** `CONFIRMED` - **Closes:** open item **O2**
**Decision:** **B = 16**, selected as an **output** of a 7-candidate trade study.
**Two findings that corrected the selection method:**
1. **Local solidity is very nearly independent of blade count.** Adkins-Liebeck chord scales as 1/B
   at fixed loading, so sigma = Bc/(2 pi r) is set by tau, lambda and design Cl - not by B. Solidity is
   therefore a feasibility bound on the *design* and **cannot discriminate between blade counts**.
   A chord/diameter criterion was added.
2. **A "tip chord >= 0.05 R" criterion can never pass** - Adkins-Liebeck drives chord to zero at the
   tip by construction (Prandtl F -> 0). It was structurally invalid and was replaced by a
   chord-at-0.90R test.
**Tie-break `[DESIGN DECISION]`:** the smallest blade count within 0.5 % of the best selectable
efficiency - efficiency rises monotonically with B but with strongly diminishing returns, and each
extra blade costs weight, cost and complexity.
**Downstream consequence:** the CFD periodic sector is **22.5 deg**, not the 30 deg assumed when
B = 12 was a placeholder - roughly 25 % fewer cells.

---

## ED-015 - Sweep law

**Status:** `CONFIRMED`
**Decision:** Lambda(r) = arccos(M_cap / M_hel(r)) with M_cap = 0.78 `[DESIGN DECISION]`, giving
**44.7 deg of tip sweep**.
**Reason:** BEM is strip theory and cannot produce sweep (limitation L4), so sweep is a separate
geometric decision requiring its own physical justification - holding the leading-edge-normal Mach
below a cap. M_cap is set marginally above the flight Mach so the inboard blade, where M_hel is
dominated by M0, stays essentially unswept.
**Cross-check (NOT a validation):** NASA's SR-3 propfan, a real M0.8 design, used **45 deg** of tip
sweep. Nothing was tuned to match it; the agreement follows from imposing the same physical
constraint. It must always be described as a cross-check, never as validation.

---

## ED-016 - SolidWorks loft: root cause and the resulting CAD parameters

**Status:** `CONFIRMED`
**Problem:** InsertProtrusionBlend2 returned a clean None for every aerofoil profile variant tried.
**Diagnosis by elimination** (preserved in `02_cad/diag_*.py` and `diag_*.json`):
1. Arity is **18** on this install, not the documented 17 (17 raises 'Parameter not optional').
2. A loft through two trivial circles **succeeded** -> the API and call signature are correct.
3. **Root cause: section point density.** Measured threshold - 48 points per section lofts cleanly
   through all 21 profiles; **64 fails**; the raw 201-point cosine-clustered section fails outright.
   Many short, nearly-collinear segments inside a sketch whose extent is ~0.7 m (the sweep offset)
   defeat SolidWorks' contour detection, so the contour never closes.
4. InsertAxis2 **does not exist** on this install; a sketched construction line along global Z is
   used as the pattern axis instead.
**This is a second independent confirmation of the S36.6 interpretive rule:** a clean None meant
"input underdetermined", exactly as the rule predicts - **not** a broken API. Applying the rule is
what led to the root cause instead of a false API-limitation conclusion.
**Resulting parameters:** N_SKETCH_PTS = 48 (uniform arc-length resampling), TE_THICKNESS = 0.006 c,
sections as 2-D sketches on Right-Plane offsets with the mapping local (a, b) -> global (Y = a,
Z = b) **verified geometrically** by bounding box.

---

## ED-017 - Platform measured; feasibility re-cut

**Status:** `CONFIRMED` - **Closes:** open item **O1**
**Measured 22 Aug 2026:** AMD Ryzen 7 6800H, **8 physical cores**, **15.2 GB RAM**, ANSYS Fluent
2025 R1.
**Consequence:** at ~2 GB per million cells for a coupled compressible solve and ~12 GB usable, the
practical ceiling is **~5 M cells**. The 6.5-8.5 M "fine" mesh assumed before the hardware was
measured is **NOT achievable** and has been **withdrawn**. The mesh-independence triplet is re-cut
to **0.9 M / 2.0 M / 4.3 M** (constant linear refinement ratio ~1.30).
**This is exactly the failure the calibration gate exists to catch, and it was caught before any
expensive case was launched.**
**Still open:** Fluent's licensed parallel core count is unconfirmed; if capped at 4, every runtime
estimate roughly doubles.


---

## ED-018 - CAD G1 recovery: two-spline segmented loft (v02 supersedes v01)

**Status:** `CONFIRMED`
**Problem:** v01 (`openfan_blade_v01.SLDPRT`, polyline-profile loft) failed gate G1: `Check2()=6`
where all known-good reference bodies return 0, and the saved geometry showed visible chordwise
rippling on visual inspection.

**Diagnosis, evidence-first, before any geometry change** (`CAD_CHECK2_DIAGNOSTIC.md`):
- SolidWorks' own type library (`swconst.tlb`, `sldworks.tlb`, reflected directly via
  `pythoncom.LoadTypeLib`) has NO named enum for Check2's return bitmask; its CHM help file could
  not be extracted locally (`hh.exe -decompile` produced zero files, twice) -- a genuine, reported
  tooling limitation, not a fabricated result.
- **Decisive empirical finding:** every open SolidWorks document with a solid body, inspected
  BEFORE any cleanup, showed `Check2()=6` -- including a visually clean 3-section coarse diagnostic
  loft. Check2=6 does NOT discriminate the rippling defect; it is common to the construction
  METHOD (polyline profiles), not proof of the visible defect specifically.
- Face-count evidence: the 21-section polyline blade had 50 faces (48 non-planar) across only 20
  spanwise gaps (~2.4 facets/span) -- consistent with a RULED/FACETED surface between corresponding
  straight segments on adjacent profiles, not one smooth patch per span.
- `IBody2::Check3` (would return a `FaultEntity` pinpointing the exact defect) was attempted with
  three calling conventions; all failed `'Member not found'` despite being declared in
  `sldworks.tlb` -- a genuine, reported tooling limitation on this install.

**Fix (Option C, least invasive, NO design parameter changed):** each section rebuilt as TWO OPEN
SMOOTH SPLINES (upper TE->LE, lower LE->TE) sharing exact endpoints, instead of a 48-segment
polyline. A single CLOSED spline was tried first and failed to loft at all (self-intersection
hypothesis: B-spline overshoot at the sharp blunt-TE corner, an interior control point on a closed
curve but a curve ENDPOINT -- never overshot -- when split into two open splines).

**Second problem found and fixed:** lofting all 21 two-spline profiles in one feature failed (0
solids) even though 3 and 5 profiles, evenly spread across the full span, succeeded. Binary search
(`diag_two_spline_scaling.py`) found the break between 5 and 8 profiles; further isolation
(`diag_root_window.py`) showed the exact 5-station group [0,1,2,3,4] (root region, highest t/c)
fails while every 4-station sub-combination of the same data succeeds -- a SolidWorks loft-engine
limit on many closely-spaced, rapidly-twisting profiles, not a defect in any individual profile.
**Fix: 7 independent lofts of <=4 profiles each (1-station overlap, full coverage), combined with
the project's own PROVEN Boolean-ADD recipe** (`_SolidWorks_API_Final_Automation_Test/sw_auto.py::
combine_add`: SOLIDBODY select, mark=2, `InsertCombineFeature(SWBODYADD, NULL, NULL)`).

**Result, independently verified in a separate process** (`verify_cad_v02.py`):
`Check2()=0` (matches every known-good reference body); 1 solid body, 0 surface bodies; volume
1600.60 cm^3, falling inside an independently-computed bracket [1594.01, 1611.19] cm^3 (polygon
lower bound / smooth closed-form upper bound, computed from the exact final CAD input points,
without SolidWorks -- see `CAD_VOLUME_CROSSCHECK.md`); radial extent correct to ~1e-5 m; no
negative/degenerate bounding box (directly catches the v01 wrong-axis-spinner failure mode);
save-close-reopen identical. **Gate G1: PASS, all 8 acceptance criteria.**

**Artifact:** `openfan_blade_v02_G1_VERIFIED.SLDPRT` supersedes `openfan_blade_v01.SLDPRT` as the
CFD master. **v01 is PRESERVED, not deleted** -- historical evidence of the diagnosed failure mode.

**Deferred, honestly, not silently:**
- **16-blade presentation pattern** -- three independent low-risk API paths (in-part
  `FeatureCircularPattern4/5`, `IMathUtility.CreateTransformRotateAxis` for body-copy) all failed
  `'Member not found'` on methods declared in the reflected type library but not reachable via late
  binding on this install -- the same pattern as `InsertAxis2` and `Check3`. This is a property of
  the installation, not a fixable code bug, and further chasing it was judged not to be a good use
  of time per the recovery brief's own guidance. Open item **O8**, unchanged in kind, updated with
  the new evidence.
- **STEP export reimport** -- the file writes successfully (477,222 bytes) but reopening it via
  `OpenDoc6` returns a **decoded** error, `swFileRequiresRepairError` (from `swconst.tlb`, not
  guessed), across every `Options` value tried. This does not affect the native SLDPRT master,
  which remains independently G1-verified. New open item **O10**.

**Why this belongs in the decision log, not just a CAD note:** it is the second independent
confirmation (after ED-016) that this install exposes API surface in its type libraries that is
not actually callable via late binding, and that the correct response -- per S36.6 -- is to keep
testing narrower hypotheses on PROVEN-working primitives (as with the segmented loft) rather than
assuming either "the API is broken" or "my geometry is wrong" without evidence.

---

## OPEN ITEMS

| ID | Item | Status | Blocks |
|---|---|---|---|
| ~~**B1**~~ | ~~Design thrust unsourced~~ | **CLOSED** (ED-009-R1) - removed from the chain; loading is now non-dimensional | - |
| ~~**B2**~~ | ~~Airfoil polar data unconfirmed~~ | **CLOSED** (ED-013) - NACA 4-digit, exactly reconstructable, no external data | - |
| ~~**O1**~~ | ~~Core count and RAM not measured~~ | **CLOSED** (ED-017) - 8 cores, 15.2 GB; fine mesh re-cut | - |
| ~~**O2**~~ | ~~Blade count must be an output~~ | **CLOSED** (ED-014) - B = 16 from the trade study | - |
| ~~**O3**~~ | ~~Hub/tip ratio unset~~ | **CLOSED** - 0.28 `[DESIGN DECISION]` | - |
| ~~**O6**~~ | ~~Lofted blade reports `Check2() = 6`~~ | **CLOSED** (ED-018) - root cause was polyline-profile faceting, NOT geometric invalidity of the design; fixed by two-spline segmented loft, v02 Check2()=0 | - |
| **O7** | Fluent licensed parallel core count unconfirmed | `INVESTIGATING` | Every runtime estimate |
| **O9** | Spinner/hub revolve used the Front-Plane mapping without verifying it, revolved about global X instead of Z, and with Merge on absorbed the blade (0.839 m3 vs 0.00161 m3 target). **Caught by gate G1.** Removed from the build; its revolve axis must be verified geometrically before reuse | `BLOCKED` | Spinner geometry only. Not a CFD blocker -- the hub is a boundary surface in the sector case |
| **O8** | 16-blade circular pattern not achieved: in-part pattern API (InsertAxis2/axis-by-sketch/Select4) AND body-copy+transform (IMathUtility.CreateTransformRotateAxis) both fail 'Member not found' on methods declared in sldworks.tlb but not reachable via late binding on this install. Same pattern as InsertAxis2/Check3 (ED-016, ED-018) -- an installation property, not a fixable code bug | `BLOCKED` | Full-rotor visualisation only. **Not** a CFD blocker -- CFD needs the single-blade 22.5 deg sector, which is v02 G1-VERIFIED |
| **O10** | STEP export of v02 (`openfan_blade_v02_G1_VERIFIED.step`, 477,222 bytes) triggers a decoded `swFileRequiresRepairError` on reimport via OpenDoc6, across every Options value tried. Native SLDPRT master unaffected and remains G1-verified | `INVESTIGATING` | STEP-based downstream tools only; the native SLDPRT is the authoritative CFD-geometry source |
| **O4** | Wing section, offsets, rotation direction | `PROPOSED` | Stage 3 only |
| **O5** | PANDORA download terms unverified | `INVESTIGATING` | Nothing — optional cross-check only |
