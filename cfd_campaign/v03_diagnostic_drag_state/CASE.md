# V03 — first CFD state: net drag at design RPM

| | |
|---|---|
| Classification | DIAGNOSTIC (drag state, design RPM) |
| Operating point | 1294.5 rpm (ω = 135.559 rad/s), flight Mach 0.75, 10,668 m ISA |
| Change | CFD derivative of PRIME with the trailing edge thickened to 0.020c for meshing. Camber was later found to be on the wrong side of the chord. |
| Mesh | 5,988,657 (value from the mesh record; the mesh-quality file is not published); no prism layers |
| Thrust T | -845.78 N |
| Torque Q | 5367.10 N·m |
| Shaft power P = Q·\|ω\| | 0.7276 MW |
| Propulsive efficiency η = T·V0/P | undefined (net drag) |
| Convergence windows | not evaluable (1 stored checkpoint(s)) |
| Validation | none — no experimental or benchmark comparison exists |

## Prediction

None registered.

## Outcome

DIAGNOSTIC. The rotor produced net drag (T < 0) while absorbing shaft power. Propulsive efficiency is undefined for this state and is not reported.

## Notes

- Only one checkpoint is stored, so neither convergence window can be evaluated from the published file.
- This state led to the camber-orientation check that found the construction error (see V04cf).

## Files in this folder

Recorded files are published unchanged; derived files are marked.

- `performance_result_omega135p559.json` (recorded)
