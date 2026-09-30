# V11 — 1000 rpm off-design case

| | |
|---|---|
| Classification | off-design case (1000 rpm) |
| Operating point | 1000.0 rpm (ω = -104.72 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | Rotational speed 1294.5 → 1000 rpm AND the blade re-twisted for the new speed (+4.07° root to +7.35° tip). Two coupled changes; their effects cannot be separated. |
| Mesh | 6,545,217 (min orthogonal quality 0.00070; 375 cells below 0.01); no prism layers |
| Thrust T | 5848.05 N |
| Torque Q | 18939.19 N·m |
| Shaft power P = Q·\|ω\| | 1.9833 MW |
| Propulsive efficiency η = T·V0/P | 0.65578 |
| Rolling window (last 5 checkpoints), T / Q | 0.12 % / 0.07 % — within the 1 % bound |
| Full second-order history (S2–S10), T / Q | 0.76 % / 0.37 % — within the 1 % bound |
| Residuals (continuity) | 1 → 0.000998 = 3.00 orders over 547 iterations (≥ 4 orders required by the G2 criterion) |
| Trailing edge | CAD parameter 0.012c; meshed (outboard mean, r/R ≥ 0.70) 0.0182c |
| Blade y+ (node-based) | median 420.7, 95th percentile 533.5, max 1673.0; 92 % of nodes above 300 |
| Validation | none (no experimental or benchmark data) |

## Prediction

η band 0.58–0.67 (central 0.62), written before the run; main check: effective lift-curve slope should rise.

## Outcome

η fell inside its band, and both convergence windows pass. At 1000 rpm, with a re-twisted blade, the case is not comparable with V08.

## Notes

- The stored `rpm` field in the result file reads 1294.49 (stale); ω = −104.72 rad/s ⇒ 1000.0 rpm.
- The solver log shows Fluent's own residual stop at iteration 547 ('solution is converged' on its default residual criterion). An earlier project report stated that V11 ran the full 600-iteration schedule; the log is the primary record. Fluent's default stop is not the convergence criterion used in this repository.
- Mesh tail quality is worse than V08 (minimum orthogonal quality about 4× lower).

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `blade_loading_v11.json` (recorded)
- `blade_yplus_node_statistics_v11_1000rpm_offdesign.json` (derived)
- `convergence_character_v11.json` (recorded)
- `openfan_v11_vol_orthoquality.json` (recorded)
- `performance_result_v11_omega104p720.json` (recorded)
- `residuals_v11_1000rpm_offdesign.csv` (derived)
- `sectional_polar_v11.json` (recorded)
- `te_thickness_v11.json` (recorded)
- `velocity_triangle_BUILT_v11.json` (recorded)
