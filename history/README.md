# History — superseded, failed and diagnostic material

> **NOT FOR CURRENT PERFORMANCE CLAIMS.** Everything in this folder is kept for the record. Nothing here is a
> current result. Current results are in [`../RESULTS.md`](../RESULTS.md).

| Label | Meaning |
|---|---|
| **HISTORICAL** | a dated record of an earlier project state |
| **SUPERSEDED** | replaced by a later artefact that is current |
| **FAILED** | the attempt did not produce its output (mesh, import or solve) |
| **UNCONVERGED** | a solution exists but did not settle; its values are not used |
| **DIAGNOSTIC** | answers a diagnostic question, not a performance question |

## Contents

| Path | Label | What it is |
|---|---|---|
| `superseded_geometry/openfan_blade_v02_G1_VERIFIED.step` | SUPERSEDED | The v02 blade. It passed its own geometry gate, but a later coordinate check showed the sweep had been built as 0.757 m of axial rake, with the tip at 1.879 m against a 1.75 m design radius. Replaced by the v03 PRIME blade. The "VERIFIED" in its name refers to that earlier gate only. |
| `drawings_2026-08/*.pdf` | HISTORICAL | Reference drawings of the structural assembly, dated 29 August 2026 (not for manufacture). Their note blocks say that no FEA or CFD had been performed on the geometry. That was true on that date; screening FEA and the CFD campaign came later. D02's note also calls PRIME the "authoritative aerodynamic master"; that label predates the camber-side error later found through CFD ([`../README.md`](../README.md) §7). The reports, studies and decision records cited in the note blocks are not published; the two verification files they cite are in [`../structural/verification/`](../structural/verification/). The document author field was removed from these copies. |
| `no_result_cases/` | FAILED | Mesh-quality records for V06, V06c (meshes rejected on memory and wall time), V09b (meshed; solve diverged) and V16 (meshed; not solved). See below. |

## Project states that are superseded (summary)

- **Before 15 September 2026 — pre-CFD state.** The project had a 22.5° periodic-sector fluid domain and no volume mesh. Its original volume check was
  later found too coarse to detect that the domain held only about half a blade. The sector approach was abandoned: the blade spans 36.7° of azimuth, more than the 22.5° pitch,
  and the sector boundaries broke the surface tessellation. The 360° annulus used for every result replaced it.
- **The first 360° mesh (4.0 M cells).** Rejected on measured quality after three diverged solves.
- **V03.** The first solution: net drag. It is DIAGNOSTIC and superseded by the camber correction.
- **V04cf.** UNCONVERGED: it diverged at iteration 246. It is kept in `cfd_campaign/` as a diagnostic.
- **+7 % RPM point.** UNCONVERGED: thrust oscillated 36 % peak-to-peak. Not used.
- **Earlier required-lift-to-drag estimates.** They were computed on different angle and loss bases and are
  superseded. None is used as a target here.
