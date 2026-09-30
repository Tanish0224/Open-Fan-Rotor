# Results — recorded CFD campaign

Every table value in this file (thrust, torque, shaft power, efficiency, convergence windows, cell counts) is read
from the recorded result and mesh-quality files in `cfd_campaign/`. `python reproducibility/verify_results.py`
recomputes shaft power, efficiency, rpm and both convergence windows from them; thrust, torque and cell counts are
recorded values and are not recomputed. All cases were solved in ANSYS Fluent 2025 R1 (steady MRF, k-ω SST,
360° domain with all 16 blades, one mesh per case, no prism layers).

**How to read these numbers.** They are **CFD observations**: numerical results recorded from completed
simulations. They are **not validated performance**. The project's verification plan requires, before any
number can be treated as performance: at least three systematically refined meshes, a residual drop of at
least four orders, thrust and torque stationary over the final 500+ iterations, and y⁺ within the range the
wall treatment needs. No design-RPM case meets those requirements, and no experimental or benchmark
comparison exists for this operating regime. The CFD campaign is therefore documented as an investigative
numerical campaign.

**Convergence windows.** Both are the peak-to-peak spread of thrust (T) and torque (Q) as a percentage of their
mean, against a 1 % bound:

- **rolling window:** the last 5 checkpoints (about 300 iterations);
- **full history:** all second-order checkpoints S2–S10 (about 540 iterations).

The full-history window is the one closer to the verification plan's requirement.

**Operating point.** The operating point is taken from the angular velocity ω and the case definition. Some
recorded files carry a stale `rpm` field (see *Data-quality notes*).

---

## 1. Design-RPM CFD (1294.5 rpm, |ω| = 135.559 rad/s, flight Mach 0.75, 10,668 m ISA)

| Case | Classification | Geometry change | Thrust [N] | Torque [N·m] | Shaft power [MW] | η_p | Rolling T/Q % | Full-history T/Q % | Mesh (cells) | Interpretation |
|---|---|---|---:|---:|---:|---:|---|---|---:|---|
| **V05n16** | observation | NACA 16-series sections | 4997.55 | 16379.44 | 2.2204 | 0.50057 | 0.64 / 0.32 ✓ | 1.42 / 0.73 ✗ | 6,700,165 | inside its pre-registered band |
| **V06e** | observation | lower design C_l, thinner root (v06 design) | 5809.08 | 17987.46 | 2.4384 | 0.52984 | 0.87 / 0.45 ✓ | 2.06 / 1.09 ✗ | 6,480,343 | — |
| **V08** | observation — **reference case** | trailing-edge parameter 0.020c → 0.012c (meshed 0.0188c) | **6548.01** | **18788.06** | **2.5469** | **0.57179** | 0.80 / 0.47 ✓ | 1.93 / 1.12 ✗ | 6,575,649 | **highest recorded design-RPM efficiency in this CFD campaign** — see note below |
| **V10** | controlled experiment | uniform de-pitch −1.77° | 3224.33 | 12062.04 | 1.6351 | 0.43856 | 1.63 / 0.70 ✗ | 5.45 / 2.36 ✗ | 6,603,468 | prediction failed; mechanism test **not performed** |
| **V12** | controlled experiment | sweep +6° | 5726.35 | 17587.74 | 2.3842 | 0.53417 | 0.86 / 0.46 ✓ | 1.95 / 1.06 ✗ | 7,173,817 | prediction failed; mesh (+9.1 %) and trailing-edge confounds |
| **V15** | controlled experiment | root de-pitch −2.40° → 0 at r/R 0.55 | 6057.41 | 17851.56 | 2.4199 | 0.55670 | 0.86 / 0.49 ✓ | 2.02 / 1.14 ✗ | 6,551,933 | prediction and primary gate failed |

> **V08.** T = 6548.01 N, Q = 18788.06 N·m, P = 2.5469 MW, η_p = 0.57179 — the highest recorded
> design-RPM efficiency in this CFD campaign. **The case did not satisfy the strict full-history
> convergence criterion, and no mesh-independence or physical-validation claim is made.** It is not a
> best, optimised or validated design; it is the reference geometry against which V10, V12, V14 and V15
> were run. The differences between V08, V14 and V15 (about 0.015 in η) are of the same order as V08's own
> full-history spread.
>
> V08's pre-registered prediction was only partly met: η was 0.0018 above the predicted band, but torque was
> expected to fall and rose 4.45 % relative to V06e.

Shaft power is P = Q·|ω| and efficiency is η_p = T·V0/P, with V0 = 222.40 m/s. For every row, shaft power and
efficiency reproduce from the recorded thrust, torque and ω to machine precision.

## 2. Off-design CFD — **1000 rpm, OFF-DESIGN (separate investigation)**

Not comparable with the design-RPM table. The blade was re-twisted for the new speed, so two things changed at
once.

| Case | Operating point | Thrust [N] | Torque [N·m] | Shaft power [MW] | η_p | Rolling T/Q % | Full-history T/Q % | Mesh (cells) | Interpretation |
|---|---|---:|---:|---:|---:|---|---|---:|---|
| **V11 — 1000 rpm OFF-DESIGN** | 1000.0 rpm (\|ω\| = 104.72 rad/s) | 5848.05 | 18939.19 | 1.9833 | 0.65578 | 0.12 / 0.07 ✓ | 0.76 / 0.37 ✓ | 6,545,217 | inside its pre-registered band; the only case in the campaign that passes both windows; single mesh; not validated |

## 3. Diagnostic / non-performance cases (design RPM)

| Case | Classification | What it is | Thrust [N] | Torque [N·m] | η_p | Convergence | Interpretation |
|---|---|---|---:|---:|---|---|---|
| **V03** | diagnostic | first CFD state: PRIME derivative with the camber on the wrong side of the chord | −845.78 | 5367.10 | undefined (net drag) | not evaluable (1 stored checkpoint) | the drag state that led to the camber-orientation check |
| **V04cf** | diagnostic | V03 with the camber sign corrected | 4209.88 (last checkpoint) | 19052.16 | 0.36252 (last checkpoint) | unsettled; diverged at iteration 246 | thrust became positive; the value is not settled |
| **V14** | boundary-condition diagnostic | V08 case with zero-shear hub walls; no geometry change | 6247.89 | 18406.41 | 0.55690 | rolling 0.83 / 0.46 ✓; full 2.22 / 1.19 ✗ | the root windmill state deepened, so the hub boundary layer is not its cause in this model. **Not a design result.** |

## 4. Cases with no CFD result

| Case | Classification | What happened |
|---|---|---|
| V06, V06c | mesh investigation | two meshes of the V06e geometry rejected: 9.13 M cells exceeded memory; 7.61 M cells exceeded wall time |
| V07 | no result | CAD built; import failed (surface-export defect); never solved |
| V08b | no result | CAD built (0.016c trailing edge); import failed; not re-attempted |
| V09 | mesh investigation | PRIME's 0.006c trailing edge; tetrahedral initialisation failed at the 7.24 mm size floor |
| V09b | failed solve | 0.008c trailing edge meshed; the solve diverged near iteration 460–470; no result is reported |
| V13 | mesh investigation | V09 geometry at a 2.5 mm size floor; tetrahedral initialisation failed. **No CFD result — not a falsified redesign** |
| V16 | unrun control | mirror of V15 (+2.40° root re-pitch); CAD built and volume mesh generated (6,181,870 cells, −5.99 % vs V08); **not solved — no CFD result** |
| +7 % RPM point | no result | thrust oscillated 36 % peak-to-peak and never settled; not used |

## Data-quality notes

- **Stale `rpm` field.** The stored `rpm` field in the recorded result files reads 1294.49 for every case,
  including V11 (ω = −104.72 rad/s, i.e. 1000 rpm). Operating conditions in this repository are determined from
  the ω field and the case definition. The recorded files are published unchanged; `campaign_summary.json`
  lists the stored field and the value implied by ω side by side.
- **ω sign.** V03–V06e record |ω| (positive); V08 onward record the signed value (negative). The journals from V04cf
  onward all set ω = −135.559 rad/s about +z, so this is a difference in how ω was recorded, not in the rotation of
  the rotor. |ω| is used for shaft power throughout.
- **Iteration counts.** Fluent's own default residual stop ended six runs before 600 iterations: V06e at 592,
  V08 at 590, V10 at 571, V11 at 547, V14 at 593 and V15 at 570 (from the solver logs). V12 ran all 600;
  V05n16's solver log is not in the extracted set. That stop is not the convergence criterion used here.
- **Span accounting.** The CFD blade wets r = 0.565–1.725 m against a design span of 0.490–1.750 m, so T and Q
  are each about 3 % low; η_p is affected at second order only.
- **Sectional polars.** The polars for V04cf, V05n16 and V06e were computed on a zero-induction basis because of
  an extraction defect found later; the published files for those cases have not been regenerated. The later
  cases use the corrected basis.
