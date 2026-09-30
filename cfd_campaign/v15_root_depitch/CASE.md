# V15 — local root de-pitch (controlled experiment)

| | |
|---|---|
| Classification | DESIGN-RPM CONTROLLED EXPERIMENT |
| Operating point | 1294.5 rpm (ω = -135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | Blade angle reduced near the root: −2.40° at the hub tapering to 0 at r/R 0.55; outboard geometry bit-identical to V08. |
| Mesh | 6,551,933 (min orthogonal quality 0.00317; 12 cells below 0.01); no prism layers |
| Thrust T | 6057.41 N |
| Torque Q | 17851.56 N·m |
| Shaft power P = Q·\|ω\| | 2.4199 MW |
| Propulsive efficiency η = T·V0/P | 0.55670 |
| Rolling window (last 5 checkpoints), T / Q | 0.86 % / 0.49 % — within the 1 % bound |
| Full second-order history (S2–S10), T / Q | 2.02 % / 1.14 % — outside the 1 % bound |
| Residuals (continuity) | 1 → 0.000994 = 3.00 orders over 570 iterations (≥ 4 orders required by the G2 criterion) |
| Trailing edge | CAD parameter 0.012c; meshed (outboard mean, r/R ≥ 0.70) 0.0161c |
| Blade y+ (node-based) | median 435.7, 95th percentile 549.9, max 960.0; 94 % of nodes above 300 |
| Validation | none — no experimental or benchmark comparison exists |

## Prediction

η band 0.585–0.635; primary gate: root thrust loading less negative and root torque toward zero. The basis was a cross-case lift slope measured over a 0.104° incidence interval.

## Outcome

PREDICTION FAILED and the primary gate failed (root dT/dr −1369 → −2487 N/m). The change also altered loading outboard of r/R 0.55 (−64 % at r/R 0.60), so it was not local. A single two-point estimate at r/R 0.40 gives a positive lift slope; that argues against a stalled root at that station but is not sufficient to quantify the correction the root needs.

## Notes

- Meshed trailing edge 0.0161c vs V08's 0.0188c from identical CAD — a confound.
- 450 temperature-limiter events on one cell were recorded.

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `blade_loading_v15.json` (recorded)
- `blade_yplus_node_statistics_v15.json` (derived)
- `convergence_character_v15.json` (recorded)
- `openfan_v15_vol_orthoquality.json` (recorded)
- `performance_result_v15_omega135p559.json` (recorded)
- `residuals_v15.csv` (derived)
- `sectional_polar_v15.json` (recorded)
- `te_thickness_v15.json` (recorded)
- `velocity_triangle_BUILT_v15.json` (recorded)
