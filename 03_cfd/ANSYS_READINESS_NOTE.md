# ANSYS READINESS NOTE
### BA-OF-01 — toolchain verification only. Fluent has NOT been run.

**Created:** 22 August 2026 · **Applies to:** the transition from verified CAD (v02) to meshing

---

## 1. WHAT GEOMETRY ENTERS THE FLUID-DOMAIN WORKFLOW

**Master:** `02_cad/openfan_blade_v02_G1_VERIFIED.SLDPRT` — one blade, gate G1 PASS (independently
verified: `Check2()=0`, single solid body, volume inside an independent bracket, radial extent
correct to ~1×10⁻⁵ m).

**Route into ANSYS:**

| Path | Status |
|---|---|
| Native SLDPRT (SolidWorks add-in/direct import, if the ANSYS install has one) | Not yet attempted |
| STEP (`02_cad/export/openfan_blade_v02_G1_VERIFIED.step`) | **File exists (477,222 bytes) but reimport is UNVERIFIED** — triggers a decoded `swFileRequiresRepairError` on `OpenDoc6` reopen in SolidWorks itself, across every tried option. Open item **O10**. Must be re-attempted specifically inside the ANSYS/SpaceClaim import path before being trusted, since a different translator may handle it differently — or the STEP export may need to be regenerated after resolving O10. |
| STL (`02_cad/export/openfan_blade_v02_G1_VERIFIED.stl`, 107,984 bytes) | Exists; **tessellated visualisation format only** — not claimed as a meshing-ready engineering interchange format |

**Recommended immediate action, not yet performed:** attempt the STEP import directly in ANSYS
SpaceClaim/DesignModeler and record whether it succeeds there independent of the SolidWorks-side
reopen failure — different translators can behave differently on the same file.

## 2. WHAT IS INSTALLED

| Tool | Location | Status |
|---|---|---|
| ANSYS Fluent | `D:\ANSYS Inc\v251\fluent\ntbin\win64\fluent.exe` | Confirmed present, version 2025 R1 |
| ANSYS Workbench | `D:\ANSYS Inc\v251\Framework\bin\Win64\RunWB2.exe` | Confirmed present |
| SpaceClaim / DesignModeler | Not separately confirmed in this session | **TBD** — check under the same `v251` tree before assuming either is available |

## 3. PROPOSED ROTATING-FRAME / SLIDING-MESH APPROACH

Unchanged from `00_requirements/CFD_METHODOLOGY_ROADMAP.md` and
`03_cfd/CFD_SETUP_SPECIFICATION.md`, both written and frozen before this CAD recovery began:

- **Isolated rotor (CFG-ISO):** single rotating reference frame (SRF) over a 22.5° periodic
  sector — exact for this axisymmetric isolated configuration, not an approximation.
- **Not sliding mesh, not MRF** for the isolated case — no stationary body exists in it.
- Compressible, ideal gas, k-ω SST baseline + Spalart–Allmaras sensitivity, `y⁺≈1` wall-resolved
  target (first cell 3.2 µm, ~32 prism layers).
- Fluent solver journal already generated from the Phase 1 design values:
  `03_cfd/cases/CFG-ISO/setup_iso_sector.jou` — traceable to `design_summary.json`, not hand-typed.

**None of this has changed as a result of the CAD recovery.** The recovery only replaced *how* the
blade solid was built; the design point, operating condition, and CFD methodology are untouched.

## 4. MACHINE-AWARE MESH BUDGET (measured, re-stated for this note)

| | |
|---|---|
| CPU | AMD Ryzen 7 6800H, **8 physical cores** |
| RAM | **15.2 GB** total, ~12 GB usable |
| Practical cell ceiling | **~5 M cells** at ~2 GB/M-cell for a coupled compressible solve |
| Mesh-independence triplet | **0.9 M / 2.0 M / 4.3 M** cells (re-cut from the original 6.5–8.5 M "fine" mesh, which is **not achievable** on this machine) |

**Not yet tested:** whether these cell counts are actually achievable in practice on this geometry
— the triplet is a *plan*, not a *measured* result. The mandatory calibration run
(`00_requirements/COMPUTATIONAL_FEASIBILITY_AUDIT.md` §1) has **not** been executed.

**Also not yet confirmed:** Fluent's licensed parallel core count (open item **O7**) — if capped
below 8, every runtime estimate in the feasibility audit roughly doubles.

## 5. WHAT REMAINS UNRESOLVED BEFORE MESHING CAN BEGIN

| # | Item | Status |
|---|---|---|
| 1 | STEP reimport verification (O10) | **Blocking** — must resolve or find an alternative import route before the fluid domain can be built from this geometry |
| 2 | Fluid-domain construction (subtract the blade from a bounding sector volume) | **Not started** — requires the domain dimensions in `CFD_SETUP_SPECIFICATION.md` §2.3 to be built as CAD, on a *derivative*, never the blade master |
| 3 | Mesh generation and quality check (`y⁺`, skewness, orthogonal quality) | **Not started** |
| 4 | Timing calibration run | **Not started** — mandatory gate before any expensive mesh is committed |
| 5 | Fluent licensed core count | **Unconfirmed** (O7) |

## 6. WHAT WILL CONSTITUTE THE PRELIMINARY FIRST CFD RUN

Per the Phase 1 authorisation's own staging (`00_requirements/PROJECT_ROADMAP.md`): a **coarse,
wall-function mesh, run to demonstrate the workflow end-to-end**, explicitly labelled
**PRELIMINARY**, grounding **no performance claim**. It requires, in order:

1. STEP (or an alternative) import resolved (item 1 above).
2. A fluid-domain derivative built and boolean-subtracted with the verified blade.
3. A coarse mesh (~0.9 M cells, the smallest step in the triplet).
4. The already-generated `setup_iso_sector.jou` journal run against that mesh.
5. Confirmation that thrust/torque monitors report physically sensible (non-NaN, correct-sign)
   values — not yet a mesh-independence claim, not yet a performance claim.

**None of steps 1–5 has been performed in this session.** This note establishes the plan and the
verified starting point (the G1-passed blade); it does not claim any CFD progress beyond that.
