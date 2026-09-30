# Cases without a CFD result

These cases produced no performance values.

| Case | What was attempted | Outcome | Record |
|---|---|---|---|
| V06 | V06 geometry, 9,133,396-cell mesh | rejected: exceeded available memory | `openfan_v06_vol_orthoquality.json` |
| V06c | same geometry, 7,609,169-cell mesh | solve aborted: exceeded wall time | `openfan_v06c_vol_orthoquality.json` |
| V07 | intermediate lift/chord schedule | CAD built; import failed (surface-export defect); never solved | — |
| V08b | 0.016c trailing-edge parameter | CAD built; import failed; not re-attempted | — |
| V09 | 0.006c trailing edge (PRIME's value) | tetrahedral initialisation failed at the 7.24 mm size floor | STEP in `cad/cfd_derivatives/` |
| V09b | 0.008c trailing edge | meshed (6,841,077 cells); the solve diverged near iteration 460–470 | `openfan_v09b_vol_orthoquality.json` |
| V13 | V09 geometry at a 2.5 mm size floor | tetrahedral initialisation failed; a mesh attempt, not a design | — |
| V16 | root re-pitch +2.40° → 0 at r/R 0.55 (mirror of V15) | CAD built and volume mesh generated (6,181,870 cells, −5.99 % vs V08); not solved. The pre-solve check did not clear it to run, because its mesh differs from V08's by more than the comparison allows. | `openfan_v16_vol_orthoquality.json`; STEP in `cad/cfd_derivatives/` |
