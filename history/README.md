# History

Earlier and superseded material, kept for the record. Current results are in [`../RESULTS.md`](../RESULTS.md).

| Path | Status | What it is |
|---|---|---|
| `superseded_geometry/openfan_blade_v02_G1_VERIFIED.step` | superseded | The v02 blade. It passed its own geometry check, but a later coordinate check showed the sweep had been built as 0.757 m of axial rake, with the tip at 1.879 m against a 1.75 m design radius. PRIME (v03) replaced it. "VERIFIED" in the name refers to that earlier check only. |
| `drawings_2026-08/*.pdf` | historical | Reference drawings of the structural assembly, dated 29 August 2026 (not for manufacture). Their notes say no FEA or CFD had been done on the geometry; that was true on that date, and both came later. D02's note calls PRIME the "authoritative aerodynamic master"; that label predates the camber error found through CFD (see [`../cfd_campaign/`](../cfd_campaign/README.md)). The reports cited in the note blocks are not published; the two check files they cite are in [`../structural/verification/`](../structural/verification/). The author field was removed from these copies. |
| `no_result_cases/` | no result | Mesh-quality records for V06 and V06c (meshes rejected on memory and wall time), V09b (meshed; solve diverged) and V16 (meshed; not solved). |

## Earlier project states

- **Before 15 September 2026.** The CFD domain was a 22.5° periodic sector with no volume mesh. Its volume check
  was too coarse to notice that the domain held only about half a blade: the blade spans 36.7° of azimuth, more
  than the 22.5° pitch, and the sector boundaries broke the surface tessellation. It was replaced by the 360°
  annulus used for every result.
- **The first 360° mesh (4.0 M cells)** was rejected on measured quality after three diverged solves.
- **V03**, the first solution, gave net drag. The camber correction superseded it; it is kept as a diagnostic.
- **V04cf** diverged at iteration 246. It is kept in `cfd_campaign/` as a diagnostic.
- **The +7 % RPM point** never settled (thrust oscillated 36 % peak-to-peak) and is not used.
- **Earlier required lift-to-drag estimates** were computed on different angle and loss bases and are not used.
