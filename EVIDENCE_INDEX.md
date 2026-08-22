# EVIDENCE INDEX — BA-OF-01 Boeing Open-Fan Rotor
### Every major claim, its evidence artifact, verification method, status, and limitations

**Scope note:** this index covers the whole project (design → CAD → CFD preprocessing). It is
distinct from `00_requirements/EVIDENCE_INDEX.md`, which covers only the Phase 0 industry/
research investigation that motivated the project's scope decisions.

---

| # | Claim | Evidence artifact | Verification method | Status | Limitations |
|---|---|---|---|---|---|
| 1 | Blade count (16) is an output of a solidity/aspect-ratio trade, not an assumption | `01_design/results/design_summary.json` → `blade_count_trade` | Inspection of the closed-form solidity formulation across 8–16+ blade counts | VERIFIED | Aspect-ratio bound is a plausibility check, not a structural FEA |
| 2 | Aerodynamic design is internally self-consistent (Gate G0) | `01_design/results/design_summary.json`, `PHASE_1_DESIGN_REPORT.md` §4 | 7 independent closure checks + 41→81 station radial-independence re-run | VERIFIED | Internal consistency only — not experimental validation; `η` is `[CFD-TBD]` |
| 3 | Helical tip Mach (1.0966) is distinct from and exceeds rotational tip Mach (0.80) | `design_summary.json` → `operating_point` | Direct vector-sum calculation, explicit code comment forbidding conflation | VERIFIED (calculation) | Not independently cross-checked against a second code path |
| 4 | Tip sweep (44.66°) is derived from a leading-edge-normal Mach constraint | `design_table.csv` tip row; `openfan_design.py` sweep law | Closed-form calculation from `mn_limit=0.78` | VERIFIED (calculation) | SR-3's ~45° is a plausibility cross-check only, not a target or validation |
| 5 | v01 CAD blade failed gate G1 | `02_cad/cad_verification.json`, `02_cad/verify_cad.py` | Independent reopen + `Check2()`, visual inspection | CONFIRMED FAILURE (documented, not hidden) | — |
| 6 | Root cause of v01's rippling was polyline faceting, not `Check2`'s literal meaning | `02_cad/CAD_CHECK2_DIAGNOSTIC.md`, `diag_two_spline_*.py/json` | Cross-document `Check2` comparison (clean vs. rippled body, same value) + face-count analysis | VERIFIED | `Check2`'s exact bitmask semantics remain undocumented (SolidWorks tooling limitation, reported not guessed) |
| 7 | v02 CAD blade passes gate G1 | `02_cad/cad_verification_v02_G1_independent.json` | Independent reopen in a separate process; 6/6 criteria | VERIFIED | STEP reimport into SolidWorks itself is a separate, unverified claim (#8) |
| 8 | v02 STEP export is valid for ANSYS use | `03_cfd/geometry_transfer/import_test_final.log` (or equivalent) | Fluent Meshing's own CAD import, successful boundary mesh produced | VERIFIED (for the ANSYS path only) | SolidWorks-side STEP reimport still fails (`swFileRequiresRepairError`) — open item O10 |
| 9 | Fluid-domain volume matches analytic wedge-minus-blade expectation | `03_cfd/geometry/domain_verification_v01.json` | Closed-form wedge volume vs. measured Boolean-subtract result | VERIFIED — 0.0006% delta | Geometry-only; predicts nothing about flow |
| 10 | 10 raw CFD boundary zones correctly classified as inlet/outlet/hub/farfield/periodic×2/blade | `03_cfd/zone_definition/ZONE_RECORD.json`, `zone_classification_raw.json` | Area-weighted centroid/normal/area measured per zone, compared to analytic domain geometry | VERIFIED — 0.01–0.16% area agreement | Blade's 4 sub-pieces are a tessellation artifact, correctly merged, not 4 real walls |
| 11 | Periodic interface (θ=0°/22.5°) is topologically valid | `03_cfd/zone_definition/domain_9zones_typed_periodic.msh.h5` | Direct HDF5 read of zone topology (not console-trusted): periodic-1↔shadow-14 (20↔20 faces), periodic-2↔shadow-15 (2↔2 faces) | VERIFIED (topology only) | Solver-side periodic behavior unverified — no case has run |
| 12 | A volume mesh exists | — | — | **NOT VERIFIED — DOES NOT EXIST** | Blocked by a Fluent process-startup stall, see `03_cfd/CFD_STATUS.md` |
| 13 | A CFD solution exists | — | — | **NOT VERIFIED — DOES NOT EXIST** | No mesh, so no solve has been attempted |
| 14 | Rotor thrust/torque/power/efficiency has been predicted by CFD | — | — | **NOT VERIFIED — DOES NOT EXIST** | The `η=0.8072` figure in the design output is a BEM estimate, explicitly labeled `[CFD-TBD]` |
| 15 | Design validated against experimental or published data | — | — | **NOT VERIFIED — NOT ATTEMPTED** | Caradonna–Tung / UIUC data identified as candidate benchmarks, not yet used |
| 16 | Installed-configuration performance | — | — | **NOT VERIFIED — NOT ATTEMPTED** | No installed geometry exists |

---

## How to use this index

- A row marked **VERIFIED** means an artifact exists and a stated, reproducible method was used
  to check it — re-run the cited script to reproduce the check.
- A row marked **NOT VERIFIED — DOES NOT EXIST** or **NOT ATTEMPTED** is a claim this project is
  explicitly *not* making yet. If a future session's output ever implies otherwise for one of
  these rows without a new artifact and method added here, that is overclaiming and should be
  corrected before anything is published or shown externally.
- When new work closes one of the open rows (12–16), add a new row rather than editing an old
  one, and update `PROJECT_STATUS.md`'s "last verified milestone" line to match.
