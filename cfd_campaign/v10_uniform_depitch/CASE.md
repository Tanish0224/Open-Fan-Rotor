# V10 — uniform de-pitch −1.77°

| | |
|---|---|
| Classification | experiment on V08, design RPM |
| Operating point | 1294.5 rpm (ω = -135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | Blade angle reduced uniformly by 1.77° from V08; everything else held. |
| Mesh | 6,603,468 (min orthogonal quality 0.00261; 232 cells below 0.01); no prism layers |
| Thrust T | 3224.33 N |
| Torque Q | 12062.04 N·m |
| Shaft power P = Q·\|ω\| | 1.6351 MW |
| Propulsive efficiency η = T·V0/P | 0.43856 |
| Rolling window (last 5 checkpoints), T / Q | 1.63 % / 0.70 % — outside the 1 % bound |
| Full second-order history (S2–S10), T / Q | 5.45 % / 2.36 % — outside the 1 % bound |
| Residuals (continuity) | 1 → 0.000999 = 3.00 orders over 571 iterations (≥ 4 orders required by the G2 criterion) |
| Validation | none (no experimental or benchmark data) |

## Prediction

η band 0.56–0.62 (central 0.59), written before the run. Mechanism check: sectional drag should fall.

## Outcome

Prediction failed: η 0.439, with thrust −50.8 % relative to V08. The mechanism check was not done: sectional loading data were not exported for this case, so the proposed mechanism was neither confirmed nor ruled out.

## Notes

- Both convergence windows fail; 484 temperature-limiter events were recorded (V06e and V08: none).

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `openfan_v10_vol_orthoquality.json` (recorded)
- `performance_result_v10_omega135p559.json` (recorded)
- `residuals_v10.csv` (derived)
