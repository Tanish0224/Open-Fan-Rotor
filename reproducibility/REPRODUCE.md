# Reproducibility

What someone with only this repository can and cannot re-derive.

| Stage | Status | What is here | What is missing |
|---|---|---|---|
| **BEM design** | **reproducible now** | `design/openfan_design.py`, `run_phase1_design.py`, `run_v06_design.py` and their outputs | nothing (NumPy only; Matplotlib for the plots written by `run_phase1_design.py`) |
| **Force → P, η, convergence windows** | **reproducible now** | recorded result files with all checkpoints; `reproducibility/verify_results.py` | nothing |
| **Figures from recorded data** | **reproducible now** (plots) / **partially** (field images) | `figures/src/make_figures.py` | the blade-to-blade field exports (hash-identified) for the three field images |
| **Geometry** | **partially reproducible** | CFD-derivative STEP files; section-generation scripts; design tables; PRIME identified by SHA-256 | the native PRIME and structural CAD files; the SolidWorks build needs SolidWorks 2026 |
| **CFD setup** | **partially reproducible** | journal templates (setup, solve, V14 boundary condition); settings table in `cfd_method/` | the mesh and case files (0.12–0.20 GB each, over the repository size limit) |
| **Mesh** | **partially reproducible** | size controls and quality records; the STEP geometry | the meshing journals and surface exports; the mesher's output is not bit-reproducible across versions |
| **CFD solution** | **not reproducible from this repository alone** | — | the case and data files, and ANSYS Fluent 2025 R1 |
| **Post-processing, published scripts** (force extraction, convergence character, trailing-edge measurement, per-case ω, BEM reference) | **partially reproducible** | the scripts in `cfd_method/postprocessing/` and their recorded outputs | Fluent transcript files (`.trn`) and blade-surface exports; the scripts document how the recorded files were made but cannot be re-run without those inputs |
| **Post-processing, scripts not published** (sectional polars, blade-loading integrals, velocity triangles, y⁺ statistics, residual histories, span accounting) | **not reproducible from this repository** | the recorded or derived outputs only (`sectional_polar_*.json`, `blade_loading_*.json`, `velocity_triangle_*.json`, `blade_yplus_node_statistics_*.json`, `residuals_*.csv`) | the generating scripts (some are named in code comments but are not in the repository), the field exports and the solver logs; the older polars were also produced on a zero-induction basis that was later found defective |
| **FEA** | **not reproducible from this repository** | stage conclusions in `structural/README.md`; reports identified by hash | the MAPDL input decks and results; the aerodynamic load dataset behind Stage 1 is not traced |

## Quick checks

```
python reproducibility/verify_results.py        # read-only: recomputes P, eta and both windows for every case
```

Two further commands **write files**, so run them on a copy of the repository, not on the published tree:

```
python figures/src/make_figures.py              # rewrites figures/cfd and figures/design (field images need --field-data)
python design/run_phase1_design.py              # re-runs the BEM design; writes into design/results/ next to the script
```

`run_phase1_design.py` writes into the `results/` folder beside itself. Run from the repository it **overwrites the
recorded design files** and adds a `figures/` folder; run it from a copy of the `design/` folder to leave the
published files untouched (copy `design/` to a scratch location and run the script there). On a copy, it reproduces
the recorded `design_summary.json` exactly. `make_figures.py` rewrites the published figure files; with the library
versions used here it regenerates them byte-for-byte, and other Matplotlib versions may differ in detail.

Software used for the recorded results: Python 3 with NumPy, SciPy and Matplotlib; SolidWorks 2026; ANSYS Fluent
2025 R1; ANSYS MAPDL 2025 R1. The checks above need only Python with NumPy and Matplotlib.

## Files that exist but are not published

`unpublished_evidence_register.json` lists 62 files by name, SHA-256 and size, with the reason each is not
included. They are:

- pre-registered predictions;
- case assessment records;
- solver logs;
- field exports;
- the V08 mesh, case and solution files;
- the PRIME native CAD file;
- the FEA stage reports;
- CFD and design check records.

Their identity can be checked against this register if they are supplied for review.
