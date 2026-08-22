# CAD VOLUME CROSSCHECK
### BA-OF-01 — v02 blade volume vs an independent reference built from the exact final CAD input

**Created:** 22 August 2026 · **Applies to:** `openfan_blade_v02_G1_VERIFIED.SLDPRT`

---

## 1. THREE DISTINCT QUANTITIES — KEPT SEPARATE, NEVER CONFLATED

| # | Quantity | What it is | Computed by |
|---|---|---|---|
| **1** | **Design idealisation** | The smooth, analytically exact NACA 4-digit closed-form curve (601 points) at each of the 21 stations. The mathematical shape the BEM design specifies. | `blade_geometry_reference.py`, no SolidWorks |
| **2a** | **CAD input geometry (polygon lower bound)** | The straight-edge polygon through the exact 48 arc-length-resampled points actually sent to `CreateSpline2` for every section in the v02 build. A polyline through these points always cuts every corner, so this is a **lower bound**. | Same file, shoelace formula on the exact CAD input points |
| **3** | **CAD-measured volume** | What SolidWorks actually built and measured, in a separate verification process. | `verify_cad_v02.py`, reopening the saved part |

## 2. WHY A BRACKET, NOT A SINGLE TARGET

The v02 blade surfaces are **smooth B-splines** through 48 points per section, not polylines. A smooth curve through points on a convex-ish aerofoil shape **bulges outward** between points rather than cutting the corner (the opposite of what a polyline does). The true section area therefore satisfies:

```
polygon_area (2a)  <=  true_spline_area  <=  smooth_closed_form_area (1)
```

This is why the reference is reported as a **bracket**, `[1594.01, 1611.19] cm³` for the whole blade, rather than as a single number the CAD result must match. Reporting a single target and then explaining away a "miss" would be exactly the failure mode this project's verification discipline exists to prevent.

## 3. RESULT

| | Value |
|---|---|
| (2a) Polygon lower bound (no SolidWorks) | **1594.01 cm³** |
| **CAD-measured volume (v02, independent reopen)** | **1600.60 cm³** |
| (1) Smooth closed-form upper bound (no SolidWorks) | **1611.19 cm³** |
| Bracket width | 1.08 % |
| CAD volume position in bracket | 1594.01 → **1600.60** → 1611.19 — **inside**, closer to the lower bound |

**The CAD volume falls inside the independently-computed bracket**, exactly where a spline-loft through 48 points on this section shape is expected to land. This is a positive, falsifiable cross-check — a result outside the bracket would have indicated either a CAD defect or an error in the reference calculation, and neither is the case here.

## 4. COMPARISON WITH THE HISTORICAL (v01) TARGET

The v01 verification compared against a single number (1611.19 cm³ — which is quantity **1**, the smooth closed-form target, unchanged and reproduced here for continuity). v01's polyline-based CAD volume (1586.71 cm³) was **also** inside a bracket, coincidentally close to the current lower bound — but v01's Check2/topology were invalid regardless of the volume agreement, which is exactly why **volume agreement alone was never a sufficient CAD verification criterion** in this project (see `VALIDATION_AND_VERIFICATION_PLAN.md`).

## 5. WHAT THIS CROSSCHECK DOES NOT ESTABLISH

- It does not independently verify that the spline **surface between sections** — as opposed to the section **area** at each station — is free of self-intersection. That is established separately, by the topology diagnostics in `verify_cad_v02.py` (single solid body, `Check2()=0`, non-degenerate bounding box) and the visual record (`diagnostics_archive/blade_v02_iso.png`, showing no rippling).
- It does not validate the **aerodynamic** correctness of the shape — that is Phase 1's BEM design and gate G0, unaffected by this CAD recovery.
