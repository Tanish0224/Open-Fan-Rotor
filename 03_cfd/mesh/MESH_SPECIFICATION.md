# MESH SPECIFICATION — preliminary workstation-scale mesh (CFG-ISO-PRELIM)
### BA-OF-01 · written BEFORE mesh generation, per task requirement

**Status:** target values only — no mesh has been generated against this spec yet at the time
of writing. This is **not** `CFD_SETUP_SPECIFICATION.md` (the frozen production spec, y+≈1,
0.9–4.3 M cells, full 8D/8D/15D domain) — it is a deliberately reduced **preliminary** target,
explicitly labelled as such, for the Day-1 workflow-demonstration case only.

---

## 1. Why these numbers, not others

| Parameter | Value | Traced to |
|---|---|---|
| Max blade chord | 0.279 m | `01_design/results/design_table.csv`, r/R ≥ 0.32 |
| Chord Reynolds range | 3.6 (root, ~0 chord) – 2.24×10⁶ (outboard) | same table |
| Domain (preliminary, reduced) | upstream 7 m, downstream 10.5 m, radial 7 m, hub 0.49 m | `geometry_transfer/build_fluid_domain.py` — explicit reduction from the frozen 8D/8D/15D spec, documented there |
| Wall treatment | **wall functions**, target y⁺ 30–100 | `00_requirements/COMPUTATIONAL_FEASIBILITY_AUDIT.md` §2, "Preliminary isolated (Stage 1)" row — NOT the resolved y⁺≈1 production target |
| Machine | 8 cores, 15.2 GB RAM (~3–4 GB reliably free during this session) | measured this session |

## 2. Cell budget

Feasibility audit's own Stage-1 preliminary row: 1.0–1.8 M cells for a **30° sector**. This
domain is a smaller **22.5° sector** with a **reduced radial/axial extent** (2D/2D/3D vs the
production 8D/8D/15D), so the target here is deliberately lower:

**Target: 150,000–400,000 cells total.** This is a workflow-demonstration mesh, not a
resolved production mesh — cell count is bounded by what this machine can reliably mesh and
hold in memory alongside SolidWorks/Fluent Meshing overhead (observed 3–4 GB free RAM during
this session, well below the nominal 12 GB usable).

## 3. Surface sizing

| Region | Target size | Basis |
|---|---|---|
| Blade surface | 3–8 mm, curvature-driven | ~1–3% of max chord (0.279 m); enough to resolve LE/TE curvature at coarse fidelity, not a resolved boundary layer |
| Hub | 15–30 mm | one order coarser than the blade, hub is a plain cylinder (spinner not modelled, item O9) |
| Farfield / inlet / outlet | 200–500 mm | far from the blade, no strong gradients expected in the preliminary wall-function solve |
| Periodic faces | must match on both sides exactly (Fluent's `make-periodic` requires this) | rotational periodicity, 22.5° |

## 4. Boundary layer (blade + hub walls)

Wall-function target y⁺ 30–100, **not** the production y⁺≈1 stack (3.2 µm / 32 layers).

```
first cell height ~ 1.0e-4 m   (scaled from the y+=1 value of 3.2 um in
                                 CFD_SETUP_SPECIFICATION.md S7, linearly to y+~30)
growth rate        1.2
number of layers   5-6          (enough to blend into the tet region; wall
                                 functions do not require resolving the full
                                 ~5 mm boundary-layer thickness)
```

This is an **estimate for mesh generation**, not a measured y⁺ — the actual y⁺ achieved can
only be confirmed after a solution exists (§10 of `CFD_SETUP_SPECIFICATION.md`).

## 5. Wake refinement

A refinement region trailing the blade (downstream, along +Z from the trailing edge to
roughly 2 chord-lengths downstream) at ~2× the blade surface sizing, to keep the wake from
being smeared into the coarse far-field cells immediately behind the blade.

## 6. Volume mesh

Tetrahedral core (`mesh/auto-mesh`), poly-hexcore explicitly **deferred** — the production
spec's Mosaic poly-hexcore topology is a Stage-2 refinement, not required to demonstrate the
workflow end-to-end.

## 7. Acceptance gate (must ALL pass before proceeding to solver setup)

| Check | Requirement |
|---|---|
| `mesh/check` | no errors, no negative-volume cells |
| Max skewness | < 0.95 (relaxed vs the production 0.85 gate — preliminary tet mesh, not Mosaic poly) |
| Min orthogonal quality | > 0.10 (relaxed vs the production 0.15 gate) |
| Zone count/type | blade (wall), hub (wall), inlet (pressure-far-field), outlet (pressure-outlet), farfield (pressure-far-field), 2 periodic faces correctly paired |
| Periodic pairing | `mesh/modify-zones/make-periodic` must report a valid periodic pair, not an error |

A mesh that fails any of these is **not** used for a solver run — the failure is diagnosed and
recorded, per the task's stop condition.
