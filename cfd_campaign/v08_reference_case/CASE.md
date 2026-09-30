# V08 — reference case (highest recorded design-RPM efficiency in this campaign)

| | |
|---|---|
| Classification | DESIGN-RPM CFD OBSERVATION (reference case) |
| Operating point | 1294.5 rpm (ω = -135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | Trailing-edge parameter 0.020c → 0.012c on the V06e aerodynamic design; every other design parameter identical. |
| Mesh | 6,575,649 (min orthogonal quality 0.00285; 325 cells below 0.01); no prism layers |
| Thrust T | 6548.01 N |
| Torque Q | 18788.06 N·m |
| Shaft power P = Q·\|ω\| | 2.5469 MW |
| Propulsive efficiency η = T·V0/P | 0.57179 |
| Rolling window (last 5 checkpoints), T / Q | 0.80 % / 0.47 % — within the 1 % bound |
| Full second-order history (S2–S10), T / Q | 1.93 % / 1.12 % — outside the 1 % bound |
| Residuals (continuity) | 1 → 0.000999 = 3.00 orders over 590 iterations (≥ 4 orders required by the G2 criterion) |
| Trailing edge | CAD parameter 0.012c; meshed (outboard mean, r/R ≥ 0.70) 0.0188c |
| Blade y+ (node-based) | median 436.4, 95th percentile 557.1, max 1907.3; 93 % of nodes above 300 |
| Validation | none — no experimental or benchmark comparison exists |

## Prediction

Pre-registered η band 0.545–0.570 (central 0.558), with the clause that shaft torque must fall. The recorded η was 0.0018 above the band and torque rose 4.45 %, so the base-drag mechanism clause was not met.

## Outcome

Highest recorded design-RPM efficiency in this CFD campaign. The case did not satisfy the strict full-history convergence criterion, and no mesh-independence or physical-validation claim is made.

## Notes

- The meshed trailing edge (0.0188c) did not match the 0.012c CAD parameter; the result tests a thinner aft section, not a 0.012c edge.
- Used as the reference geometry for V10, V12, V14 and V15.

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `blade_loading_v08.json` (recorded)
- `blade_yplus_node_statistics_v08.json` (derived)
- `convergence_character_v08.json` (recorded)
- `energy_ledger_design_rpm_v08.json` (recorded)
- `openfan_v08_vol_orthoquality.json` (recorded)
- `performance_result_v08_omega135p559.json` (recorded)
- `residuals_v08.csv` (derived)
- `sectional_polar_v08.json` (recorded)
- `te_thickness_v08.json` (recorded)
- `velocity_triangle_BUILT_v08.json` (recorded)
