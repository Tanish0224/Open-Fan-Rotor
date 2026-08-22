# PHASE 1 (G0) AND CAD RECOVERY (G1) — FINAL REPORT
### BA-OF-01 — Open-Fan Rotor

**Created:** 22 August 2026 · **Scope:** design generation through CAD recovery. **CFD not started.**

---

## A. DESIGN GENERATION (Phase 1)

Unchanged from `PHASE_1_DESIGN_REPORT.md`, which this report does not repeat in full. Summary:
actuator-disk sizing → Adkins–Liebeck minimum-induced-loss BEM with Prandtl tip/hub loss →
sweep derived separately from the helical-Mach field. **Gate G0: PASS** — all five closure checks
and the radial-station independence study passed, `η` route agreement 1.4×10⁻¹⁴ %. Blade count
(16) and sweep (44.7°, cross-checking NASA SR-3's published 45°) are **outputs** of the method, not
assumptions. No design parameter was touched during this recovery task.

## B. BLADE CAD GENERATION (v01)

Parametric SolidWorks build (`build_rotor_cad.py`) driven entirely by the Phase 1 radial table:
each of 21 stations resampled to 48 arc-length points, sketched as a 48-segment polyline on a
Right-Plane offset, lofted through all 21 sections in one feature. Saved as `openfan_blade_v01.
SLDPRT`. **Preserved unchanged as historical evidence — not deleted, not overwritten.**

## C. CAD FAILURE

Independent verification (`verify_cad.py`, separate process, reopened the saved file) found:
volume within 1.52 % of an independent analytical target (PASS), radial extent correct to 10⁻⁷ m
(PASS), save/reopen identical (PASS) — but **`Check2() = 6`**, where every known-good reference
body in this project's history returns 0 (FAIL). Visual inspection of the reopened part showed
visible chordwise rippling. **Gate G1: FAIL**, 5 of 6 criteria passing.

## D. ROOT-CAUSE DIAGNOSIS

Executed in this order, each step recorded in `CAD_CHECK2_DIAGNOSTIC.md`:

1. **RAM cleanup first** (explicit user instruction, priority over diagnosis). 11 open SolidWorks
   documents audited before any closure. Classified: 7 trivial/failed 0-solid diagnostic leftovers
   (closed, undocumented nothing was lost — already recorded in existing `diag_*.json` files);
   2 duplicates of the saved v01 geometry (closed); 1 coarse 3-section diagnostic loft, **Part33**
   (saved to `diagnostics_archive/`, not left anonymous); 1 full-blade loft, **Part65**, bit-
   identical to the already-saved `openfan_blade_v01.SLDPRT` (closed, no new information lost).
   **11 → 0 documents open**, evidence captured before every closure.
2. **`Check2`'s meaning investigated from SolidWorks' own type library** (`pythoncom.LoadTypeLib`
   against `swconst.tlb`/`sldworks.tlb`, not a third-party writeup). Finding: no named enum
   corresponds to the bitmask; its CHM documentation exists locally but could not be extracted
   (`hh.exe -decompile` produced zero files, twice — a real, reported tooling limitation).
3. **The decisive empirical cross-check, gathered before closing anything:** `Check2 = 6` on
   **both** Part33 (visually clean, 3 sections, 27 faces) and Part65/v01 (visibly rippled, 21
   sections, 50 faces). **The code does not discriminate the defect** — it is common to the
   construction *method*.
4. **`Check3`** (would return a `FaultEntity` locating the exact fault) attempted with three
   calling conventions — all `'Member not found'`, a genuine tooling limitation, reported as such.
5. **Face-count evidence located the real cause:** 50 faces / 48 non-planar across only 20
   spanwise gaps in v01 — a faceted/ruled surface between corresponding straight polyline segments
   on adjacent profiles, not one smooth patch per span.

## E. GEOMETRY REPAIR

**No design parameter changed.** Same reference planes, same authoritative design-table points,
same blunt TE, same span. Only the sketch entity type changed:

1. **Two open smooth splines per section** (upper TE→LE, lower LE→TE, sharing exact endpoints)
   replace the 48-segment polyline. A single *closed* spline was tried first and failed to loft at
   all — consistent with B-spline overshoot at the sharp blunt-TE corner (an interior control
   point on a closed curve, but only a curve *endpoint* — never overshot — when split in two).
   Verified on a fast 3-profile probe first: `Check2` 6→0, faces 27→4.
2. **A second, unrelated problem** surfaced scaling to 21 profiles: the single-feature loft failed
   even though 3 and 5 evenly-spread profiles worked. Binary search located the break between 5
   and 8 profiles; further isolation found the exact 5-station root cluster `[0,1,2,3,4]` fails
   while every 4-station sub-combination of the same data succeeds — a SolidWorks loft-engine
   limit on many closely-spaced, rapidly-twisting profiles, not a defect in any individual profile.
3. **Fix: 7 independent lofts of ≤4 profiles each** (1-station overlap, full 21-station coverage),
   combined into one solid using this project's own **proven** Boolean-ADD recipe
   (`_SolidWorks_API_Final_Automation_Test/sw_auto.py::combine_add`).

## F. FINAL VERIFICATION

Independent, separate-process re-open (`verify_cad_v02.py`), plus a full topology dump:

| Criterion | Result |
|---|---|
| Exactly 1 solid body | ✅ 1 |
| Zero unintended surface bodies | ✅ 0 |
| `Check2()` matches known-good reference | ✅ **0** |
| Volume vs **independent bracket** (computed from the exact CAD-input points, without SolidWorks) | ✅ 1600.60 cm³, inside [1594.01, 1611.19] cm³ |
| Radial root/tip extent vs design | ✅ ~1.3×10⁻⁵ m / ~1.1×10⁻⁵ m |
| No negative/degenerate bounding box | ✅ confirmed (directly catches the v01 wrong-axis-spinner failure mode) |
| Save → close → reopen identical | ✅ 0.0 % |
| No unresolved O6 blocker | ✅ O6 closed |

**All 8 criteria pass. Gate G1: PASS.** Face count dropped from 50 (48 non-planar) to **16** (14
non-planar = 7 windows × 2 spline surfaces + 2 planar caps), and visual inspection
(`diagnostics_archive/blade_v02_iso.png`) shows a smooth, twisted, swept blade with no rippling.

## G. CAD EXPORT

- **Native SLDPRT** (`openfan_blade_v02_G1_VERIFIED.SLDPRT`) — the authoritative, G1-verified
  master. All downstream work should use this file.
- **STEP** (477,222 bytes) — writes successfully, but reopening it triggers a **decoded**
  `swFileRequiresRepairError` (from `swconst.tlb`, not guessed) across every `OpenDoc6` option
  tried. **Not verified for reimport.** Open item **O10**. Does not affect the native master.
- **STL** (107,984 bytes) — exists; explicitly **not** claimed as a high-fidelity engineering
  interchange format, only a tessellated visualisation.

## H. PRESENTATION ROTOR STATUS

**Deferred, not built.** Three independent, low-risk API paths were attempted and all failed with
the identical symptom (`'Member not found'` on methods declared in the reflected type library but
not reachable via late binding on this install): in-part `FeatureCircularPattern4/5` (axis
selection every route), and body-copy + `IMathUtility.CreateTransformRotateAxis`. This is the same
pattern already confirmed twice this session (`InsertAxis2`, `Check3`) — an installation property,
not a fixable code bug, and continuing to chase it was judged, per the recovery brief's own
guidance, not a good use of remaining time. The verified single blade
(`diagnostics_archive/blade_v02_iso.png`) is the presentable CAD deliverable in its place.

## I. ANSYS READINESS

Toolchain confirmed present (Fluent 2025 R1, Workbench). Geometry route into ANSYS is **not yet
verified** — the STEP reimport issue (item O10) must be resolved or bypassed first. CFD methodology
(steady SRF, compressible, k-ω SST, `y⁺≈1`, 22.5° sector) is unchanged from before this recovery
and is documented in `03_cfd/ANSYS_READINESS_NOTE.md`. **No mesh, no run, no CFD result exists.**

## J. UNRESOLVED ITEMS

| ID | Item | Status | Blocks |
|---|---|---|---|
| **O7** | Fluent licensed parallel core count unconfirmed | `INVESTIGATING` | Runtime estimates only |
| **O8** | 16-blade pattern — installation-level API limitation | `BLOCKED` | Visualisation only |
| **O9** | Spinner/hub — deferred after a prior gate-G1 catch | `BLOCKED` | Not required for the CFD sector case |
| **O10** | STEP export reimport unverified | `INVESTIGATING` | STEP-based downstream tools; native SLDPRT unaffected |

---

## ANSWERS TO THE REQUIRED QUESTIONS

**1. What caused `Check2 = 6`?**
The precise bit meaning was never decoded (SolidWorks' own type library has no symbolic enum for
it, and its CHM documentation could not be extracted locally). But it was proven, empirically, to
be common to the *construction method* (polyline-profile lofts), not a marker of the specific
visible defect — it appeared identically on a visually clean loft and a visibly rippled one.

**2. Was the original diagnosis correct?**
Partially. "Check2=6 means invalid geometry" was literally accurate (that is the method's stated
purpose) but implied the code was diagnostic of the rippling specifically, which the cross-document
comparison disproved. The rippling's actual cause — faceted polyline profiles — was a separate,
independently-established finding from face-count evidence.

**3. What changed in v02?**
Only the sketch entity type (two open splines instead of a polyline per section) and the loft
strategy (7 segmented lofts + Boolean ADD instead of one 21-profile loft). No design parameter,
no reference plane, no blunt-TE value, no span, no sweep/twist/chord changed.

**4. What aerodynamic geometry changed, if anything?**
Nothing. The BEM design (Phase 1, gate G0) is completely unaffected by this recovery.

**5. What independent evidence proves the corrected geometry is valid?**
Reopening the saved file in a separate process and finding: `Check2()=0` matching every known-good
reference body in this project; a volume falling inside a bracket computed without SolidWorks from
the exact CAD-input points; correct radial extent; a non-degenerate bounding box; identical
geometry after save/close/reopen; and a visual record showing no rippling.

**6. What is the final volume and independent reference volume?**
Final CAD volume: **1600.60 cm³**. Independent reference: a **bracket** `[1594.01, 1611.19] cm³`
(polygon lower bound / smooth closed-form upper bound), not a single point — because the CAD
surface is spline-based and a spline through the same points bulges outward relative to a
polyline, so a bracket, not a single target, is the honest comparison. The CAD volume falls inside
it, closer to the lower bound, exactly as expected for a fine (48-point) discretisation.

**7. Does G1 PASS?**
**Yes.** All 8 acceptance criteria, verified independently in a separate process.

**8. Does a 16-blade presentation rotor exist?**
**No.** Deferred as an installation-level API limitation, honestly documented (item O8), not built.

**9. Are CAD artifacts now ready to show on GitHub?**
**Yes**, for the single verified blade: native SLDPRT (G1-verified), a clean isometric screenshot,
and the full diagnostic trail demonstrating real engineering debugging. **Not yet** for STEP
(unverified reimport, O10) or the 16-blade pattern (not built, O8).

**10. What exactly is the next CFD task?**
Resolve or bypass the STEP reimport issue (O10), build a fluid-domain derivative around the
verified blade (never modifying the master), generate the coarse mesh (~0.9 M cells) from the
already-cut triplet, run the mandatory timing calibration, then execute the already-generated
Fluent journal (`03_cfd/cases/CFG-ISO/setup_iso_sector.jou`) as an explicitly labelled
**PRELIMINARY** workflow-demonstration run grounding no performance claim.
