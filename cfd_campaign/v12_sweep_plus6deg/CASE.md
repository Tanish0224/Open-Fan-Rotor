# V12 — sweep +6° (controlled experiment)

| | |
|---|---|
| Classification | DESIGN-RPM CONTROLLED EXPERIMENT |
| Operating point | 1294.5 rpm (ω = -135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | Sweep angle increased by 6.00° along the span from V08. |
| Mesh | 7,173,817 (min orthogonal quality 0.00069; 193 cells below 0.01); no prism layers |
| Thrust T | 5726.35 N |
| Torque Q | 17587.74 N·m |
| Shaft power P = Q·\|ω\| | 2.3842 MW |
| Propulsive efficiency η = T·V0/P | 0.53417 |
| Rolling window (last 5 checkpoints), T / Q | 0.86 % / 0.46 % — within the 1 % bound |
| Full second-order history (S2–S10), T / Q | 1.95 % / 1.06 % — outside the 1 % bound |
| Residuals (continuity) | 1 → 0.00132 = 2.88 orders over 600 iterations (≥ 4 orders required by the G2 criterion) |
| Trailing edge | CAD parameter 0.012c; meshed (outboard mean, r/R ≥ 0.70) 0.0212c |
| Blade y+ (node-based) | median 430.3, 95th percentile 566.3, max 3084.0; 93 % of nodes above 300 |
| Validation | none — no experimental or benchmark comparison exists |

## Prediction

Two pre-registered bands: A 0.579–0.652 (before CAD); B 0.575–0.647 (corrected basis, before the solve).

## Outcome

PREDICTION FAILED: η 0.534, below both bands. The evidence on the normal-Mach mechanism was mixed (lift-slope rose at 2 of 9 stations and fell at 5). Interpretation is qualified by two confounds.

## Notes

- Mesh +9.1 % cells relative to V08 (size controls identical; the mesher responded to the geometry).
- Meshed trailing edge 0.0212c vs V08's 0.0188c from the same 0.012c trailing-edge parameter (the swept CAD differs). A project report stated 0.0182c; the measurement file published here reads 0.0212c.

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `blade_loading_v12.json` (recorded)
- `blade_yplus_node_statistics_v12.json` (derived)
- `convergence_character_v12.json` (recorded)
- `openfan_v12_vol_orthoquality.json` (recorded)
- `performance_result_v12_omega135p559.json` (recorded)
- `residuals_v12.csv` (derived)
- `sectional_polar_v12.json` (recorded)
- `te_thickness_v12.json` (recorded)
- `velocity_triangle_BUILT_v12.json` (recorded)
