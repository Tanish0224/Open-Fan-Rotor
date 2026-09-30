# V06e — lower design C_l / thinner root (v06-family BEM redesign)

| | |
|---|---|
| Classification | design iteration, design RPM |
| Operating point | 1294.5 rpm (ω = 135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | BEM redesign: C_l root 0.70 → 0.45, tip 0.40 → 0.26, root t/c 0.20 → 0.12 (more chord). Same thrust design point. Two earlier meshes of this geometry were rejected (memory, wall time); V06e is the third mesh. |
| Mesh | 6,480,343 (min orthogonal quality 0.00191; 586 cells below 0.01); no prism layers |
| Thrust T | 5809.08 N |
| Torque Q | 17987.46 N·m |
| Shaft power P = Q·\|ω\| | 2.4384 MW |
| Propulsive efficiency η = T·V0/P | 0.52984 |
| Rolling window (last 5 checkpoints), T / Q | 0.87 % / 0.45 % — within the 1 % bound |
| Full second-order history (S2–S10), T / Q | 2.06 % / 1.09 % — outside the 1 % bound |
| Residuals (continuity) | 1 → 0.000999 = 3.00 orders over 592 iterations (≥ 4 orders required by the G2 criterion) |
| Trailing edge | CAD parameter 0.020c; meshed (outboard mean, r/R ≥ 0.70) 0.0200c |
| Validation | none (no experimental or benchmark data) |

## Prediction

No prediction file was registered for this change.

## Outcome

The case fails the full-history convergence window.

## Notes

- Sectional polar uses the zero-induction basis (not regenerated).
- Comparisons use the v06-family BEM design (η_BEM 0.7951), not the v03-family value.

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `blade_loading_v06e.json` (recorded)
- `convergence_character_v06e.json` (recorded)
- `energy_ledger_design_rpm_v06e.json` (recorded)
- `openfan_v06e_vol_orthoquality.json` (recorded)
- `performance_result_v06e_omega135p559.json` (recorded)
- `residuals_v06e.csv` (derived)
- `sectional_polar_v06e.json` (recorded)
- `te_thickness_v06e.json` (recorded)
- `velocity_triangle_v06e.json` (recorded)
