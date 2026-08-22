# CFD STATUS — BA-OF-01 CFG-ISO preliminary case
### Updated 22 August 2026 · geometry transfer + boundary zone setup complete; volume mesh BLOCKED

**Claim discipline for everything below:**
**PRELIMINARY WORKSTATION-SCALE CFD PREPARATION — NOT VALIDATED, NOT MESH-INDEPENDENT, NOT A
FINAL PERFORMANCE PREDICTION.** No solve has been run. No performance number exists.

---

## 1. What is COMPLETE (independently verified, not just console-claimed)

| Item | Status | Evidence |
|---|---|---|
| CAD master (single blade) | G1 PASS | `02_cad/openfan_blade_v02_G1_VERIFIED.SLDPRT` — `Check2()=0`, volume inside independent bracket |
| Fluid-domain derivative (22.5° sector, blade subtracted) | Built, verified | `geometry/domain_CFG-ISO_v01.SLDPRT`, `domain_verification_v01.json` — Check2=0, volume within 0.0006% of analytic wedge-minus-blade |
| Geometry transfer into ANSYS (item O10) | **Resolved** | STEP export imports cleanly via **Fluent Meshing's own CAD translator**, independent of the unrelated SolidWorks-side reimport failure |
| Boundary zone separation | 10 raw zones, then classified | `zone_definition/ZONE_RECORD.json` — every zone's measured area/centroid/normal matched against analytic domain geometry to ≤0.16% |
| Zone naming + merge | Complete | inlet, outlet, hub, farfield, periodic-1, periodic-2, blade (4 loft-facet pieces merged into 1) |
| Boundary condition types | Complete | inlet=pressure-far-field, farfield=pressure-far-field, outlet=pressure-outlet, hub=wall, blade=wall |
| **Periodic pairing** | **Complete, independently verified** | `zone_definition/domain_9zones_typed_periodic.msh.h5` read back with h5py: periodic-1↔shadow-14 (20↔20 faces), periodic-2↔shadow-15 (2↔2 faces) — matching face counts confirm a valid periodic interface, not just a console message |
| Mesh specification (written BEFORE meshing) | Complete | `mesh/MESH_SPECIFICATION.md` — every target traced to blade geometry, Reynolds range, and measured machine RAM |

## 2. What is BLOCKED, and why (honest, evidenced)

**Volume mesh generation (prism layers + tet fill) did not complete this session.**

Root cause is **not** a geometry or command-syntax failure — the zone-selection portion of
`mesh/prism/create` was confirmed working (`hub`, `blade` accepted, reached the
`Offset Method [uniform]` prompt). The blocker is a **reproducible process-level instability**:
across three independent clean-process attempts (fresh `taskkill` of all `fluent`/`cx2510`/
`fl2510`/`mpiexec`/`hydra_pmi_proxy` processes, confirmed ≥4.7 GB free RAM before each launch),
Fluent Meshing hung at the identical point in startup (immediately after
`Graphics driver currently in use: dx11`, before `Reading journal file...`) for 5+ minutes with
no progress, on 2 of 3 attempts. This is consistent with either a licence-server round-trip
delay (`1055@akash3.cc.iitk.ac.in`, a remote IIT Kanpur server) or a resource contention effect
from the many repeated Fluent restarts already performed in this session — not with anything
wrong in the mesh specification or the TUI commands themselves.

**What is confirmed, narrowly:**
- `/mesh/prism/create` exists and accepts a blank-terminated zone list (`hub`, `blade`, blank).
- It then prompts `Offset Method [uniform]>`, which does **not** accept a blank line (errors
  "Invalid option chosen") — an explicit value (e.g. `uniform`) is required.
- The exact remaining prompt sequence (first height / growth rate / number of layers, and the
  `mesh/auto-mesh` tet-fill prompts) was **not** reached before the process instability
  interrupted the run.

**Not attempted further per the task's explicit stop condition** ("do not spend hours chasing
...", "stop and diagnose... rather than spending hours tuning").

## 3. GitHub-ready files created this session

```
03_cfd/
  geometry/
    domain_CFG-ISO_v01.SLDPRT          fluid-domain derivative (SolidWorks master)
    domain_CFG-ISO_v01.step            STEP export (verified importable into Fluent)
    domain_verification_v01.json       independent geometric verification record
  zone_definition/
    ZONE_RECORD.json                   labeled, analytically-cross-checked zone classification
    build_zone_record.py               the classification script (reproducible, not hand-labeled)
    domain_10zones_separated.msh.h5    raw feature-angle-separated mesh (pre-naming)
    domain_9zones_typed_periodic.msh.h5   FINAL boundary-conditioned mesh: named zones,
                                        correct BC types, verified periodic pairing
    zone_classification_raw.json       raw geometric measurements (centroid/normal/area) per zone
  mesh/
    MESH_SPECIFICATION.md              preliminary mesh targets, written before generation
    prism_create_attempt.jou           the journal that reached (but did not complete) prism
                                        creation -- kept as evidence, not a working recipe yet
  setup/
    boundary_zone_setup.jou            the WORKING journal that produced domain_9zones_typed_periodic.msh.h5
                                        (reproducible: read v01 STEP -> separate -> rename -> type -> pair)
  CFD_STATUS.md                        this file
```

Not yet created (correctly, since nothing exists to put in them): `03_cfd/results/`,
`03_cfd/screenshots/` (no mesh or solution exists to screenshot), `03_cfd/logs/` beyond what's
implicit in the `.jou`/`.log` pairs already present in `geometry_transfer/`.

## 4. Exact resume-safe claims (today)

- "Built and independently geometrically verified a CAD fluid-domain derivative for a 22.5°
  periodic-sector isolated-rotor CFD case."
- "Established a working, reproducible geometry-transfer route from SolidWorks into ANSYS Fluent
  Meshing via STEP, diagnosing and resolving an initial translator ambiguity."
- "Automated boundary-zone identification via feature-angle separation, cross-checked every zone
  against the domain's analytic geometry (not by name or assumption), and assigned physically
  correct boundary condition types."
- "Verified rotational periodic connectivity independently by reading the mesh file's own zone
  topology (matching face counts across each periodic pair), not by trusting solver console
  output alone."

## 5. Exact claims that must wait

- Any statement that a volume mesh, surface mesh quality metric, or cell count exists.
- Any CFD solver run, residual, thrust, torque, or contour.
- Any statement that the boundary-layer/prism strategy in `MESH_SPECIFICATION.md` has been
  executed (it is a target, not yet a result).
- Any claim that periodic pairing has been validated inside the SOLVER (only the meshing-side
  topology has been verified so far — solver-side periodic behaviour is unverified until a case
  actually runs).

## 6. Next technical step (unchanged priority, next session)

1. Re-attempt `mesh/prism/create` on a machine/session with confirmed Fluent process stability
   (e.g. after a reboot, or with a longer per-launch timeout budget) — the zone selection and
   BC-type work already reached is directly reusable (`setup/boundary_zone_setup.jou` regenerates
   `domain_9zones_typed_periodic.msh.h5` from the verified STEP export in ~2 minutes).
2. Discover the `Offset Method` follow-on prompts (first height, growth rate, layers) the same
   way the periodic-pairing prompts were discovered — one clean probe at a time, not a blind
   multi-step guess.
3. `mesh/auto-mesh` for the tet fill, `mesh/check` + `mesh/quality`, gate per
   `mesh/MESH_SPECIFICATION.md` §7.
4. Only once the mesh gate passes: solver setup, verified against `setup_iso_sector.jou`, one
   PRELIMINARY run.
