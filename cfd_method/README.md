# CFD method

This setup applies to every case in `cfd_campaign/` unless a case page says otherwise. The executable settings are
in the journal templates in `journals/`. They are the V08 setup and solve journals with absolute file paths
removed. The journals for V05n16, V06e, V09b, V10, V12 and V15 are identical to V08's apart from the case tag and
the solver-assigned zone ID. V11 differs only in ω. V14 re-reads the V08 case and changes only the hub-wall
condition (`setup_v14_hub_bc_template.jou`).

## Setup

| Item | Setting |
|---|---|
| Solver | ANSYS Fluent 2025 R1, 3-D, steady (pressure-velocity coupling scheme not set in the journals; solver default) |
| Domain | 360° annulus containing all 16 blades; far field to r = 7 m, z = −7 … +10.5 m |
| Frame | multiple reference frame: rotating cylindrical zone r ≤ 2.0 m, z = −1 … +1 m; outer zone stationary |
| Rotation | ω = −135.559045147 rad/s about +z in the case journals (V04cf onward), i.e. 1294.49 rpm about −z; V11: −104.719755 rad/s (1000 rpm) |
| Turbulence | k-ω SST |
| Fluid | air, ideal gas, three-coefficient Sutherland viscosity, energy equation on |
| Inlet / far field | pressure far-field, p = 23,842.27 Pa, T = 218.808 K, Mach 0.75 along +z |
| Outlet | pressure outlet, 23,842.27 Pa |
| Walls | blade and hub no-slip (V14: hub zero-shear) |
| Discretisation | 60 first-order iterations, then second order |
| Schedule | 60 first-order + 9 × 60 second-order iterations requested; force and moment reported at every 60-iteration checkpoint (S1–S10). Fluent's default residual stop ended some runs a few iterations early. |
| Mesh | Fluent Meshing watertight workflow, tetrahedral, size 7.24 mm – 0.5 m, growth 1.2, curvature and proximity sizing; **no prism layers**; about 6–7 M cells |

## Mesh-quality gate

The first 4.0 M-cell mesh diverged in three solves. The cause was traced to degenerate surface triangles carried
over from the CAD tessellation, and I rejected that mesh on measured quality (minimum orthogonal quality of zero).
From then on every mesh was checked before it was solved. The per-case quality records are in
`cfd_campaign/<case>/openfan_*_vol_orthoquality.json`.

## Force extraction and derived quantities

- Thrust T = −F_z and torque Q = M_z are taken from Fluent's force and moment reports on the blade walls. Hub
  walls are excluded.
- Shaft power is P = Q·|ω|; propulsive efficiency is η_p = T·V0/P with V0 = 222.40 m/s.
- η_p is reported only when T > 0 and P > 0. In a windmill or drag state a negative-over-negative ratio can look
  like a plausible efficiency, so none is reported.
- Two independent extractors (`postprocessing/compute_performance.py`, `postprocessing/independent_extract.py`)
  give identical values for the cases where both were run.

## Convergence and what the numbers may be called

| Term | Definition used here |
|---|---|
| Rolling window | peak-to-peak / mean of T and Q over the last 5 checkpoints; bound 1 % |
| Full-history window | peak-to-peak / mean of T and Q over S2–S10 (all second-order checkpoints); bound 1 % |
| Gate G2 (from the verification plan written before any CFD) | at least three refined meshes with < 2 % change between the two finest; residuals down at least 4 orders; T and Q stationary over the final 500+ iterations; y⁺ within the range the wall treatment requires |
| **CFD observation** | a numerical result recorded from a completed simulation |
| **Validated performance** | a result supported by the required convergence, verification and applicable physical evidence |

G2 was not achieved for any design-RPM case. Design-RPM results are therefore presented as **CFD observations**,
each with its convergence status beside it, and never as validated performance.

The plan written before any CFD said that no performance number should be reported if G2 failed. The numbers
are published here as recorded observations with that failure stated next to each one, not as performance
claims.

## Post-processing scripts (`postprocessing/`)

| Script | Purpose | Input (not all published) |
|---|---|---|
| `compute_performance.py` (+ `bem_reference.py`, `case_omega.py`) | T, Q, P, η from the Fluent transcript file (`.trn`); per-family BEM reference; per-case ω | Fluent transcript file (`.trn`) |
| `independent_extract.py` | a second, separately written parser of the force reports | Fluent transcript file (`.trn`) |
| `convergence_character.py` | window statistics and trend test | Fluent transcript file (`.trn`) |
| `measure_te_thickness.py` | meshed trailing-edge thickness from the blade-surface export | blade-surface CSV |

These scripts document how the recorded files were produced. The Fluent transcript files and field exports they read are not in
this repository (see `reproducibility/REPRODUCE.md`). What can instead be re-derived from the
recorded JSON files with `reproducibility/verify_results.py` is shaft power, efficiency, rpm and both convergence
windows; thrust, torque, mesh counts and the other recorded values are its inputs and are not recomputed.

**Not published.** The scripts that produced the sectional polars, blade-loading integrals, velocity-triangle files,
y⁺ statistics, residual histories and span accounting are not in this repository. Code comments refer to some of them
(for example `sectional_polar_from_cfd.py` and `analyse_blade_loading.py`). Their outputs in `cfd_campaign/` are
published unchanged and cannot be regenerated from here.
