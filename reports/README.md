# Reports

The technical write-up is organised so that each number appears in one authoritative place:

| Topic | Where |
|---|---|
| Overview and engineering narrative | [`../README.md`](../README.md) |
| Design method, design point, BEM families | [`../design/README.md`](../design/README.md) |
| Geometry, PRIME, CFD derivatives, trailing-edge values | [`../cad/README.md`](../cad/README.md) |
| CFD setup, convergence definitions, CFD-observation policy | [`../cfd_method/README.md`](../cfd_method/README.md) |
| Every recorded CFD result | [`../RESULTS.md`](../RESULTS.md) and `../cfd_campaign/<case>/CASE.md` |
| Structural CAD lock and FEA screening | [`../structural/README.md`](../structural/README.md) |
| What is not demonstrated | [`../LIMITATIONS.md`](../LIMITATIONS.md) |
| Where each claim comes from | [`../EVIDENCE_INDEX.md`](../EVIDENCE_INDEX.md) |

## Engineering lessons

1. **Check the built geometry against the design intent, not only against the build script.** Both geometry
   errors in this project passed their own CAD gates: sweep built as rake (v02), and camber on the wrong side of
   the chord (v03). Each was found only by measuring the built geometry against what the design meant.
2. **A mesh can pass volume and connectivity checks and still be unusable.** The first 360° mesh diverged because
   of degenerate surface cells. Mesh quality has to be measured before any force is trusted.
3. **A convergence verdict depends on the window.** Every design-RPM case with a full checkpoint history
   fails the full second-order history, and all of them except V10 pass a five-checkpoint window. Both results are
   reported.
4. **Write the prediction before the run.** The three controlled experiments on V08 (one design feature each) each missed their
   written prediction, which is what made them informative. V10 also shows the cost of not exporting the data
   needed to test the mechanism: its prediction failed, but its mechanism remains untested.
5. **CAD value ≠ meshed value.** The trailing edge the mesh resolved differed from the CAD parameter by up to
   0.009c across cases that share the same 0.012c trailing-edge parameter, and PRIME's own trailing edge could not
   be meshed at all.
