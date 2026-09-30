# V14 — hub-wall boundary-condition diagnostic (not a design)

| | |
|---|---|
| Classification | BOUNDARY-CONDITION DIAGNOSTIC (design RPM) |
| Operating point | 1294.5 rpm (ω = -135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | V08 case with one boundary condition changed: hub walls set to zero shear (slip). Geometry, mesh and operating point identical to V08. No new CAD. |
| Mesh | identical to V08 (same case file); no prism layers |
| Thrust T | 6247.89 N |
| Torque Q | 18406.41 N·m |
| Shaft power P = Q·\|ω\| | 2.4952 MW |
| Propulsive efficiency η = T·V0/P | 0.55690 |
| Rolling window (last 5 checkpoints), T / Q | 0.83 % / 0.46 % — within the 1 % bound |
| Full second-order history (S2–S10), T / Q | 2.22 % / 1.19 % — outside the 1 % bound |
| Residuals (continuity) | 1 → 0.000995 = 3.00 orders over 593 iterations (≥ 4 orders required by the G2 criterion) |
| Blade y+ (node-based) | median 434.8, 95th percentile 557.0, max 1914.8; 92 % of nodes above 300 |
| Validation | none — no experimental or benchmark comparison exists |

## Prediction

η band 0.59–0.64; primary gate: root thrust loading at r/R 0.40 must become less negative. Written after the case was built and before the solve.

## Outcome

BOUNDARY-CONDITION DIAGNOSTIC. The root windmill state deepened (dT/dr at r/R 0.40 from −1369 to −1858 N/m), so the hub boundary layer is not its cause in this model. Its η must not be read as an achievable design result.

## Notes

- No convergence-character file existed for this case; windows are computed by reproducibility/verify_results.py from the stored checkpoints.

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `blade_loading_v14.json` (recorded)
- `blade_yplus_node_statistics_v14.json` (derived)
- `performance_result_v14_omega135p559.json` (recorded)
- `residuals_v14.csv` (derived)
- `sectional_polar_v14.json` (recorded)
- `velocity_triangle_BUILT_v14.json` (recorded)
