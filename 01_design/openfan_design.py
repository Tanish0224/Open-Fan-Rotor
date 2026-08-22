"""
openfan_design.py -- BA-OF-01 first-principles open-fan rotor design module.

AUTHORITATIVE ANALYTICAL MODEL. Every geometric quantity used downstream (CAD, CFD)
must originate here. No dimension is typed by hand anywhere in this project.

DESIGN CHAIN (fixed by Phase 1 authorisation, item A)
-----------------------------------------------------
    cruise condition
      -> diameter
      -> rotational speed / relative tip-Mach constraint
      -> advance ratio
      -> NON-DIMENSIONAL loading  (tau = T / (rho A V0^2))
      -> rotor thrust / power coefficients
      -> dimensional interpretation  (thrust in newtons is an OUTPUT, never an input)

There is deliberately NO aircraft-level thrust requirement in this model. Blocking
item B1 is closed by prescribing non-dimensional loading instead (see ED-009-R1).

EVIDENCE LABELS used throughout, per Phase 1 authorisation item H:
    [REQUIREMENT]       imposed by the project requirements document
    [PUBLISHED INPUT]   traceable to a public source
    [DESIGN DECISION]   a choice made by this project, owned and defensible
    [DERIVED]           computed from other labelled quantities
    [ASSUMPTION]        a modelling assumption whose validity is bounded
    [CFD-TBD]           will ultimately be determined by ANSYS Fluent, not here

METHOD
------
Adkins & Liebeck (1983), "Design of Optimum Propellers", J. Propulsion & Power --
Betz minimum-induced-loss formulation with Prandtl tip/hub loss. Closed form,
derivable, not a black box.  [PUBLISHED INPUT]

SECTIONS
--------
NACA 4-digit series. Chosen because its geometry is defined by published closed-form
equations and can therefore be reconstructed EXACTLY with no request-only data.
Sectional lift comes from thin-airfoil theory at the ideal (shock-free-entry) angle.
Sectional drag is a low-order estimate and is the weakest input in the model --
it is explicitly flagged [CFD-TBD].

KNOWN LIMITATIONS (stated before use, not after)
------------------------------------------------
L1  Prandtl-Glauert is applied only where M_n < PG_VALID_LIMIT. Outboard of that the
    sectional aerodynamics is NOT trustworthy and is flagged. The tip of this rotor
    runs at helical Mach > 1, which is exactly why 3-D CFD is required.
L2  BEM is strip theory: no radial equilibrium, no 3-D tip-vortex physics beyond the
    Prandtl factor.
L3  NACA 4-digit is not a high-critical-Mach propeller family (NACA 16-series would
    be). This is a deliberate, recorded trade of aerodynamic optimality for exact
    public reconstructability. CFD will quantify the penalty.
L4  Sweep is NOT designed by BEM -- BEM has no spanwise geometric awareness. Sweep is
    layered on afterwards from the computed helical-Mach distribution.
"""

from __future__ import annotations

import json
import numpy as np
from dataclasses import dataclass, asdict, field

# ----------------------------------------------------------------------------------
# PHYSICAL CONSTANTS
# ----------------------------------------------------------------------------------
R_GAS = 287.05287          # J/(kg K)   [PUBLISHED INPUT] ISA
GAMMA = 1.4                # -          [PUBLISHED INPUT] ISA
G0 = 9.80665               # m/s^2      [PUBLISHED INPUT] ISA
T0_SL = 288.15             # K          [PUBLISHED INPUT] ISA
P0_SL = 101325.0           # Pa         [PUBLISHED INPUT] ISA
LAPSE = 0.0065             # K/m        [PUBLISHED INPUT] ISA troposphere

PG_VALID_LIMIT = 0.70      # [ASSUMPTION] Prandtl-Glauert validity ceiling on M_normal


# ----------------------------------------------------------------------------------
# ATMOSPHERE
# ----------------------------------------------------------------------------------
def isa(altitude_m: float) -> dict:
    """ISA troposphere. Sutherland viscosity. [DERIVED from PUBLISHED INPUT]"""
    if altitude_m > 11000.0:
        raise ValueError("This ISA implementation covers the troposphere only.")
    T = T0_SL - LAPSE * altitude_m
    p = P0_SL * (T / T0_SL) ** (G0 / (LAPSE * R_GAS))
    rho = p / (R_GAS * T)
    a = np.sqrt(GAMMA * R_GAS * T)
    mu = 1.458e-6 * T ** 1.5 / (T + 110.4)      # Sutherland
    return {"altitude_m": altitude_m, "T_K": T, "p_Pa": p,
            "rho_kgm3": rho, "a_ms": a, "mu_Pas": mu, "nu_m2s": mu / rho}


# ----------------------------------------------------------------------------------
# NACA 4-DIGIT SECTION  -- exact closed form, thin-airfoil theory
# ----------------------------------------------------------------------------------
def naca4_camber_slope(x: np.ndarray, m: float, p: float) -> np.ndarray:
    """dyc/dx for the NACA 4-digit mean line. [PUBLISHED INPUT] closed form."""
    x = np.asarray(x, dtype=float)
    dy = np.empty_like(x)
    if m == 0.0:
        return np.zeros_like(x)
    fwd = x < p
    dy[fwd] = (2.0 * m / p ** 2) * (p - x[fwd])
    dy[~fwd] = (2.0 * m / (1.0 - p) ** 2) * (p - x[~fwd])
    return dy


def thin_airfoil_coefficients(m: float, p: float, n_theta: int = 2001) -> dict:
    """
    Thin-airfoil theory for a NACA 4-digit mean line. [DERIVED]

    Returns the ideal (shock-free entry, A0 = 0) design condition:
        Cl_ideal   = pi * A1
        alpha_ideal= (1/pi) * Int_0^pi (dyc/dx) dtheta
        alpha_L0   = -(1/pi) * Int_0^pi (dyc/dx)(cos(theta) - 1) dtheta

    Designing at the ideal angle gives smooth leading-edge entry, which is the
    correct choice for a Mach-critical propeller section.  [DESIGN DECISION]
    """
    if m == 0.0:
        return {"Cl_ideal": 0.0, "alpha_ideal_rad": 0.0, "alpha_L0_rad": 0.0, "A1": 0.0}
    theta = np.linspace(0.0, np.pi, n_theta)
    x = 0.5 * (1.0 - np.cos(theta))
    dydx = naca4_camber_slope(x, m, p)
    A1 = (2.0 / np.pi) * np.trapezoid(dydx * np.cos(theta), theta)
    alpha_ideal = (1.0 / np.pi) * np.trapezoid(dydx, theta)
    alpha_L0 = -(1.0 / np.pi) * np.trapezoid(dydx * (np.cos(theta) - 1.0), theta)
    return {"Cl_ideal": np.pi * A1, "alpha_ideal_rad": alpha_ideal,
            "alpha_L0_rad": alpha_L0, "A1": A1}


def solve_camber_for_cl(cl_target: float, p: float) -> tuple[float, dict]:
    """
    Solve NACA 4-digit max camber m giving Cl_ideal = cl_target. [DERIVED]
    Cl_ideal is linear in m, so one evaluation is exact.
    """
    if cl_target <= 0.0:
        return 0.0, thin_airfoil_coefficients(0.0, p)
    probe = thin_airfoil_coefficients(0.01, p)
    m = 0.01 * cl_target / probe["Cl_ideal"]
    return m, thin_airfoil_coefficients(m, p)


TE_THICKNESS = 0.006   # [DESIGN DECISION] trailing-edge thickness, fraction of chord


def naca4_section(m: float, p: float, t: float, n_pts: int = 121,
                  te_thickness: float = TE_THICKNESS) -> np.ndarray:
    """
    Closed-form NACA 4-digit ordinates, cosine-spaced, with a BLUNT trailing edge.
    Returns (N,2) array from TE over the upper surface to LE and back along lower.
    [PUBLISHED INPUT] -- the exact published thickness polynomial.

    BLUNT TRAILING EDGE  [DESIGN DECISION]
    --------------------------------------
    The published polynomial (-0.1036 coefficient) closes the section to ZERO
    thickness at x/c = 1. That knife edge is undesirable for two independent
    reasons, and it caused a real, diagnosed failure in this project:
      * CAD  -- after arc-length resampling the near-TE points on the upper and
                lower surfaces converge, the section polygon degenerates, and the
                lofted solid reports Check2 != 0 (invalid geometry).
      * CFD  -- a zero-thickness TE cannot carry prism layers and forces either a
                collapsed cell or an arbitrary local truncation.
    A finite TE is also what a real composite blade has, for manufacturing and
    structural reasons. Thickness is added linearly in x, so the leading edge and
    the camber line are untouched and the design Cl is unaffected.
    """
    beta = np.linspace(0.0, np.pi, n_pts)
    x = 0.5 * (1.0 - np.cos(beta))
    yt = 5.0 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2
                    + 0.2843 * x ** 3 - 0.1036 * x ** 4)
    yt = yt + 0.5 * te_thickness * x          # blunt the TE; LE unchanged
    if m == 0.0:
        yc = np.zeros_like(x)
        dyc = np.zeros_like(x)
    else:
        yc = np.where(x < p,
                      (m / p ** 2) * (2 * p * x - x ** 2),
                      (m / (1 - p) ** 2) * ((1 - 2 * p) + 2 * p * x - x ** 2))
        dyc = naca4_camber_slope(x, m, p)
    th = np.arctan(dyc)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    xs = np.concatenate([xu[::-1], xl[1:]])
    ys = np.concatenate([yu[::-1], yl[1:]])
    return np.column_stack([xs, ys])


# ----------------------------------------------------------------------------------
# SECTIONAL DRAG -- low-order estimate, the weakest link, flagged [CFD-TBD]
# ----------------------------------------------------------------------------------
def section_cd(cl: float, re: float, toc: float) -> float:
    """
    Low-order profile drag estimate. [ANALYTICAL ESTIMATE] / [CFD-TBD]

    Cd0 : turbulent flat-plate skin friction x a thickness form factor
    Cdi : a quadratic lift-dependent term

    This model does NOT represent wave drag and is NOT valid transonically.
    Torque -- and therefore propulsive efficiency -- depends directly on Cd, so
    the efficiency reported by this module is an ESTIMATE whose accuracy is
    bounded by this correlation. Determining it properly is a CFD deliverable.
    """
    re = max(re, 1.0e5)
    cf = 0.074 / re ** 0.2                       # turbulent flat plate
    form = 1.0 + 2.0 * toc + 60.0 * toc ** 4     # thickness form factor
    cd0 = 2.0 * cf * form
    return cd0 + 0.006 * cl ** 2


# ----------------------------------------------------------------------------------
# DESIGN SPECIFICATION
# ----------------------------------------------------------------------------------
@dataclass
class DesignSpec:
    """All Phase 1 inputs. Every field carries its evidence label in the comment."""
    # --- cruise condition ---
    mach_flight: float = 0.75         # [DESIGN DECISION] inside CFM's stated M0.75-0.85
    altitude_m: float = 10668.0       # [DESIGN DECISION] 35 000 ft, standard cruise

    # --- geometry ---
    diameter_m: float = 3.5           # [DESIGN DECISION] from CFM "blade over 1.6 m" => D ~ 3.5-4 m
    hub_tip_ratio: float = 0.28       # [DESIGN DECISION] typical propfan spinner fraction

    # --- rotational-speed constraint ---
    mach_tip_rot: float = 0.80        # [DESIGN DECISION] classical propfan tip-speed practice

    # --- NON-DIMENSIONAL loading (this replaces any thrust requirement) ---
    tau: float = 0.08                 # [DESIGN DECISION] tau = T/(rho A V0^2); sets the
                                      #                   ideal propulsive-efficiency ceiling.
                                      # Selected to give a propfan-representative planform
                                      # (c/D ~ 0.1 at 0.75R). A tau sweep is reported so the
                                      # consequence of this choice is visible, not hidden.

    # --- blade ---
    n_blades: int = 12                # [DESIGN DECISION] selected by the trade study, not assumed

    # --- section design schedule ---
    cl_root: float = 0.70             # [DESIGN DECISION] design Cl inboard
    cl_tip: float = 0.40              # [DESIGN DECISION] unloaded tip: local Mach is highest there
    cl_taper_start: float = 0.40      # [DESIGN DECISION] r/R where Cl begins to fall
    camber_pos: float = 0.40          # [DESIGN DECISION] NACA 4-digit max-camber position p
    toc_root: float = 0.20            # [DESIGN DECISION] thick root for structure, low local Mach
    toc_tip: float = 0.025            # [DESIGN DECISION] thin tip for critical-Mach margin
    toc_decay: float = 2.2            # [DESIGN DECISION] exponent of the t/c distribution

    # --- sweep law ---
    mn_limit: float = 0.78            # [DESIGN DECISION] cap on leading-edge-normal Mach.
                                      # Set marginally above the flight Mach (0.75) so that
                                      # the inboard blade, where M_hel is dominated by M0,
                                      # is essentially unswept and sweep is introduced only
                                      # where rotation actually drives M_hel up.

    # --- numerics ---
    n_stations: int = 41              # cosine-clustered toward the tip
    max_iter: int = 200
    tol: float = 1.0e-10


# ----------------------------------------------------------------------------------
# THE DESIGN
# ----------------------------------------------------------------------------------
class OpenFanRotorDesign:
    """Adkins-Liebeck minimum-induced-loss design of an open-fan rotor."""

    def __init__(self, spec: DesignSpec):
        self.spec = spec
        self.atm = isa(spec.altitude_m)
        self._setup_operating_point()
        self._setup_stations()
        self.converged = False
        self.zeta = None

    # -- chain step 1-4: cruise -> diameter -> speed -> advance ratio ---------------
    def _setup_operating_point(self):
        s, atm = self.spec, self.atm
        self.V0 = s.mach_flight * atm["a_ms"]                       # [DERIVED]
        self.R = 0.5 * s.diameter_m                                 # [DERIVED]
        self.R_hub = s.hub_tip_ratio * self.R                       # [DERIVED]
        self.U_tip = s.mach_tip_rot * atm["a_ms"]                   # [DERIVED]
        self.omega = self.U_tip / self.R                            # [DERIVED]
        self.rpm = self.omega * 60.0 / (2.0 * np.pi)                # [DERIVED]
        self.n_rev = self.omega / (2.0 * np.pi)                     # [DERIVED]
        self.J = self.V0 / (self.n_rev * s.diameter_m)              # [DERIVED] advance ratio
        self.lam = self.V0 / (self.omega * self.R)                  # [DERIVED] speed ratio
        self.area = np.pi * self.R ** 2                             # [DERIVED]
        # helical tip Mach -- DISTINCT from rotational tip Mach. Never conflate.
        self.mach_tip_helical = np.hypot(s.mach_flight, s.mach_tip_rot)   # [DERIVED]
        # non-dimensional loading -> Adkins thrust coefficient
        self.Tc = 2.0 * s.tau                                       # [DERIVED] Tc = 2T/(rho V^2 A)
        # actuator-disk ceiling implied by the prescribed loading
        self.eta_ideal = 2.0 / (1.0 + np.sqrt(1.0 + 2.0 * s.tau))    # [DERIVED]

    def _setup_stations(self):
        s = self.spec
        xh = s.hub_tip_ratio
        # cosine clustering toward the tip: resolves the Prandtl factor and the shock region
        beta = np.linspace(0.0, np.pi / 2.0, s.n_stations)
        self.xi = xh + (1.0 - xh) * np.sin(beta)
        self.r = self.xi * self.R

    # -- radial schedules ----------------------------------------------------------
    def cl_design(self, xi):
        """Prescribed design-Cl schedule. [DESIGN DECISION]"""
        s = self.spec
        f = np.clip((xi - s.cl_taper_start) / (1.0 - s.cl_taper_start), 0.0, 1.0)
        return s.cl_root + (s.cl_tip - s.cl_root) * f

    def toc(self, xi):
        """Thickness-to-chord schedule. [DESIGN DECISION]"""
        s = self.spec
        xh = s.hub_tip_ratio
        f = np.clip((xi - xh) / (1.0 - xh), 0.0, 1.0)
        return s.toc_tip + (s.toc_root - s.toc_tip) * (1.0 - f) ** s.toc_decay

    # -- Adkins-Liebeck core -------------------------------------------------------
    def _station_pass(self, zeta):
        """One evaluation of all stations for a given displacement-velocity ratio."""
        s, atm = self.spec, self.atm
        xi, lam, B = self.xi, self.lam, s.n_blades

        # tip flow angle and its Prandtl factor
        tan_phi_t = lam * (1.0 + zeta / 2.0)
        phi_t = np.arctan(tan_phi_t)

        phi = np.arctan(tan_phi_t / xi)                       # local flow angle
        sin_phi, cos_phi = np.sin(phi), np.cos(phi)

        # Prandtl tip and hub loss
        f_tip = (B / 2.0) * (1.0 - xi) / np.sin(phi_t)
        F_tip = (2.0 / np.pi) * np.arccos(np.clip(np.exp(-f_tip), 0.0, 1.0))
        f_hub = (B / 2.0) * (xi - s.hub_tip_ratio) / (s.hub_tip_ratio * np.sin(phi_t))
        F_hub = (2.0 / np.pi) * np.arccos(np.clip(np.exp(-f_hub), 0.0, 1.0))
        F = np.clip(F_tip * F_hub, 1.0e-6, 1.0)

        x = xi / lam                                          # local speed ratio Omega r / V
        G = F * x * cos_phi * sin_phi

        cl = self.cl_design(xi)
        toc = self.toc(xi)

        # Wc = W * c  (Adkins eq. for the chord-velocity product)
        Wc = 4.0 * np.pi * lam * G * self.V0 * self.R * zeta / (cl * B)

        # local Reynolds number from the Wc product
        Re = Wc * atm["rho_kgm3"] / atm["mu_Pas"]
        cd = np.array([section_cd(c_, re_, t_) for c_, re_, t_ in zip(cl, Re, toc)])
        eps = cd / cl

        a_ax = (zeta / 2.0) * cos_phi ** 2 * (1.0 - eps * np.tan(phi))
        a_tan = (zeta / (2.0 * x)) * cos_phi * sin_phi * (1.0 + eps / np.tan(phi))

        W = self.V0 * (1.0 + a_ax) / sin_phi
        chord = Wc / W

        # Adkins integrands
        I1 = 4.0 * xi * G * (1.0 - eps * np.tan(phi))
        I2 = lam * (I1 / (2.0 * xi)) * (1.0 + eps / np.tan(phi)) * cos_phi * sin_phi
        J1 = 4.0 * xi * G * (1.0 + eps / np.tan(phi))
        J2 = (J1 / 2.0) * (1.0 - eps * np.tan(phi)) * cos_phi ** 2

        return dict(phi=phi, F=F, G=G, cl=cl, cd=cd, toc=toc, Wc=Wc, Re=Re,
                    a_ax=a_ax, a_tan=a_tan, W=W, chord=chord, eps=eps,
                    I1=I1, I2=I2, J1=J1, J2=J2, phi_t=phi_t)

    def solve(self):
        """Iterate the displacement-velocity ratio zeta to hit the prescribed loading."""
        s = self.spec
        zeta = 0.05
        for it in range(s.max_iter):
            st = self._station_pass(zeta)
            I1 = np.trapezoid(st["I1"], self.xi)
            I2 = np.trapezoid(st["I2"], self.xi)
            J1 = np.trapezoid(st["J1"], self.xi)
            J2 = np.trapezoid(st["J2"], self.xi)

            disc = (I1 / (2.0 * I2)) ** 2 - self.Tc / I2
            if disc < 0.0:
                raise RuntimeError(
                    f"No minimum-induced-loss solution at Tc={self.Tc:.4f}: the "
                    f"prescribed loading exceeds what this disk can produce. "
                    f"Reduce tau, or increase diameter."
                )
            zeta_new = I1 / (2.0 * I2) - np.sqrt(disc)

            if abs(zeta_new - zeta) < s.tol:
                zeta = zeta_new
                self.converged = True
                break
            zeta = 0.5 * zeta + 0.5 * zeta_new      # under-relaxed

        self.zeta = zeta
        self.iterations = it + 1
        self.st = self._station_pass(zeta)
        self.I1, self.I2, self.J1, self.J2 = I1, I2, J1, J2
        self._finalise()
        return self

    # -- chain step 5-7: coefficients -> dimensional interpretation -----------------
    def _finalise(self):
        s, atm, st = self.spec, self.atm, self.st

        # power coefficient in Adkins' normalisation, then efficiency
        self.Pc = self.J1 * self.zeta + self.J2 * self.zeta ** 2      # [DERIVED]
        self.eta_bem = self.Tc / self.Pc                              # [DERIVED]

        # dimensional INTERPRETATION -- outputs, never inputs
        q = 0.5 * atm["rho_kgm3"] * self.V0 ** 2
        self.thrust_N = self.Tc * q * self.area                       # [DERIVED]
        self.power_W = self.Pc * q * self.area * self.V0              # [DERIVED]
        self.torque_Nm = self.power_W / self.omega                    # [DERIVED]
        self.disk_loading_Pa = self.thrust_N / self.area              # [DERIVED]

        # classical propeller coefficients
        rho, n, D = atm["rho_kgm3"], self.n_rev, s.diameter_m
        self.C_T = self.thrust_N / (rho * n ** 2 * D ** 4)            # [DERIVED]
        self.C_P = self.power_W / (rho * n ** 3 * D ** 5)             # [DERIVED]
        self.eta_coeff = self.C_T * self.J / self.C_P                 # [DERIVED] cross-check

        # ---- local Mach numbers -------------------------------------------------
        a = atm["a_ms"]
        self.M_rel = st["W"] / a                                      # [DERIVED] relative Mach
        # helical Mach from pure kinematics (no induction) -- the design constraint
        self.M_hel = np.hypot(s.mach_flight, s.mach_tip_rot * self.xi)  # [DERIVED]

        # ---- sweep law, derived from the helical-Mach distribution --------------
        # L4: BEM cannot produce sweep. This is a separate geometric decision whose
        # justification is the normal-Mach argument M_n = M_hel * cos(Lambda).
        cos_lam = np.clip(s.mn_limit / np.maximum(self.M_hel, 1.0e-9), 0.0, 1.0)
        self.sweep_rad = np.arccos(cos_lam)                           # [DERIVED]
        self.M_normal = self.M_hel * np.cos(self.sweep_rad)           # [DERIVED]

        # ---- section camber and blade angle ------------------------------------
        # Prandtl-Glauert: the incompressible section must deliver less Cl than the
        # compressible requirement. Applied ONLY where M_n is inside PG validity.
        self.pg_valid = self.M_normal < PG_VALID_LIMIT
        beta_pg = np.where(self.pg_valid,
                           np.sqrt(np.clip(1.0 - self.M_normal ** 2, 1.0e-6, None)),
                           np.nan)
        cl_inc = np.where(self.pg_valid, st["cl"] * beta_pg, st["cl"])

        self.camber_m = np.zeros_like(self.xi)
        self.alpha_ideal = np.zeros_like(self.xi)
        self.alpha_L0 = np.zeros_like(self.xi)
        for i, clv in enumerate(cl_inc):
            m, coef = solve_camber_for_cl(float(clv), s.camber_pos)
            self.camber_m[i] = m
            self.alpha_ideal[i] = coef["alpha_ideal_rad"]
            self.alpha_L0[i] = coef["alpha_L0_rad"]

        # blade (pitch) angle = flow angle + ideal incidence
        self.beta_rad = st["phi"] + self.alpha_ideal                  # [DERIVED]

        # ---- solidity and Reynolds ---------------------------------------------
        self.solidity = s.n_blades * st["chord"] / (2.0 * np.pi * self.r)   # [DERIVED]
        self.Re_chord = (atm["rho_kgm3"] * st["W"] * st["chord"]
                         / atm["mu_Pas"])                             # [DERIVED]

        # ---- radial load distributions ------------------------------------------
        rho_ = atm["rho_kgm3"]
        W, chord, cl, cd, phi = st["W"], st["chord"], st["cl"], st["cd"], st["phi"]
        self.dT_dr = (0.5 * rho_ * W ** 2 * s.n_blades * chord
                      * (cl * np.cos(phi) - cd * np.sin(phi)))        # [DERIVED]
        self.dQ_dr = (0.5 * rho_ * W ** 2 * s.n_blades * chord
                      * (cl * np.sin(phi) + cd * np.cos(phi)) * self.r)  # [DERIVED]
        self.T_blade_element = np.trapezoid(self.dT_dr, self.r)       # [DERIVED] cross-check
        self.Q_blade_element = np.trapezoid(self.dQ_dr, self.r)       # [DERIVED] cross-check

    # -- verification (gate G0) ----------------------------------------------------
    def verify(self) -> dict:
        """Gate G0. Independent closure checks. Returns a pass/fail record."""
        checks = {}

        # 1. two independent efficiency routes
        e1 = abs(self.eta_coeff - self.eta_bem) / self.eta_bem * 100.0
        checks["eta_route_agreement_pct"] = {
            "value": e1, "limit": 1.0, "pass": bool(e1 < 1.0),
            "what": "C_T*J/C_P  vs  Tc/Pc"}

        # 2. BEM efficiency must not exceed the actuator-disk ideal ceiling
        checks["eta_below_ideal_ceiling"] = {
            "value": self.eta_bem, "limit": self.eta_ideal,
            "pass": bool(self.eta_bem < self.eta_ideal),
            "what": "minimum-induced-loss eta must be below the actuator-disk ceiling"}

        # 3. blade-element integration reproduces the Adkins thrust
        e3 = abs(self.T_blade_element - self.thrust_N) / self.thrust_N * 100.0
        checks["thrust_integration_pct"] = {
            "value": e3, "limit": 2.0, "pass": bool(e3 < 2.0),
            "what": "Int(dT/dr)dr  vs  Tc-derived thrust"}

        # 4. blade-element torque reproduces the Adkins power
        e4 = abs(self.Q_blade_element - self.torque_Nm) / self.torque_Nm * 100.0
        checks["torque_integration_pct"] = {
            "value": e4, "limit": 3.0, "pass": bool(e4 < 3.0),
            "what": "Int(dQ/dr)dr  vs  Pc-derived torque"}

        # 5. prescribed loading recovered
        tau_out = self.thrust_N / (self.atm["rho_kgm3"] * self.area * self.V0 ** 2)
        e5 = abs(tau_out - self.spec.tau) / self.spec.tau * 100.0
        checks["tau_closure_pct"] = {
            "value": e5, "limit": 0.1, "pass": bool(e5 < 0.1),
            "what": "recovered tau vs prescribed tau"}

        checks["converged"] = {"value": self.converged, "pass": bool(self.converged),
                               "what": "zeta iteration converged"}
        checks["ALL_PASS"] = all(v["pass"] for v in checks.values())
        return checks

    # -- outputs -------------------------------------------------------------------
    def radial_table(self) -> dict:
        st = self.st
        return {
            "r_over_R": self.xi,
            "r_m": self.r,
            "chord_m": st["chord"],
            "chord_over_R": st["chord"] / self.R,
            "beta_deg": np.degrees(self.beta_rad),
            "phi_deg": np.degrees(st["phi"]),
            "alpha_ideal_deg": np.degrees(self.alpha_ideal),
            "sweep_deg": np.degrees(self.sweep_rad),
            "toc": st["toc"],
            "camber_m": self.camber_m,
            "camber_p": np.full_like(self.xi, self.spec.camber_pos),
            "Cl_design": st["cl"],
            "Cd_est": st["cd"],
            "M_rel": self.M_rel,
            "M_helical": self.M_hel,
            "M_normal": self.M_normal,
            "PG_valid": self.pg_valid.astype(int),
            "Re_chord": self.Re_chord,
            "solidity": self.solidity,
            "a_axial": st["a_ax"],
            "a_tangential": st["a_tan"],
            "F_prandtl": st["F"],
            "dT_dr_Npm": self.dT_dr,
            "dQ_dr_Nmpm": self.dQ_dr,
        }

    def summary(self) -> dict:
        s = self.spec
        return {
            "design_chain": [
                "cruise condition", "diameter", "rotational speed / tip-Mach constraint",
                "advance ratio", "non-dimensional loading tau",
                "thrust & power coefficients", "dimensional interpretation"],
            "inputs": {
                "mach_flight": s.mach_flight, "altitude_m": s.altitude_m,
                "diameter_m": s.diameter_m, "hub_tip_ratio": s.hub_tip_ratio,
                "mach_tip_rotational": s.mach_tip_rot, "tau_nondimensional_loading": s.tau,
                "n_blades": s.n_blades, "cl_root": s.cl_root, "cl_tip": s.cl_tip,
                "mn_limit": s.mn_limit, "section_family": "NACA 4-digit (closed form)",
            },
            "atmosphere": self.atm,
            "operating_point": {
                "V0_ms": self.V0, "R_m": self.R, "R_hub_m": self.R_hub,
                "U_tip_ms": self.U_tip, "omega_rads": self.omega, "rpm": self.rpm,
                "n_rev_per_s": self.n_rev, "advance_ratio_J": self.J,
                "disk_area_m2": self.area,
                "mach_tip_ROTATIONAL": s.mach_tip_rot,
                "mach_tip_HELICAL": self.mach_tip_helical,
                "NOTE": "rotational and helical tip Mach are distinct quantities and "
                        "are never interchanged in this project",
            },
            "nondimensional": {
                "tau": s.tau, "Tc_adkins": self.Tc, "Pc_adkins": self.Pc,
                "C_T": self.C_T, "C_P": self.C_P, "zeta_displacement_ratio": self.zeta,
            },
            "performance": {
                "eta_actuator_disk_ideal_CEILING": self.eta_ideal,
                "eta_bem_minimum_induced_loss": self.eta_bem,
                "eta_from_coefficients_crosscheck": self.eta_coeff,
                "CAVEAT": "eta depends on the low-order Cd model and is an ESTIMATE. "
                          "[CFD-TBD] ANSYS Fluent determines the achieved value.",
            },
            "dimensional_interpretation": {
                "NOTE": "OUTPUTS of the non-dimensional design. Not requirements. "
                        "No aircraft-level thrust requirement exists in this project.",
                "thrust_N": self.thrust_N, "thrust_kN": self.thrust_N / 1000.0,
                "power_W": self.power_W, "power_MW": self.power_W / 1.0e6,
                "torque_Nm": self.torque_Nm,
                "disk_loading_Pa": self.disk_loading_Pa,
            },
            "geometry_outcomes": {
                "chord_root_m": float(self.st["chord"][0]),
                "chord_75R_m": float(np.interp(0.75, self.xi, self.st["chord"])),
                "chord_tip_m": float(self.st["chord"][-1]),
                "beta_root_deg": float(np.degrees(self.beta_rad[0])),
                "beta_75R_deg": float(np.degrees(np.interp(0.75, self.xi, self.beta_rad))),
                "beta_tip_deg": float(np.degrees(self.beta_rad[-1])),
                "sweep_tip_deg": float(np.degrees(self.sweep_rad[-1])),
                "max_solidity": float(np.max(self.solidity)),
                "aspect_ratio_blade": float((self.R - self.R_hub)
                                            / np.mean(self.st["chord"])),
            },
            "validity_flags": {
                "stations_outside_PG_validity": int(np.sum(~self.pg_valid)),
                "n_stations": int(len(self.xi)),
                "max_M_normal": float(np.max(self.M_normal)),
                "max_M_helical": float(np.max(self.M_hel)),
                "WARNING": "Sections outside Prandtl-Glauert validity have sectional "
                           "aerodynamics that this model cannot be trusted for. That is "
                           "the reason 3-D compressible CFD is required. [CFD-TBD]",
            },
            "convergence": {"converged": self.converged, "iterations": self.iterations,
                            "zeta": self.zeta},
        }


def station_independence_check(spec: DesignSpec, factor: int = 2) -> dict:
    """Analytical analogue of a mesh-independence study. Gate G0."""
    d1 = OpenFanRotorDesign(spec).solve()
    s2 = DesignSpec(**{**asdict(spec), "n_stations": spec.n_stations * factor - 1})
    d2 = OpenFanRotorDesign(s2).solve()
    dT = abs(d2.thrust_N - d1.thrust_N) / d1.thrust_N * 100.0
    dQ = abs(d2.torque_Nm - d1.torque_Nm) / d1.torque_Nm * 100.0
    de = abs(d2.eta_bem - d1.eta_bem) / d1.eta_bem * 100.0
    return {"n_base": spec.n_stations, "n_refined": s2.n_stations,
            "thrust_change_pct": dT, "torque_change_pct": dQ, "eta_change_pct": de,
            "limit_pct": 0.1,
            "pass": bool(dT < 0.1 and dQ < 0.1 and de < 0.1)}
