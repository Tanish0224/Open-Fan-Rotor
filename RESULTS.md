# Results

All cases were solved in ANSYS Fluent 2025 R1: steady MRF, k-ω SST, a 360° domain with all 16 blades, one mesh per
case and no prism layers. The values below are read from the result and mesh-quality files in `cfd_campaign/`.
`python reproducibility/verify_results.py` recomputes shaft power, efficiency, rpm and both convergence windows
from those files. Thrust, torque and cell counts are the recorded solver values.

Shaft power is P = Q·|ω| and propulsive efficiency is η_p = T·V0/P, with V0 = 222.40 m/s.

**Convergence windows.** Each window is the peak-to-peak spread of thrust (T) and torque (Q) as a percentage of
their mean, checked against 1 %:

- **rolling:** the last 5 checkpoints (about 300 iterations);
- **full history:** all second-order checkpoints S2–S10 (about 540 iterations). This is the stricter of the two
  and the closer one to the original convergence target.

None of the design-RPM cases meets the full-history criterion. Mesh independence was not assessed, and there is
no experimental data to compare against. See [`LIMITATIONS.md`](LIMITATIONS.md).

---

## 1. Design RPM (1294.5 rpm, |ω| = 135.559 rad/s, Mach 0.75, 10,668 m ISA)

| Case | Role | Geometry change | Thrust [N] | Torque [N·m] | Shaft power [MW] | η_p | Rolling T/Q % | Full-history T/Q % | Mesh (cells) | Notes |
|---|---|---|---:|---:|---:|---:|---|---|---:|---|
| **V05n16** | design iteration | NACA 16-series sections | 4997.55 | 16379.44 | 2.2204 | 0.50057 | 0.64 / 0.32 ✓ | 1.42 / 0.73 ✗ | 6,700,165 | inside its predicted band |
| **V06e** | design iteration | lower design C_l, thinner root (v06 design) | 5809.08 | 17987.46 | 2.4384 | 0.52984 | 0.87 / 0.45 ✓ | 2.06 / 1.09 ✗ | 6,480,343 | — |
| **V08** | **reference case** | trailing-edge parameter 0.020c → 0.012c (meshed 0.0188c) | **6548.01** | **18788.06** | **2.5469** | **0.57179** | 0.80 / 0.47 ✓ | 1.93 / 1.12 ✗ | 6,575,649 | highest design-RPM efficiency in the campaign |
| **V10** | experiment on V08 | uniform de-pitch −1.77° | 3224.33 | 12062.04 | 1.6351 | 0.43856 | 1.63 / 0.70 ✗ | 5.45 / 2.36 ✗ | 6,603,468 | prediction failed; mechanism not tested |
| **V12** | experiment on V08 | sweep +6° | 5726.35 | 17587.74 | 2.3842 | 0.53417 | 0.86 / 0.46 ✓ | 1.95 / 1.06 ✗ | 7,173,817 | prediction failed; mesh +9.1 % and a different meshed trailing edge |
| **V15** | experiment on V08 | root de-pitch −2.40° → 0 at r/R 0.55 | 6057.41 | 17851.56 | 2.4199 | 0.55670 | 0.86 / 0.49 ✓ | 2.02 / 1.14 ✗ | 6,551,933 | prediction and root-loading target both missed |

**V08.** V08 is the reference geometry for V10, V12, V14 and V15. It passes the rolling window, but its
full-history spread of 1.93 % / 1.12 % is above the 1 % criterion. V08, V14 and V15 differ by about 0.015 in η,
which is the same order as V08's own full-history spread. The V08 prediction was only partly met: η came
out 0.0018 above the predicted band, but the prediction also expected a fall in torque, and torque rose 4.45 %
relative to V06e.

For every row, shaft power and efficiency reproduce from the recorded thrust, torque and ω to machine precision.

## 2. Off-design: 1000 rpm

Speed and twist changed together (the blade was re-twisted for 1000 rpm), so V11 is not comparable with the
design-RPM table.

| Case | Operating point | Thrust [N] | Torque [N·m] | Shaft power [MW] | η_p | Rolling T/Q % | Full-history T/Q % | Mesh (cells) | Notes |
|---|---|---:|---:|---:|---:|---|---|---:|---|
| **V11** | 1000.0 rpm (\|ω\| = 104.72 rad/s) | 5848.05 | 18939.19 | 1.9833 | 0.65578 | 0.12 / 0.07 ✓ | 0.76 / 0.37 ✓ | 6,545,217 | inside its predicted band; the only case that passes both windows |

## 3. Diagnostic cases (design RPM)

| Case | Role | What it is | Thrust [N] | Torque [N·m] | η_p | Convergence | Notes |
|---|---|---|---:|---:|---|---|---|
| **V03** | diagnostic | first CFD run: PRIME-based blade with the camber on the wrong side of the chord | −845.78 | 5367.10 | undefined (net drag) | 1 stored checkpoint | led to the camber check |
| **V04cf** | diagnostic | V03 with the camber sign corrected | 4209.88 (last checkpoint) | 19052.16 | 0.36252 (last checkpoint) | diverged at iteration 246 | thrust became positive; not settled |
| **V14** | boundary-condition test | V08 case with zero-shear hub walls; same geometry and mesh | 6247.89 | 18406.41 | 0.55690 | rolling 0.83 / 0.46 ✓; full 2.22 / 1.19 ✗ | root windmilling got deeper, so the hub boundary layer is not its cause in this model; not a design |

## 4. Cases without a result

| Case | Type | What happened |
|---|---|---|
| V06, V06c | mesh attempts | two meshes of the V06e geometry: 9.13 M cells exceeded memory; 7.61 M cells exceeded wall time |
| V07 | no result | CAD built; import failed (surface-export defect); never solved |
| V08b | no result | CAD built (0.016c trailing edge); import failed; not re-attempted |
| V09 | mesh attempt | PRIME's 0.006c trailing edge; tetrahedral initialisation failed at the 7.24 mm size floor |
| V09b | failed solve | 0.008c trailing edge meshed; the solve diverged near iteration 460–470 |
| V13 | mesh attempt | V09 geometry at a 2.5 mm size floor; tetrahedral initialisation failed; no CFD result |
| V16 | not solved | mirror of V15 (+2.40° root re-pitch); CAD built and volume mesh generated (6,181,870 cells, −5.99 % vs V08); not solved |
| +7 % RPM point | no result | thrust oscillated 36 % peak-to-peak and never settled; not used |

## Notes on the recorded data

- **Stale `rpm` field.** The stored `rpm` field reads 1294.49 in every result file, including V11
  (ω = −104.72 rad/s, i.e. 1000 rpm). The operating point is taken from ω and the case definition.
  `campaign_summary.json` lists both.
- **ω sign.** V03–V06e record |ω|; V08 onward record the signed value. From V04cf onward, the journals all set
  ω = −135.559 rad/s about +z, so the rotor's rotation is the same throughout. Shaft power uses |ω|.
- **Iteration counts.** Fluent's default residual stop ended six runs before 600 iterations: V06e at 592, V08 at
  590, V10 at 571, V11 at 547, V14 at 593 and V15 at 570. V12 ran all 600. V05n16's solver log is not in the
  extracted set. This stop is separate from the convergence windows above.
- **Span.** The CFD blade covers r = 0.565–1.725 m against a design span of 0.490–1.750 m, so T and Q are each
  about 3 % low. η_p is affected only at second order.
- **Sectional polars.** The polars for V04cf, V05n16 and V06e were computed on a zero-induction basis that was
  later found to be wrong. Those files were not regenerated. The later cases use the corrected basis.
