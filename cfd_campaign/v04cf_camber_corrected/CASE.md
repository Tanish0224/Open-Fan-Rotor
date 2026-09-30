# V04cf — camber sign corrected

| | |
|---|---|
| Classification | diagnostic (camber corrected; diverged at iteration 246) |
| Operating point | 1294.5 rpm (ω = 135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | Single change from V03: the sign of the camber line (the section camber was on the wrong side of the chord for the direction of rotation). |
| Mesh | 5,943,535 (min orthogonal quality 0.00325; 9 cells below 0.01); no prism layers |
| Thrust T | 4209.88 N |
| Torque Q | 19052.16 N·m |
| Shaft power P = Q·\|ω\| | 2.5827 MW |
| Propulsive efficiency η = T·V0/P | 0.36252 |
| Convergence windows | not evaluable (4 stored checkpoint(s)) |
| Validation | none (no experimental or benchmark data) |

## Prediction

None registered.

## Outcome

Thrust became positive at design RPM. The case did not settle: it diverged at iteration 246 and only four checkpoints exist. Two values are stored (last checkpoint and window mean); both are kept.

## Notes

- Sectional polar in this folder uses the zero-induction basis (an extraction defect found later; not regenerated for this case).

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `blade_loading_v04cf.json` (recorded)
- `convergence_character_v04cf.json` (recorded)
- `energy_ledger_design_rpm_v04cf.json` (recorded)
- `openfan_v04cf_vol_orthoquality.json` (recorded)
- `performance_result_v04cf_omega135p559.json` (recorded)
- `sectional_polar_v04cf.json` (recorded)
- `velocity_triangle_v04cf.json` (recorded)
