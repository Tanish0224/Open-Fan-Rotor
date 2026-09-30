"""
case_omega.py -- the ONE declared table of rotational speed per case tag.

WHY THIS MODULE EXISTS
----------------------
Every case in this project from v03 through v10 ran at omega = 135.559045147
rad/s (1294.49 rpm). v11 is the first to change it: 104.719755 rad/s, 1000 rpm.

When that constant was surveyed across the post-processing chain it turned out to
be baked in as a literal in SIX separate tools, each of which would have produced
confident, plausible, wrong numbers for v11:

    sectional_polar_from_cfd.py    phi, W, q, M_rel, Cl AND Cd -- all of them
    make_velocity_triangle_figure.py  phi, and hence alpha
    analyse_blade_loading.py       the Cp normalising dynamic pressure
    wall_treatment_check.py        the flat-plate Re and Cf reference
    convergence_character.py       eta_p, printed directly in the report
    verify_case.py                 the case gate's expected rotation

Copying a corrected map into each of them would leave six copies to drift out of
step the next time an operating point changes. So the table lives here once, and
the tools import it.

THE RULE
--------
resolve() RAISES on an unknown tag. It does not default. A default is exactly how
one hard-coded speed survived ten cases without being noticed, and adding a
seventh copy of a default would have repeated the mistake at the moment it was
being fixed.

If a new case is added, declare it here with a note saying WHY its speed is what
it is. "Same as last time" is a legitimate note; silence is not.
"""
from __future__ import annotations

DESIGN_OMEGA = 135.559045147       # rad/s, magnitude; rotation is about -z
DESIGN_RPM = 1294.49

# tag -> (|omega| rad/s, note)
OMEGA_FOR = {
    "v03":    (DESIGN_OMEGA, "design speed; PRIME-derived baseline"),
    "c6":     (DESIGN_OMEGA, "design speed; v03 case, early tag"),
    "c6n":    (DESIGN_OMEGA, "design speed; v03 case"),
    "v04cf":  (DESIGN_OMEGA, "design speed; camber orientation corrected"),
    "v05n16": (DESIGN_OMEGA, "design speed; NACA 16-series sections"),
    "v06":    (DESIGN_OMEGA, "design speed; low-Cl / thin-root redesign"),
    "v06c":   (DESIGN_OMEGA, "design speed; v06 variant"),
    "v06e":   (DESIGN_OMEGA, "design speed; v06 accepted mesh"),
    "v07":    (DESIGN_OMEGA, "design speed; intermediate loading experiment"),
    "v08":    (DESIGN_OMEGA, "design speed; TE 0.020c -> 0.012c only"),
    "v08b":   (DESIGN_OMEGA, "design speed; TE 0.016c variant"),
    "v09":    (DESIGN_OMEGA, "design speed; TE 0.006c, never volume-meshable"),
    "v09b":   (DESIGN_OMEGA, "design speed; TE 0.008c, DIVERGED"),
    "v10":    (DESIGN_OMEGA, "design speed -- v10 changes beta, NOT the speed"),
    "v12":    (DESIGN_OMEGA,
               "design speed. v12 changes SWEEP only -- Lambda(r) + 6.00 deg -- and "
               "deliberately does NOT change the operating point. It is the first case "
               "to move M_normal while HOLDING M_rel fixed."),
    "v14":    (DESIGN_OMEGA,
               "design speed. v14 is v08's case with the HUB WALL SHEAR set to "
               "zero -- a BOUNDING test of how much of the root loss is the "
               "duct-wall hub artefact. Geometry, mesh and RPM are v08's exactly."),
    "v15":    (DESIGN_OMEGA,
               "design speed. v15 is v08's geometry with a LOCAL ROOT DE-PITCH -- "
               "d_beta = -2.40 deg at the root tapering linearly to EXACTLY 0.00 deg "
               "at r/R 0.55 and outboard. RPM, chord, camber, t/c, sweep and the "
               "trailing edge are v08's. This is NOT v10: v10 de-pitched the WHOLE "
               "blade and was falsified."),
    "v11":    (104.719755,
               "1000 rpm. OFF-DESIGN BY DESIGN: v11 tests whether lowering M_rel "
               "recovers the sections' lift response, and rotational speed is the "
               "only variable that moves M_rel. The blade is re-twisted to match. "
               "Its eta_p is NOT a design-RPM result and must never be substituted "
               "for one -- v08 remains the design-RPM benchmark."),
}


def resolve(tag):
    """|omega| in rad/s for a declared tag. Raises on anything undeclared."""
    if tag not in OMEGA_FOR:
        raise SystemExit(
            "REFUSING to run: tag %r has no declared rotational speed in "
            "case_omega.py. Add it explicitly, with a note saying why its speed is "
            "what it is. Do NOT default to the design value -- that assumption was "
            "correct for ten consecutive cases and silently wrong for the eleventh."
            % tag)
    return OMEGA_FOR[tag][0]


def note(tag):
    resolve(tag)
    return OMEGA_FOR[tag][1]


def is_design_speed(tag):
    return abs(resolve(tag) - DESIGN_OMEGA) < 1e-9
