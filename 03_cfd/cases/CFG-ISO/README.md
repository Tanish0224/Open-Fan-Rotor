# CFG-ISO — isolated open-fan rotor, 22.5° periodic sector

**Generated** from `01_design/results/design_summary.json`. Do not hand-edit
`setup_iso_sector.jou` — regenerate it with `python 03_cfd/make_fluent_case.py`.

## Status

| Item | State |
|---|---|
| Setup specification | ✅ `../../CFD_SETUP_SPECIFICATION.md` |
| Solver journal | ✅ `setup_iso_sector.jou` (generated, parameters traced to the design) |
| **Fluid-domain geometry** | ❌ **not yet built** |
| **Mesh** | ❌ **not yet generated** |
| **Solution** | ❌ **NOT RUN — no CFD result exists for this project** |

## What must exist before this journal can run

1. A **fluid domain**: a 22.5° sector of the flow volume
   (8 D upstream, 8 D radial, 15 D downstream) with the blade and spinner
   subtracted. This is a **derivative** of the CAD master, never the master itself.
2. A mesh with these named zones, which the journal expects:
   `fluid`, `farfield`, `outlet`, `blade`, `spinner`, and the two periodic sides.
3. Prism layers sized to `y+ ≈ 1`: first cell **3.2 µm**, growth 1.2, ~32 layers.

## Run

```
"D:\ANSYS Inc\v251\fluent\ntbin\win64\fluent.exe" 3ddp -t8 -g -i setup_iso_sector.jou
```

`-t8` uses 8 cores. **Confirm the licence permits 8 parallel processes** — if it
caps at 4, every runtime estimate in the feasibility audit roughly doubles.

## Design intent this case is testing

| Quantity | BEM design intent |
|---|---|
| `C_T` | 0.5450 |
| `C_P` | 1.9886 |
| `η_p` | 0.8072 — *estimate, bounded by a low-order drag model* |
| Ideal ceiling | 0.9629 — CFD thrust must not exceed this |

A CFD-vs-BEM disagreement **at the tip is expected**: the BEM design uses
sectional aerodynamics outside Prandtl–Glauert validity across the whole blade
(helical tip Mach 1.097). Gate G4 therefore sends the
investigation to the BEM first, not to the mesh.
