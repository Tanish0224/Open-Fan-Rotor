# CAD and geometry

## PRIME — the design master

PRIME is the v03 blade, `openfan_blade_v03_G1_PRIME_VERIFIED.SLDPRT`. It is built by `scripts/blade_geometry_v03.py`
from the design table in `design/results/`, and I use it as the fixed design master ("v03" here is the CAD version, not the V03 CFD case; see the naming note
in the top-level README).

| | |
|---|---|
| SHA-256 | `f5d54c78d1596cdd4fd3df130d34287fe25768e99919c7a82be7b751ab17aeca` |
| Gate | 12 of 12 geometry checks passed, before saving and after re-opening (`structural/verification/blade_v03_G1_PRIME_verification.json`) |
| What "VERIFIED" in the file name means | the CAD geometry passed its geometry gate: body count, validity check, volume, true radius, axial rake, sweep realisation, save/re-open. It does **not** mean aerodynamic or structural validation. |
| Known issue | the section camber is on the wrong side of the chord for the direction of rotation. This was found in the CFD derivatives (§7 of the README); PRIME shares the section-placement code. PRIME is kept unchanged as the record of the design as built. |

The native SolidWorks file is not distributed; its identity is fixed by the hash above.

## CFD derivatives (`cfd_derivatives/`)

Each CFD case used a separate CFD geometry built by script from the same generator, never PRIME itself. V03 to
V05n16 keep PRIME's v03-family design table (V05n16 changes the section family); V06e onward use the v06-family
design table. The STEP files are the exported CFD geometries.

| File | Case(s) | Change from its parent |
|---|---|---|
| `openfan_blade_v03_CFD_SINGLELOFT.step` | V03 | PRIME with the trailing edge thickened to 0.020c (camber-side error retained) |
| `openfan_blade_v04_CFD_CAMBERFIX_SINGLELOFT.step` | V04cf | camber sign corrected |
| `openfan_blade_v05_CFD_NACA16_SINGLELOFT.step` | V05n16 | NACA 16-series sections |
| `openfan_blade_v06_CFD_SINGLELOFT.step` | V06, V06c, V06e | v06-family BEM design (lower C_l, thinner root) |
| `openfan_blade_v08_CFD_SINGLELOFT.step` | V08, V14 | trailing-edge parameter 0.012c |
| `openfan_blade_v09_CFD_SINGLELOFT.step` | V09, V13 | trailing-edge parameter 0.006c (PRIME's value); could not be meshed |
| `openfan_blade_v10_CFD_SINGLELOFT.step` | V10 | uniform de-pitch −1.77° |
| `openfan_blade_v11_CFD_SINGLELOFT.step` | V11 (1000 rpm, off-design) | re-twisted for 1000 rpm |
| `openfan_blade_v12_CFD_SINGLELOFT.step` | V12 | sweep +6° |
| `openfan_blade_v15_CFD_SINGLELOFT.step` | V15 | root de-pitch −2.40° → 0 at r/R 0.55 |
| `openfan_blade_v16_CFD_SINGLELOFT.step` | V16 (not solved) | root re-pitch +2.40° → 0 at r/R 0.55 |

## Trailing-edge thickness: CAD value vs meshed value

The trailing-edge thickness set in CAD is **not** the thickness the mesh resolved. The meshed values were
measured from the blade-surface mesh (outboard mean, r/R ≥ 0.70); the measurement files are in each
`cfd_campaign/<case>/te_thickness_*.json`.

| CAD parameter | Cases | Meshed thickness | Mesh | Solution |
|---|---|---|---|---|
| 0.020c | V03, V04cf, V05n16, V06e | 0.0200c (measured for V06e only) | generated | results |
| 0.016c | V08b | — | import failed | none |
| 0.012c | V08, V10, V11, V12, V14, V15, V16 | V08 0.0188c · V11 0.0182c · V12 0.0212c · V15 0.0161c · not measured for V10 (its own mesh, 6,603,468 cells against V08's 6,575,649), V14 (the V08 mesh itself) and V16 (meshed, not solved) | generated | results (V16 not solved) |
| 0.008c | V09b | not measured | generated | solve diverged |
| 0.006c (PRIME) | V09, V13 | — | failed at 7.24 mm and at 2.5 mm size floors | none |

A result labelled with a CAD trailing-edge value should always be read together with its meshed value.

## Scripts (`scripts/`)

`blade_geometry.py` and `blade_geometry_v03.py` generate the section coordinates that the CAD build consumes. The
SolidWorks build and verification scripts for the structural assembly are in `structural/scripts/`. They need
SolidWorks 2026 and are included to document the method; they are not runnable without it.

## Superseded geometry

The v02 blade (sweep built as axial rake; tip at 1.879 m against a 1.75 m design radius) is kept in
`history/superseded_geometry/` for the record.
