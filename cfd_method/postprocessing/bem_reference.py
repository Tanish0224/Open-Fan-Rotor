"""
bem_reference.py -- the ONE declared table of which BEM design each CFD case
should be compared against.

THE DEFECT THIS FIXES
---------------------
The project quotes a single BEM reference throughout:

    T_BEM = 14451.5 N,  Q_BEM = 29372.3 N.m,  eta_BEM = 0.8072

Those are the numbers in 01_design/results/design_summary.json -- the v03/v04/v05
design, cl_root 0.70. They are the RIGHT reference for v03, v04cf and v05n16.

They are the WRONG reference for everything since. v06 changed the design
schedule (cl_root 0.70 -> 0.45, cl_tip 0.40 -> 0.26, toc_root 0.20 -> 0.12) and
re-ran the same Adkins-Liebeck code, which answered:

    T_BEM = 14451.5 N,  Q_BEM = 29818.2 N.m,  eta_BEM = 0.7951
    (01_design/results/design_summary_v06.json)

and v07 answered Q = 29601.4 N.m. v06e, v08, v08b, v09, v09b, v10 and v11 all
carry v06 aerodynamics, so v06's BEM is their design intent -- not v03's.

WHY THRUST IS UNAFFECTED AND TORQUE IS NOT
------------------------------------------
The design is specified by a NON-DIMENSIONAL loading tau = T/(rho A V0^2), held
fixed across all three designs. rho, A and V0 are identical, so every design
produces EXACTLY the same thrust, 14451.541505118192 N, by construction. Only
the torque needed to produce it -- and hence the efficiency -- changes with the
blade schedule.

So:
    T/T_BEM     was never affected by this defect
    Q/Q_BEM     was overstated by a factor 29818.2/29372.3 = 1.0152 for every
                v06-family case, i.e. reported roughly 1.5 % too HIGH
    eta vs BEM  the gap was overstated by 0.0121 for every v06-family case,
                because 0.8072 was used where 0.7951 was the design's own answer

NO CFD NUMBER CHANGES. T, Q, P_shaft and eta_p are measured from Fluent
transcripts and are untouched. What changes is the design-intent reference they
are compared against.

DISCOVERED HOW
--------------
By trying to reproduce the recorded design point before using the design code at
a different rotational speed. The reproduction check matched T to 0.000 % and
missed Q by 1.518 %, and refused to continue. Without that check the v11 BEM
comparison would have been built on an unreproduced design and the discrepancy
would have been invisible.

USAGE
    import bem_reference
    ref = bem_reference.resolve("v11")     # -> dict with T_N, Q_Nm, eta
"""
from __future__ import annotations

# family -> the BEM design that family's geometry was synthesised from
_FAMILIES = {
    "v03": {
        "source": "01_design/results/design_summary.json",
        "schedule": "cl_root 0.70, cl_tip 0.40, toc_root 0.20, n_blades 16",
        "T_N": 14451.541505118192,
        "Q_Nm": 29372.33898838303,
        "P_W": 3981686.226998358,
        "eta": 0.807207090017987,
    },
    "v06": {
        "source": "01_design/results/design_summary_v06.json",
        "schedule": "cl_root 0.45, cl_tip 0.26, toc_root 0.12, n_blades 16",
        "T_N": 14451.541505118192,
        "Q_Nm": 29818.17277864206,
        "P_W": 4042123.029900127,
        "eta": 0.7951379334288734,
    },
    "v07": {
        "source": "01_design/results/design_summary_v07.json",
        "schedule": "v07 intermediate loading experiment",
        "T_N": 14451.541505118192,
        "Q_Nm": 29601.412837184136,
        "P_W": None,
        "eta": None,
    },
}

# CFD case tag -> design family. This MIRRORS sectional_polar_from_cfd.py:_TABLE_FOR,
# and it must: a case compared against one design's table while being scored against
# another design's BEM is the same defect wearing a different hat.
_FAMILY_FOR = {
    "v03": "v03", "c6": "v03", "c6n": "v03", "v04cf": "v03", "v05n16": "v03",
    "v06": "v06", "v06c": "v06", "v06e": "v06",
    "v07": "v07",
    "v08": "v06", "v08b": "v06", "v09": "v06", "v09b": "v06",
    "v10": "v06",      # v08 geometry de-pitched; still v06 aerodynamics
    "v11": "v06",      # v08 geometry re-twisted; still v06 aerodynamics
    "v12": "v06",      # v08 geometry re-swept; still v06 aerodynamics
    "v14": "v06",      # v08 geometry unchanged; only the hub wall shear BC
    "v15": "v06",      # v08 geometry, inboard twist only; still v06 aerodynamics
}


def resolve(tag):
    """The BEM design intent for a CFD case tag. Raises on an undeclared tag."""
    if tag not in _FAMILY_FOR:
        raise SystemExit(
            "REFUSING: case tag %r has no declared BEM family. Add it explicitly and "
            "make it agree with sectional_polar_from_cfd.py:_TABLE_FOR. Do NOT default "
            "to the v03 numbers -- quoting 0.8072 against a v06-family rotor is the "
            "defect this module exists to fix." % tag)
    fam = _FAMILY_FOR[tag]
    d = dict(_FAMILIES[fam])
    d["family"] = fam
    d["tag"] = tag
    return d


def note(tag):
    d = resolve(tag)
    return ("BEM reference: %s family (%s), T %.1f N, Q %.1f N.m, eta %s"
            % (d["family"], d["source"], d["T_N"], d["Q_Nm"],
               "%.5f" % d["eta"] if d["eta"] is not None else "n/a"))
