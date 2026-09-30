# Evidence index

This index says where each major claim comes from.

**Evidence classes.**

| Class | Meaning |
|---|---|
| **PRIMARY** | a recorded file produced by the design code, CAD gate, solver or its extraction, published unchanged |
| **DERIVED** | computed for this repository from primary data (the source is stated). The comparison scripts are published; the scripts that extracted the residual histories, y⁺ statistics and sectional and loading files are not (see `reproducibility/REPRODUCE.md`) |
| **DESIGN INTENT** | a BEM/analytical design value, not a measurement |
| **DIAGNOSTIC** | a real result that answers a diagnostic question, not a performance question |
| **HISTORICAL** | superseded, kept for the record |

"Register" means `reproducibility/unpublished_evidence_register.json`: a file that exists, identified by name and
SHA-256, but is not published.

## Design

| Claim | Class | Evidence | Method |
|---|---|---|---|
| Design point: Mach 0.75, 10,668 m, D 3.5 m, tip Mach 0.80, τ 0.08 | DESIGN INTENT | `design/results/design_summary.json` (`inputs`, `operating_point`) | defined requirements |
| Helical tip Mach 1.0966; 1294.49 rpm | DESIGN INTENT | `design_summary.json` → `operating_point` | calculation (re-runs identically) |
| 16 blades chosen from a trade study | DESIGN INTENT | `design/results/blade_count_trade.csv`; `run_phase1_design.py` | aspect-ratio and chord bounds + 0.5 % efficiency tie-break |
| Tip sweep 44.66° | DESIGN INTENT | `design/results/design_table.csv` | cos Λ = 0.78 / M_helical |
| The sweep law over-credits Mach relief; sections run above their critical Mach | DERIVED | register: `sweep_relief_audit.json`, `critical_mach_audit.json` | geometric projection check; 2-D panel method |
| BEM η 0.8072 (v03 family), 0.7951 (v06 family); design thrust 14,451.5 N | DESIGN INTENT | `design_summary.json`, `design_summary_v06.json` | Adkins–Liebeck design; 7 internal closure checks (`gate_G0`, `station_independence`) |

## Geometry

| Claim | Class | Evidence | Method |
|---|---|---|---|
| PRIME passes a 12-check geometry gate (before saving and after re-opening) | PRIMARY | `structural/verification/blade_v03_G1_PRIME_verification.json` | independent re-open and measurement |
| PRIME identity | PRIMARY | SHA-256 in `cad/README.md`; register (native file) | hash |
| v02 was built with 0.757 m axial rake and a 1.879 m tip | PRIMARY | same file (`v02_Z_span_m`, `v02_true_radius_max_m`) | coordinate readback |
| Camber on the wrong side of the chord in V03 (and in PRIME's section code) | PRIMARY | register: `camber_orientation_check.json`, `camber_stl_check.json`, `STAGE35_CAMBER_INVERSION_ROOT_CAUSE.md` | mean-line direction measured on the solved blade, the CAD source and the exported CAD surfaces |
| CFD derivative geometry per case | PRIMARY | `cad/cfd_derivatives/*.step` | exported CAD |
| Meshed trailing edge differs from the CAD value (0.0161c–0.0212c for 0.012c CAD) | PRIMARY | `cfd_campaign/*/te_thickness_*.json` | measured from the blade-surface mesh |
| 0.006c trailing edge could not be meshed; 0.008c diverged | PRIMARY | register: `v09_TE006_MESH_FAILURE.json`, `v13_TET_INIT_FAILED_definitive_root_cause.json`, `v09b_TE008_DIVERGED.json` | mesher and solver records |

## CFD

| Claim | Class | Evidence | Method |
|---|---|---|---|
| V08 T = 6548.01 N, Q = 18788.06 N·m, P = 2.5469 MW, η_p = 0.57179 | PRIMARY → DERIVED check | `cfd_campaign/v08_reference_case/performance_result_v08_omega135p559.json` → `reproducibility/verify_results.py` → `figures/cfd/cfd_v08_summary.svg` | force report; P = Q·\|ω\|, η = T·V0/P recomputed exactly |
| Values for every other case in `RESULTS.md` | PRIMARY → DERIVED check | `cfd_campaign/<case>/performance_result_*.json` → `campaign_summary.json` | as above |
| V08 passes the rolling window and fails the full-history window | DERIVED | `verify_results.py` from the stored checkpoints (matches `convergence_character_v08.json`) | peak-to-peak / mean against 1 % |
| No design-RPM case passes full-history convergence; V11 (off-design) passes both | DERIVED | `campaign_summary.json` | as above |
| Residual drop about 3 orders | DERIVED | `cfd_campaign/*/residuals_*.csv` (from the solver logs in the register) | log parse |
| Blade y⁺ node-median about 430–440; > 90 % of nodes above 300 | DERIVED | `cfd_campaign/*/blade_yplus_node_statistics_*.json` (from blade-surface exports in the register) | node statistics |
| Mesh cell counts and quality | PRIMARY | `cfd_campaign/*/openfan_*_vol_orthoquality.json`; `history/no_result_cases/` | mesh quality report |
| V11 runs at 1000 rpm (the stored `rpm` field is stale) | PRIMARY + DERIVED | V11 result file (`omega` = −104.719755); `campaign_summary.json` (`rpm_from_omega`) | rpm = \|ω\|·60 / 2π |
| V03 produced net drag; axial induction ≈ 0 and incidence above design | DIAGNOSTIC | V03 result file; register: `operating_points.json` | force report; ring-averaged velocity triangle |
| V14: zero-shear hub walls deepened the root windmill state | DIAGNOSTIC | `cfd_campaign/v14_hub_bc_diagnostic/blade_loading_v14.json`; register: `HUB_BOUNDARY_LAYER_CONFIRMED.json` (the boundary-layer measurement on V08 that motivated the test) | sectional loading at r/R 0.40 |
| V10: prediction failed; mechanism not tested | PRIMARY | V10 result file; register: `v10_prediction.json`, `v10_PITCH_FALSIFIED.json` (the file name refers to the prediction) | pre-registered band vs recorded η; no V10 sectional export exists |
| V12, V15: predictions failed | PRIMARY | result files; register: `v12_prediction.json`, `v12b_prediction_corrected_basis.json`, `v15_prediction.json`, `v15_gate_report.json` | pre-registered bands and gates |
| V16 built and meshed, not solved | PRIMARY | `cad/cfd_derivatives/openfan_blade_v16_CFD_SINGLELOFT.step`; `history/no_result_cases/openfan_v16_vol_orthoquality.json`; register: `V16_PRESOLVE_SIGN_REVERSAL_AUDIT.json` | no case file and no solution exist |
| First 360° mesh rejected on quality; the sector domain abandoned; the sector domain's volume check was too coarse | HISTORICAL | register: `STAGE29_DOMAIN_LOCK_REPORT.md`, `STAGE30_VOLUME_MESH_BLOCKER.md`, `STAGE31_CFD_DIVERGENCE_DIAGNOSIS.md` | mesh-quality and domain-volume measurement |
| Sectional drag decomposition that motivated V08 | DERIVED (model-based) | register: `STAGE38_DRAG_DECOMPOSITION_AND_V08.md` | base-drag correlation applied to the V06e sectional polar |

## Structural

| Claim | Class | Evidence | Method |
|---|---|---|---|
| 34 components, 99 mates, fully constrained; clearances and rake | PRIMARY | `structural/verification/rotor_assembly_v02_final_verification.json` | CAD re-open and measurement |
| FEA stage outcomes (Stage 15 "not viable as drawn"; Stage 20 moment balance does not close; Stages 18–19 not mesh-converged) | PRIMARY (reports not published) | register: the eight FEA stage reports | ANSYS MAPDL screening analyses |

## Figures

Every figure's source data and generating script are listed in [`figures/README.md`](figures/README.md).
