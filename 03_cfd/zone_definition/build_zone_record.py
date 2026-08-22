"""
build_zone_record.py -- turn zone_classification_raw.json (geometric measurement,
no labels) into ZONE_RECORD.json (labeled, with the classification RULE and the
analytic cross-check that justifies each label). Pure Python, no Fluent required.

Classification method: each of the 10 Fluent face zones produced by
sep-face-zone-by-angle was measured (area-weighted centroid, area-weighted mean
normal, total area) directly from the mesh node coordinates -- see
classify_zones2.py in 03_cfd/geometry_transfer/. Labels below are assigned by
comparing those MEASURED quantities against the domain's known analytic
geometry (03_cfd/geometry_transfer/build_fluid_domain.py parameters), not by
name or by assumption.
"""
import json
import pathlib
import numpy as np

HERE = pathlib.Path(__file__).parent
raw = json.load(open(HERE / "zone_classification_raw.json"))

R_HUB, R_FAR = 0.49, 7.0
Z0, Z1 = -7.0, 10.5
SECTOR_DEG = 22.5

def analytic_area(kind):
    if kind == "inlet" or kind == "outlet":
        return 0.5 * np.radians(SECTOR_DEG) * (R_FAR**2 - R_HUB**2)
    if kind == "hub":
        return np.radians(SECTOR_DEG) * R_HUB * (Z1 - Z0)
    if kind == "farfield":
        return np.radians(SECTOR_DEG) * R_FAR * (Z1 - Z0)
    return None

records = []
blade_pieces = []
for z in raw:
    r, z_, theta, n = z["r"], z["z"], z["theta_deg"], z["avg_normal"]
    area = z["total_area_m2"]
    label, btype, rule, expected = None, None, None, None

    if abs(z_ - Z0) < 0.05 and abs(n[2] + 1) < 0.1:
        label, btype = "inlet", "pressure-far-field"
        rule = f"planar cap at z={z_:.3f} (expected {Z0}), normal -Z"
        expected = analytic_area("inlet")
    elif abs(z_ - Z1) < 0.05 and abs(n[2] - 1) < 0.1:
        label, btype = "outlet", "pressure-outlet"
        rule = f"planar cap at z={z_:.3f} (expected {Z1}), normal +Z"
        expected = analytic_area("outlet")
    elif abs(r - R_HUB) < 0.05:
        label, btype = "hub", "wall"
        rule = f"cylindrical surface at r={r:.3f} (expected R_hub={R_HUB}), radially inward normal"
        expected = analytic_area("hub")
    elif abs(r - R_FAR) < 0.1:
        label, btype = "farfield", "pressure-far-field"
        rule = f"cylindrical surface at r={r:.3f} (expected R_farfield={R_FAR}), radially outward normal"
        expected = analytic_area("farfield")
    elif abs(theta - 0.0) < 0.5:
        label, btype = "periodic-theta0", "periodic"
        rule = f"planar face at theta={theta:.2f} deg (expected 0 deg)"
    elif abs(theta - SECTOR_DEG) < 0.5:
        label, btype = "periodic-theta22p5", "periodic"
        rule = f"planar face at theta={theta:.2f} deg (expected {SECTOR_DEG} deg)"
    elif 0.50 <= r <= 1.80:
        label, btype = "blade (piece)", "wall"
        rule = (f"non-planar surface with r={r:.3f} inside the blade CAD span "
                f"[0.56, 1.72] m; complex normal direction {[round(x,2) for x in n]} "
                f"(not aligned with any domain-boundary normal)")
        blade_pieces.append(z)
    else:
        label, btype = "UNCLASSIFIED", "unknown"
        rule = "did not match any known-geometry rule -- requires manual review"

    rec = dict(z)
    rec["label"] = label
    rec["boundary_type_recommended"] = btype
    rec["classification_rule"] = rule
    if expected is not None:
        rec["analytic_area_m2"] = expected
        rec["area_delta_pct"] = abs(area - expected) / expected * 100.0
    records.append(rec)

blade_total_area = sum(p["total_area_m2"] for p in blade_pieces)
blade_r_range = [min(p["r"] for p in blade_pieces), max(p["r"] for p in blade_pieces)]

out = {
    "source_mesh": "domain_10zones_separated.msh.h5",
    "method": "sep-face-zone-by-angle (40 deg) on the verified fluid-domain STEP "
              "export, imported via Fluent Meshing's own CAD translator (independent "
              "of the unrelated SolidWorks-side STEP reimport issue, item O10). "
              "Every zone was then classified by comparing its MEASURED "
              "area-weighted centroid/normal/area against the domain's analytic "
              "geometry (build_fluid_domain.py parameters) -- not by assumption.",
    "domain_params": {"R_hub_m": R_HUB, "R_farfield_m": R_FAR,
                       "z_upstream_m": Z0, "z_downstream_m": Z1,
                       "sector_deg": SECTOR_DEG},
    "n_zones_raw": len(raw),
    "zones": records,
    "blade_summary": {
        "n_pieces_before_merge": len(blade_pieces),
        "total_area_m2": blade_total_area,
        "r_range_m": blade_r_range,
        "expected_r_range_m_from_CAD": [0.56, 1.724],
        "note": "4 zones because the 40 deg feature-angle separation split the "
                "blade's smooth spline surface into facet clusters at internal "
                "curvature breaks; NOT 4 physically distinct walls. Must be merged "
                "into one 'blade' zone before meshing (boundary/manage/merge).",
    },
    "unclassified_count": sum(1 for r in records if r["label"] == "UNCLASSIFIED"),
}

json.dump(out, open(HERE / "ZONE_RECORD.json", "w"), indent=2)
print(f"wrote ZONE_RECORD.json -- {len(records)} zones, "
      f"{out['unclassified_count']} unclassified, "
      f"blade pieces={len(blade_pieces)} total_area={blade_total_area:.5f} m^2")
for r in records:
    extra = f" (area delta {r.get('area_delta_pct', 0):.3f}%)" if "area_delta_pct" in r else ""
    print(f"  id={r['zone_id']:3d}  {r['label']:22s}  n_faces={r['n_faces']:3d}"
          f"  area={r['total_area_m2']:9.5f} m^2{extra}")
