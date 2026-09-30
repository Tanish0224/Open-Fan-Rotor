"""
compute_performance.py -- turn Fluent force/moment reports into the project's
headline performance numbers, with the red-team checks built in.

USAGE
    python compute_performance.py <fluent_transcript.trn>

    P_shaft = Q * omega
    eta_p   = T * V0 / (Q * omega)

WHICH WALL ZONES COUNT -- CORRECTED 2026-09-15
----------------------------------------------
Measured from openfan_mrf.cas.h5, the wall zones are:

    id  8  blade         wall           2 faces
    id  9  blade:009     wall      343110 faces
    id  6  hub           wall        1752 faces
    id 10  hub:010       wall        1290 faces

Two corrections to the first version of this script, both of which would have
produced a wrong eta_p:

1. The blade surface is SPLIT across two zones by the MRF cell-zone separation.
   Zone `blade` retains only 2 of the 343,112 blade faces. Reporting on `blade`
   alone would capture ~0.0006% of the blade loading. ALL of them must be summed.

   Zones are therefore matched by PREFIX, not by a fixed list of names. The split
   chooses its own suffix, so a hard-coded "blade:009" would match nothing at all
   after the mesh is rebuilt -- and would report zero thrust rather than failing,
   which is the worst possible failure mode for this script.

2. `hub` is NOT a spinner. It is the inner cylindrical wall of the annular
   domain and it runs the full domain length, z = -7 m to +10.5 m. Its axial
   force is skin friction over 17.5 m of unphysical duct wall, and including it
   in thrust would be a straightforward error. Thrust and torque are taken from
   the BLADE zones only, which is also the quantity the Adkins-Liebeck design
   and the BEM estimate refer to.

The `net` row is likewise NOT used: it sums every wall zone, hub included.

SCALING -- THE POINT THAT MATTERS
---------------------------------
The CFD domain is a FULL 360 deg annulus containing ALL 16 blades. The force and
moment reported on the blade wall zones are therefore ALREADY full-rotor.
The sector scaling factor is 1, NOT 16. Multiplying by 16 here would be the
classic double-count to avoid, and this script asserts
against it rather than trusting a comment.

CAVEAT CARRIED WITH EVERY NUMBER
--------------------------------
The analysed geometry is the CFD DERIVATIVE blade (trailing edge 0.020 c versus
the design 0.006 c). A blunter TE adds base drag, which raises torque and so
LOWERS eta_p relative to the frozen PRIME design geometry. Results must be
reported as "computed on the CFD derivative blade", never as PRIME's performance.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bem_reference  # noqa: E402  -- per-design-family BEM, NOT one constant

DESIGN = pathlib.Path(__file__).resolve().parents[2] / "01_design" / "results" / "design_summary.json"
ETA_TARGET = 0.75
N_BLADES = 16
SECTOR_SCALING = 1                       # 360 deg domain => already full-rotor

# Zone selection is by PREFIX, not by a fixed list of names. The MRF cell-zone
# split renames whatever it cuts with a suffix it chooses itself -- the first
# build produced `blade` (2 faces) and `blade:009` (343,110 faces) -- and a
# hard-coded "blade:009" would silently match nothing after a remesh, reporting
# zero thrust rather than failing. Anything starting with "blade" counts;
# anything starting with "hub", plus the "net" summary row, is excluded.
BLADE_PREFIX = "blade"
EXCLUDE_PREFIX = ("hub", "net")

NUM = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
ROW = re.compile(r"^\s*([A-Za-z][\w:.\-]*)\s+((?:" + NUM + r"\s+){2,}" + NUM + r")\s*$")


def load_operating_point():
    d = json.load(open(DESIGN, encoding="utf-8"))
    op, at = d["operating_point"], d["atmosphere"]
    return {"V0": op["V0_ms"], "omega": op["omega_rads"], "rpm": op["rpm"],
            "rho": at["rho_kgm3"], "p": at["p_Pa"], "T": at["T_K"],
            "a": at["a_ms"], "mach": d["inputs"]["mach_flight"],
            "R_design": op["R_m"]}


def parse_reports(txt: str):
    """Return every force/moment checkpoint found, in transcript order.

    Fluent prints one block per report command. Each block has a header naming
    it a force or a moment, then one row per wall zone. Later blocks are later
    iteration counts, which is exactly what the convergence check needs.
    """
    blocks, cur = [], None
    for line in txt.splitlines():
        low = line.lower()
        if "forces -" in low or "force vector" in low:
            cur = {"kind": "force", "rows": {}}
            blocks.append(cur)
            continue
        if "moments -" in low or "moment vector" in low:
            cur = {"kind": "moment", "rows": {}}
            blocks.append(cur)
            continue
        if cur is None:
            continue
        m = ROW.match(line)
        if m:
            name = m.group(1)
            vals = [float(v) for v in m.group(2).split()]
            low = name.lower()
            if low.startswith(BLADE_PREFIX) or low.startswith(EXCLUDE_PREFIX):
                cur["rows"][name] = vals
    return [b for b in blocks if b["rows"]]


def blade_total(rows, comp=2):
    """Sum the requested component over EVERY blade zone. comp: 0 pres, 1 visc, 2 tot."""
    present = sorted(z for z in rows if z.lower().startswith(BLADE_PREFIX))
    if not present:
        return None, present
    return sum(rows[z][comp] for z in present), present


def omega_from_transcript(txt):
    """The omega the RUN actually used, if the journal set it.

    DEFECT THIS FIXES. omega came only from design_summary.json -- the DESIGN
    speed, 135.559045 rad/s. Runs at other speeds (the +7 % point at 145.0) were
    therefore reported with the wrong omega, and because P_shaft = -Mz*omega and
    eta_p = T*V0/P_shaft, that silently understates the power and OVERSTATES the
    efficiency: 0.2799 instead of the correct 0.2617, an 7 % relative error in
    the headline number, with nothing visibly wrong in the output.

    Forces are unaffected -- they come from the stored pressure field -- which is
    exactly what makes this easy to miss.

    The rotating-zone speed is echoed by the journal's own fluid-zone dialogue,
    so it is recovered here from the transcript rather than assumed.
    """
    best = None
    for m in re.finditer(
            r"[Ss]peed.*?\[[^\]]*\]\s*(-?\d+(?:\.\d+)?)", txt):
        try:
            v = float(m.group(1))
        except ValueError:
            continue
        if 1.0 < abs(v) < 1000.0:
            best = v
    return best


def main():
    if len(sys.argv) < 2:
        raise SystemExit(
            "usage: compute_performance.py <transcript.trn> [--omega <rad/s>]")
    txt = pathlib.Path(sys.argv[1]).read_text(errors="ignore")
    op = load_operating_point()

    # omega precedence: explicit flag > the value the transcript shows the run
    # used > the design value. The last of those is only a fallback and says so.
    omega_src = "design_summary.json (DESIGN speed)"
    if "--omega" in sys.argv:
        op["omega"] = float(sys.argv[sys.argv.index("--omega") + 1])
        omega_src = "--omega on the command line"
    else:
        found = omega_from_transcript(txt)
        if found is not None and abs(abs(found) - abs(op["omega"])) > 1e-6:
            op["omega"] = abs(found)
            omega_src = "the transcript: the run reset the rotating zone"
    print("  omega source: %s  ->  |omega| = %.6f rad/s" % (omega_src, op["omega"]))
    if omega_src.startswith("design_summary"):
        print("  WARNING: no omega found in the transcript. If this run was NOT at the")
        print("           design speed, P_shaft and eta_p below are WRONG. Pass --omega.")

    # FILE SAFETY -- FIXED TWICE, because the first fix was not enough.
    #
    # ROUND 1. This used to write the single fixed name "performance_result.json" on
    # every run, so extracting a second operating point silently destroyed the first --
    # which is what happened to the design-RPM result when the +7 % RPM transcript was
    # processed. The name was then keyed on OMEGA.
    #
    # ROUND 2. Keying on omega alone is still not unique: v03, v04 and v05 are three
    # DIFFERENT GEOMETRIES solved at the SAME design omega, so they all mapped to
    # "performance_result_omega135p559.json". Processing the v05 transcript therefore
    # overwrote the v03 drag-state record -- the same class of loss, one layer down. It
    # was recovered by re-running the v03 transcript, which reproduced T = -845.77679 N
    # and Q = 5367.0989 N.m exactly, but only because the transcript had been preserved.
    #
    # The name now carries the CASE as well, read out of the transcript rather than
    # assumed, so two geometries at one speed cannot collide. The pre-existing v03
    # file keeps its historical name performance_result_omega135p559.json, because
    # EVIDENCE_INDEX.md and PROJECT_STATUS.md cite it; it holds the same numbers.
    m_case = re.findall(r"openfan[\w.-]*?([\w]+)_mrf\.cas\.h5", txt)
    case_tag = (m_case[-1].strip("_") if m_case else "unknowncase")

    # ----------------------------------------------------------------- DEFECT FIX
    # The geometry description used to be the HARD-CODED CONSTANT
    #     "CFD derivative blade, TE 0.020c (design 0.006c)"
    # printed in the banner, printed in the red-team block, and written into the
    # output JSON's "geometry" field. That string is CORRECT for c6/c6n/v04cf/
    # v05n16/v06* and WRONG for every case after them: v08 exists precisely to
    # change the trailing edge to 0.012 c, and v10/v11 inherit v08's edge.
    #
    # The NUMBERS were never affected -- T, Q and eta_p are read from the
    # transcript. But performance_result_v08_omega135p559.json, the artifact for
    # the highest-efficiency design-RPM case, described the ONE VARIABLE v08 was
    # built to test as unchanged from v06e. Read on its own it made the
    # 0.5298 -> 0.5718 gain unattributable.
    #
    # Per the project's evidence-integrity rule an unknown tag must RAISE, never
    # fall back -- a silent default is exactly how this defect survived.
    _GEOMETRY_FOR = {
        "c6":     "v03 PRIME-derived CFD derivative, TE 0.020c (PRIME design 0.006c)",
        "c6n":    "v03 PRIME-derived CFD derivative, TE 0.020c (PRIME design 0.006c)",
        "v04cf":  "v04 CFD derivative, camber side corrected (yc -> -yc), TE 0.020c",
        "v05n16": "v05 CFD derivative, NACA 16-series thickness + a=1.0 mean line, TE 0.020c",
        "v06":    "v06 CFD derivative, low-Cl / thin-root BEM redesign, TE 0.020c",
        "v06c":   "v06 CFD derivative, low-Cl / thin-root BEM redesign, TE 0.020c",
        "v06e":   "v06 CFD derivative, low-Cl / thin-root BEM redesign, TE 0.020c",
        "v08":    "v08 CFD derivative, v06 aerodynamics EXACTLY, CAD TE 0.012c "
                  "(MEASURED meshed TE 0.0188c -- the mesher does not resolve the CAD edge)",
        "v09b":   "v09b CFD derivative, v06 aerodynamics, CAD TE 0.008c -- DIVERGED, NOT A RESULT",
        "v10":    "v10 CFD derivative, v08 geometry with a UNIFORM -1.77 deg de-pitch, "
                  "CAD TE 0.012c -- FALSIFIED (eta_p 0.43856, thrust -50.8 %)",
        "v12":    "v12 CFD derivative, v08 geometry with SWEEP Lambda(r) + 6.00 deg, "
                  "CAD TE 0.012c, DESIGN RPM -- the first case to move M_normal while "
                  "holding M_rel fixed. Directly comparable to v08.",
        "v14":    "v14 = v08 geometry, mesh and RPM EXACTLY, with the HUB WALL "
                  "SHEAR set to zero specified shear. A BOUNDING test of the "
                  "duct-wall hub artefact -- NOT a design, and NOT part of the "
                  "design-RPM ladder.",
        "v15":    "v15 CFD derivative, v08 geometry with a LOCAL ROOT DE-PITCH "
                  "d_beta = -2.40 deg at the root tapering LINEARLY to EXACTLY "
                  "0.00 deg at r/R 0.55 and zero outboard, CAD TE 0.012c, DESIGN "
                  "RPM. Outboard of r/R 0.55 the blade is bit-identical to v08. "
                  "Directly comparable to v08. NOT v10, which de-pitched the "
                  "whole blade uniformly and was falsified.",
        "v11":    "v11 CFD derivative, v08 geometry RE-TWISTED for 1000 rpm "
                  "(+4.07 deg root to +7.35 deg tip), CAD TE 0.012c -- OFF-DESIGN RPM, "
                  "never comparable to the design-RPM ladder without saying so",
    }
    if case_tag not in _GEOMETRY_FOR:
        raise SystemExit(
            "REFUSING to run: case tag %r has no declared geometry description. "
            "Add it to _GEOMETRY_FOR explicitly. Do NOT let it default -- a stale "
            "hard-coded description is the defect this map was added to fix."
            % case_tag)
    GEOMETRY = _GEOMETRY_FOR[case_tag]
    out_path = pathlib.Path(__file__).with_name(
        "performance_result_%s_omega%s.json"
        % (case_tag, ("%.3f" % abs(op["omega"])).replace(".", "p")))

    blocks = parse_reports(txt)

    print("=" * 74)
    print("BA-OF-01  PERFORMANCE EXTRACTION")
    print("  geometry: %s" % GEOMETRY)
    print("=" * 74)
    print(f"  altitude 10668 m   T {op['T']:.3f} K   p {op['p']:.3f} Pa   "
          f"rho {op['rho']:.6f} kg/m3")
    print(f"  M {op['mach']}   V0 {op['V0']:.5f} m/s   omega {op['omega']:.9f} rad/s "
          f"({op['rpm']:.4f} rpm)")
    print(f"  sector scaling = {SECTOR_SCALING} (360 deg domain, all {N_BLADES} blades)")
    print(f"  thrust/torque zones = any starting {BLADE_PREFIX!r};  "
          f"excluded = any starting {EXCLUDE_PREFIX}")

    forces = [b for b in blocks if b["kind"] == "force"]
    moments = [b for b in blocks if b["kind"] == "moment"]
    if not forces or not moments:
        print("\n  NO force/moment rows found in that transcript.")
        print("  The solve has not reached the report stage, or it did not converge.")
        print("  NOT computing eta_p from an absent or unconverged field.")
        return 1

    # ---- convergence: thrust and torque must PLATEAU across checkpoints -------
    hist, split = [], []
    for fb, mb in zip(forces, moments):
        T, zf = blade_total(fb["rows"])
        Q, zm = blade_total(mb["rows"])
        # pressure (col 0) and viscous (col 1) kept separately -- the red-team
        # check below needs them apart, not just their sum.
        Tp, _ = blade_total(fb["rows"], 0)
        Tv, _ = blade_total(fb["rows"], 1)
        Qp, _ = blade_total(mb["rows"], 0)
        Qv, _ = blade_total(mb["rows"], 1)
        split.append((Tp, Tv, Qp, Qv))
        if T is None or Q is None:
            continue
        hist.append((T * SECTOR_SCALING, Q * SECTOR_SCALING, zf, zm))

    if not hist:
        print("\n  force/moment blocks found but no BLADE zone rows in them.")
        print(f"  expected a zone whose name starts with {BLADE_PREFIX!r}; "
              f"aborting rather than guessing.")
        return 1

    print(f"\n  {len(hist)} checkpoint(s), blade zones present: {hist[-1][2]}")
    print(f"  {'#':>3} {'T [N]':>14} {'Q [N.m]':>14} {'dT %':>9} {'dQ %':>9}")
    for i, (T, Q, _, _) in enumerate(hist):
        if i:
            dT = 100.0 * (T - hist[i - 1][0]) / abs(hist[i - 1][0]) if hist[i - 1][0] else float("nan")
            dQ = 100.0 * (Q - hist[i - 1][1]) / abs(hist[i - 1][1]) if hist[i - 1][1] else float("nan")
            print(f"  {i:>3} {T:>14.3f} {Q:>14.3f} {dT:>9.3f} {dQ:>9.3f}")
        else:
            print(f"  {i:>3} {T:>14.3f} {Q:>14.3f} {'-':>9} {'-':>9}")

    # ---- CONVERGENCE -------------------------------------------------------
    # DEFECT THIS FIXES. The old test compared only the LAST TWO checkpoints. On
    # the +7 % RPM run the sequence was
    #     2014.0 -> 2410.0 -> 1712.2 -> 2519.5 -> 2507.7 N
    # i.e. swings of +19.7 %, -29.0 %, +47.2 %, then -0.5 %. The last pair agree
    # to 0.47 %, so the old rule printed "SETTLED (<1%)" for what is plainly a
    # large undamped oscillation. Two adjacent samples of an oscillation landing
    # close together is coincidence, not convergence -- and it flatters the
    # result, which is the dangerous direction.
    #
    # The V&V plan asks for T and Q "flat over the final 500+ iterations", so the
    # test now looks at the whole recorded history: the full peak-to-peak spread
    # of the last N checkpoints must itself be inside the bound.
    settled = None
    spread_T = spread_Q = None
    if len(hist) >= 2:
        dT = abs(hist[-1][0] - hist[-2][0]) / max(abs(hist[-2][0]), 1e-12)
        dQ = abs(hist[-1][1] - hist[-2][1]) / max(abs(hist[-2][1]), 1e-12)
        print(f"\n  last-two-checkpoint drift: T {dT*100:.3f}%  Q {dQ*100:.3f}%")

        win = hist[-5:] if len(hist) >= 5 else hist
        Ts = [h[0] for h in win]
        Qs = [h[1] for h in win]
        mT = sum(Ts) / len(Ts)
        mQ = sum(Qs) / len(Qs)
        spread_T = (max(Ts) - min(Ts)) / max(abs(mT), 1e-12)
        spread_Q = (max(Qs) - min(Qs)) / max(abs(mQ), 1e-12)
        settled = bool(spread_T < 0.01 and spread_Q < 0.01 and len(win) >= 3)
        print(f"  peak-to-peak over the last {len(win)} checkpoints: "
              f"T {spread_T*100:.1f}%  Q {spread_Q*100:.1f}%")
        print(f"  -> {'SETTLED (<1% across the whole window)' if settled else 'NOT SETTLED'}")
        if not settled and dT < 0.01:
            print("     NOTE: the last two checkpoints agree to <1% but the window "
                  "does not.\n     That is an oscillation sampled twice near a "
                  "crossing, not convergence.")
        if len(win) >= 3:
            print(f"  mean over the window: T {mT:.1f} N, Q {mQ:.1f} N.m "
                  f"(quote a RANGE, not the last value, when NOT SETTLED)")

    # ---- SIGNS -------------------------------------------------------------
    # Fz and Mz below are what the FLUID exerts on the blade, about +Z.
    #
    # Freestream runs in +Z (inlet at z = -7 m, far-field direction (0,0,1)), so
    # the aircraft flies toward -Z and USEFUL THRUST IS -Z:
    #       T_useful = -Fz
    # The shaft must react the fluid's moment to hold omega, so the power it
    # delivers is
    #       P_shaft  = -Mz * omega_z
    # Both reduce to the textbook forms for a normal propeller.
    #
    # CORRECTED 2026-09-15 -- an earlier version of this comment claimed that the
    # reverse-rotation run produced eta_p = -0.833 and was "flagged". That claim
    # was FALSE, and the check built on it was unsound. Running this script over
    # the reverse-rotation transcript (fluent-20260915-051909-20492.trn) gives
    #       Fz = +49673.373 N     ->  T_useful = -49673 N      (drag, not thrust)
    #       Mz = -97844.678 N.m   ->  P_shaft  = -13.26 MW     (DELIVERING power)
    #       eta_p = T*V0/P = (-)/(-) = +0.8329
    # A windmill-brake state therefore produces a perfectly healthy-looking 83 %
    # efficiency, and a test on the sign of eta_p alone does NOT catch it,
    # because a negative divided by a negative is positive.
    #
    # The sound test is on T and P_shaft SEPARATELY:
    #       T       > 0  -- the rotor must push the aircraft forward
    #       P_shaft > 0  -- the rotor must ABSORB shaft power, not deliver it
    # Only if both hold is eta_p a propulsive efficiency at all. These are
    # enforced below and the result is withheld if either fails.
    OMEGA_Z = -abs(op["omega"])       # rotation is -Z; see make_setup_journal.py
    Fz, Mz = hist[-1][0], hist[-1][1]
    T = -Fz                            # useful thrust, +ve = forward (-Z)
    P = -Mz * OMEGA_Z                  # shaft power, +ve = absorbed by the rotor
    Q = P / abs(OMEGA_Z)               # shaft torque magnitude
    eta = (T * op["V0"] / P) if P else float("nan")

    print(f"\n  Fz on blade (fluid->wall)  = {Fz:12.3f} N")
    print(f"  Mz on blade (fluid->wall)  = {Mz:12.3f} N.m")
    print(f"  omega_z                    = {OMEGA_Z:12.6f} rad/s")
    print(f"\n  thrust  T  = -Fz          = {T:12.3f} N")
    print(f"  P_shaft    = -Mz*omega_z  = {P:12.3f} W  = {P/1e6:.4f} MW")
    print(f"  torque  Q  = P/|omega|    = {Q:12.3f} N.m")
    # ---- physical-state gate: BOTH must hold before eta_p means anything ----
    thrust_ok = T > 0.0
    power_ok = P > 0.0
    state_ok = thrust_ok and power_ok
    if not state_ok:
        if not thrust_ok and not power_ok:
            state = ("WINDMILL-BRAKE: the rotor is producing DRAG and DELIVERING "
                     "power. eta_p is a ratio of two negatives and is positive "
                     "but meaningless.")
        elif not thrust_ok:
            state = "DRAG STATE: axial force opposes flight."
        else:
            state = "TURBINE STATE: the rotor is extracting power from the flow."
        print(f"  eta_p      = T*V0/P_shaft = {eta:.4f}   <-- NOT A VALID EFFICIENCY")
        print(f"\n  ***** PHYSICAL-STATE GATE FAILED *****")
        print(f"  {state}")
        print(f"    thrust  T > 0 ?    {thrust_ok}   (T = {T:.3f} N)")
        print(f"    power   P > 0 ?    {power_ok}   (P = {P/1e6:.4f} MW)")
        print("  This is NOT a propulsive operating point. The number above is")
        print("  reported for diagnosis only and MUST NOT be used as a result.")
    else:
        print(f"  eta_p      = T*V0/P_shaft = {eta:.4f}")
        print(f"  target     = {ETA_TARGET:.2f}      difference = {eta-ETA_TARGET:+.4f}")

    # ---- pressure / viscous decomposition (protocol section 10) -------------
    # A propeller blade's axial force and torque must both be PRESSURE dominated.
    # If viscous stress carried most of the torque, the wall treatment would be
    # driving the answer rather than the blade loading, and the result would not
    # be defensible on a mesh with no prism layers and y+ ~ 610-765.
    Tp, Tv, Qp, Qv = split[-1]
    pres_frac_T = abs(Tp) / max(abs(Tp) + abs(Tv), 1e-30)
    pres_frac_Q = abs(Qp) / max(abs(Qp) + abs(Qv), 1e-30)
    print("\n  PRESSURE / VISCOUS DECOMPOSITION (blade zones, last checkpoint):")
    print(f"    axial force   pressure {Tp:14.3f} N    viscous {Tv:12.3f} N"
          f"    pressure share {100*pres_frac_T:6.2f} %")
    print(f"    axial moment  pressure {Qp:14.3f} N.m  viscous {Qv:12.3f} N.m"
          f"  pressure share {100*pres_frac_Q:6.2f} %")

    print("\n  RED-TEAM:")
    print(f"    torque pressure-dominated?      "
          f"{'yes' if pres_frac_Q > 0.7 else 'NO - wall treatment is driving it'}"
          f"  ({100*pres_frac_Q:.1f} %)")
    print(f"    omega in rad/s not rpm?         {op['omega']:.4f} rad/s "
          f"(rpm would be {op['rpm']:.1f} -> {abs(op['rpm']/op['omega']):.3f}x error)")
    print(f"    scaling applied exactly once?   factor {SECTOR_SCALING}, 360 deg domain")
    print(f"    all blade zones summed?         {hist[-1][2]}")
    print("    hub excluded from thrust?       yes - 17.5 m duct wall, not a spinner")
    print(f"    thrust T > 0 (pushes forward)?  "
          f"{'yes' if thrust_ok else 'NO - DRAG, not thrust'}  ({T:.1f} N)")
    print(f"    P_shaft > 0 (absorbs power)?    "
          f"{'yes' if power_ok else 'NO - rotor is DELIVERING power'}  ({P/1e6:.4f} MW)")
    print(f"    eta_p > 1 (unphysical)?         {'YES - REJECT' if eta > 1 else 'no'}")
    print(f"    eta_p < 0 (wrong sign)?         {'YES - check signs' if eta < 0 else 'no'}")
    print("    NOTE: eta_p > 0 is NOT sufficient -- a windmill-brake state gives")
    print("          (-)/(-) = positive. T and P are therefore checked separately.")
    print(f"    T and Q settled to <1%?         {settled}")
    # The 0.8072 this line used to hard-code is the v03 design's BEM efficiency.
    # Every v06-family case -- v06*, v08*, v09*, v10, v11, v12, v14, v15 -- was
    # therefore scored against the WRONG design intent, overstating the gap by
    # 0.0121 each time. Same defect class as DEFECT_bem_reference_was_v03.json,
    # which was fixed in the sectional tools and missed here. Print-only: no
    # stored JSON number ever carried it.
    _bem = bem_reference.resolve(case_tag)
    if _bem["eta"] is None:
        print("    vs BEM estimate                 n/a (%s family has no declared "
              "BEM eta)" % _bem["family"])
    else:
        print(f"    vs BEM estimate {_bem['eta']:.4f}          "
              f"{eta-_bem['eta']:+.4f}   ({_bem['family']} family)")
    print("    %s" % bem_reference.note(case_tag))
    print("    geometry = %s" % GEOMETRY)
    print("               (a CFD DERIVATIVE -- never PRIME's own performance)")

    json.dump({"T_N": T, "Q_Nm": Q, "P_shaft_W": P,
               "eta_p": eta if state_ok else None,
               "eta_p_raw_if_invalid": None if state_ok else eta,
               "physical_state_valid": state_ok,
               "thrust_positive": thrust_ok, "shaft_power_positive": power_ok,
               "eta_target": ETA_TARGET, "difference": eta - ETA_TARGET,
               "checkpoints": [{"T_N": h[0], "Q_Nm": h[1]} for h in hist],
               "settled_within_1pct": settled,
               "peak_to_peak_T_frac": spread_T, "peak_to_peak_Q_frac": spread_Q,
               "blade_zones_summed": hist[-1][2],
               "excluded_prefixes": list(EXCLUDE_PREFIX),
               "pressure_viscous": {"Fz_pressure_N": Tp, "Fz_viscous_N": Tv,
                                    "Mz_pressure_Nm": Qp, "Mz_viscous_Nm": Qv,
                                    "pressure_share_force": pres_frac_T,
                                    "pressure_share_moment": pres_frac_Q},
               "span_caveat": ("CFD wets r 0.5650-1.7254 m vs design 0.4900-1.7500 m; "
                               "2.97% of design thrust AND 2.97% of design torque are "
                               "outside the wetted span, so T and Q are each biased low "
                               "by ~3% while eta_p is first-order unaffected "
                               "(see span_accounting.py)"),
               "operating_point": op, "sector_scaling": SECTOR_SCALING,
               "source_transcript": pathlib.Path(sys.argv[1]).name,
               "geometry": GEOMETRY,
               "geometry_case_tag": case_tag},
              open(out_path, "w"), indent=1)
    print(f"  wrote {out_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
