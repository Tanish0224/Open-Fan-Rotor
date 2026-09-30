# V05n16 — NACA 16-series sections

| | |
|---|---|
| Classification | design iteration, design RPM |
| Operating point | 1294.5 rpm (ω = 135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | Section family changed to NACA 16-series thickness on an a = 1.0 mean line; chord, t/c, design C_l, sweep and trailing edge held. |
| Mesh | 6,700,165 (min orthogonal quality 0.00180; 572 cells below 0.01); no prism layers |
| Thrust T | 4997.55 N |
| Torque Q | 16379.44 N·m |
| Shaft power P = Q·\|ω\| | 2.2204 MW |
| Propulsive efficiency η = T·V0/P | 0.50057 |
| Rolling window (last 5 checkpoints), T / Q | 0.64 % / 0.32 % — within the 1 % bound |
| Full second-order history (S2–S10), T / Q | 1.42 % / 0.73 % — outside the 1 % bound |
| Validation | none (no experimental or benchmark data) |

## Prediction

η band 0.434–0.517 (central 0.4755), written before the solve (file `v05_prediction.json`, see the unpublished-evidence register).

## Outcome

η fell inside the predicted band. The case fails the full-history convergence window.

## Notes

- Sectional polar uses the zero-induction basis (not regenerated).
- Residual history for this case is not extracted (its solver log is not in the extracted set).

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `blade_loading_v05n16.json` (recorded)
- `convergence_character_v05n16.json` (recorded)
- `energy_ledger_design_rpm_v05n16.json` (recorded)
- `openfan_v05n16_vol_orthoquality.json` (recorded)
- `performance_result_v05n16_omega135p559.json` (recorded)
- `sectional_polar_v05n16.json` (recorded)
- `velocity_triangle_v05n16.json` (recorded)
