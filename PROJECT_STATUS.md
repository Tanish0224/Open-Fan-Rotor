# PROJECT STATUS — BA-OF-01 Boeing Open-Fan Rotor
### Last updated 22 August 2026 · read this first when resuming after a break

---

## Last verified milestone

**Boundary-zone / periodic-topology setup for the isolated-rotor CFD sector — PASS, independently
verified.** See `03_cfd/CFD_STATUS.md` for the full technical detail; see
`BOEING_OPEN_FAN_PROJECT_REPORT.md` §11–13 for the complete verification hierarchy.

Before that: aerodynamic design (Gate G0 — PASS) and CAD blade geometry (Gate G1 — PASS) are
both complete and independently verified. **No CFD solution exists yet.**

## Current blocker

Volume mesh generation (`mesh/prism/create` → `mesh/auto-mesh`) has not been completed.
Not a command-syntax problem — the zone-selection step of `mesh/prism/create` was confirmed
working. The blocker is a **reproducible Fluent Meshing process stall at startup** (hangs after
graphics-driver init, before journal execution, on repeated clean-process attempts). Root cause
not diagnosed (candidates: remote license-server latency, session-restart resource contention —
neither confirmed).

## Exact next restart point

```
"D:\ANSYS Inc\v251\fluent\ntbin\win64\fluent.exe" 3ddp -meshing -hidden -t1 \
  -i 03_cfd/setup/boundary_zone_setup.jou -o resume.log
```

This regenerates `domain_9zones_typed_periodic.msh.h5` (the verified boundary mesh) from the
verified STEP export in ~2 minutes. From there, resume at: discover the `mesh/prism/create`
offset-method/height/growth/layer prompt sequence (one clean probe at a time — see
`BOEING_OPEN_FAN_PROJECT_REPORT.md` §15 for the full continuation sequence).

**Before restarting ANSYS:** reboot the machine, or at minimum confirm no stray
`fluent.exe`/`cx2510.exe`/`fl2510.exe`/`mpiexec.exe`/`hydra_pmi_proxy.exe` processes are running
and ≥4 GB RAM is free — the stall was never observed on a genuinely clean first launch.

## Authoritative files (use these, not older/alternate versions)

| Purpose | File |
|---|---|
| Aerodynamic design module | `01_design/openfan_design.py` |
| Design results (G0-verified) | `01_design/results/design_summary.json` |
| CAD master (CFD-relevant single blade) | `02_cad/openfan_blade_v02_G1_VERIFIED.SLDPRT` |
| CAD build script (v02, working) | `02_cad/build_rotor_cad_v02.py` |
| Fluid-domain derivative | `03_cfd/geometry/domain_CFG-ISO_v01.SLDPRT` / `.step` |
| Fluid-domain build script | `03_cfd/geometry_transfer/build_fluid_domain.py` |
| **Working boundary-zone-setup journal** | `03_cfd/setup/boundary_zone_setup.jou` |
| Verified boundary-typed periodic mesh | `03_cfd/zone_definition/domain_9zones_typed_periodic.msh.h5` |
| Zone classification record | `03_cfd/zone_definition/ZONE_RECORD.json` |
| Mesh targets (not yet executed) | `03_cfd/mesh/MESH_SPECIFICATION.md` |
| Frozen production CFD spec | `03_cfd/CFD_SETUP_SPECIFICATION.md` |
| Pre-generated solver journal (untested against a real mesh) | `03_cfd/cases/CFG-ISO/setup_iso_sector.jou` |
| Full technical report | `BOEING_OPEN_FAN_PROJECT_REPORT.md` |
| Evidence-to-artifact index | `EVIDENCE_INDEX.md` |
| Decision log (all ED- entries) | `00_requirements/DECISION_LOG.md` |

**Explicitly superseded, kept as history — do not build on these:**
`02_cad/openfan_blade_v01.SLDPRT`, `02_cad/build_rotor_cad.py` (archived as
`build_rotor_cad_v01_FAILED_ARCHIVE.py`), everything under `03_cfd/geometry_transfer/` named
`test_*`, `probe_*`, `import_*`, `full_pipeline1..10.jou`, `mesh_pipeline1..2.jou` (exploratory
attempts that led to the working `full_pipeline11.jou`, copied as `setup/boundary_zone_setup.jou`).

## Known open items

| ID | Item | Status |
|---|---|---|
| O6 | v01 `Check2()=6` | **CLOSED** — root cause diagnosed (ED-018), fixed in v02 |
| O7 | Fluent licensed parallel core count | unconfirmed |
| O8 | 16-blade presentation pattern | blocked — SolidWorks installation-level API limitation (3 independent paths failed identically); not a CFD blocker, CFD only needs the single-blade sector |
| O9 | Spinner/hub fairing | deferred — hub currently modeled as a plain cylinder |
| O10 | SolidWorks-side STEP reimport | unverified (decoded `swFileRequiresRepairError`); does not block CFD, which uses ANSYS's own STEP translator instead |
| O11 (new) | Fluent Meshing startup stall | unresolved — see "Current blocker" above |

## Forbidden claims (until the corresponding work actually exists)

Do not state or imply: a CFD solution exists; a mesh exists; thrust/torque/power/efficiency has
been predicted by CFD; validation against experimental or published data has occurred; an
installed configuration has been studied; the rotor has been optimized. See
`BOEING_OPEN_FAN_PROJECT_REPORT.md` §14 for the full safe/forbidden claim lists.

## Recommended next command/workflow after resuming

1. Read this file, then `BOEING_OPEN_FAN_PROJECT_REPORT.md` §12 and §15.
2. Reboot (or verify clean process state) before touching ANSYS.
3. Run the restart command above; confirm `domain_9zones_typed_periodic.msh.h5` regenerates
   identically (9 face zones, 2 periodic face-pairs, matching face counts) before doing anything
   new.
4. Proceed to prism-layer discovery per the continuation plan — do not re-attempt the earlier
   failed TUI guesses; start from the confirmed-working `Offset Method [uniform]>` prompt.
