# CFD campaign — case folders

One folder per case that produced a recorded result. Each folder has a `CASE.md` (change, prediction, outcome,
limitations), the recorded result file (published unchanged) and supporting records. Summary tables:
[`../RESULTS.md`](../RESULTS.md). Machine-readable summary: `campaign_summary.json`, written by
`reproducibility/verify_results.py`.

| Folder | Case | Operating point | Classification |
|---|---|---|---|
| [`v03_diagnostic_drag_state/`](v03_diagnostic_drag_state/CASE.md) | V03 | design RPM | diagnostic (net drag) |
| [`v04cf_camber_corrected/`](v04cf_camber_corrected/CASE.md) | V04cf | design RPM | diagnostic (unsettled) |
| [`v05n16_naca16_sections/`](v05n16_naca16_sections/CASE.md) | V05n16 | design RPM | observation |
| [`v06e_cl_chord_schedule/`](v06e_cl_chord_schedule/CASE.md) | V06e | design RPM | observation |
| [`v08_reference_case/`](v08_reference_case/CASE.md) | V08 | design RPM | observation — reference case |
| [`v10_uniform_depitch/`](v10_uniform_depitch/CASE.md) | V10 | design RPM | controlled experiment |
| [`v11_1000rpm_offdesign/`](v11_1000rpm_offdesign/CASE.md) | V11 | **1000 rpm, OFF-DESIGN** | separate investigation |
| [`v12_sweep_plus6deg/`](v12_sweep_plus6deg/CASE.md) | V12 | design RPM | controlled experiment |
| [`v14_hub_bc_diagnostic/`](v14_hub_bc_diagnostic/CASE.md) | V14 | design RPM | boundary-condition diagnostic |
| [`v15_root_depitch/`](v15_root_depitch/CASE.md) | V15 | design RPM | controlled experiment |

Cases without a result (V06, V06c, V07, V08b, V09, V09b, V13, V16) are described in `../RESULTS.md` §4 and
`../history/no_result_cases/`.

**Recorded vs derived.**

- **Recorded** files are copied byte-for-byte from the project records.
- **Derived** files were produced from recorded data for this repository:
  - `residuals_*.csv`, extracted from the solver logs;
  - `blade_yplus_node_statistics_*.json`, from the blade-surface exports;
  - `campaign_summary.json`.

  Each derived file states its source. The scripts that produced the residual and y⁺ files are not published.

**Known data-quality items.**

- The stored `rpm` field is stale in some recorded files: V11's reads 1294.49, while ω gives 1000 rpm.
- The raw field `settled_within_1pct` in the result files refers to the **rolling** window only.
- The polars for V04cf, V05n16 and V06e use the zero-induction basis.
