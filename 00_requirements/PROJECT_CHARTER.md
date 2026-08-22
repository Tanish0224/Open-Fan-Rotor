# PROJECT CHARTER
### Open-Fan Rotor — Aerodynamic Design and Installation-Effect Assessment

**Project ID:** BA-OF-01
**Phase:** 0 — Definition (no engineering work performed)
**Created:** 22 August 2026
**Parent research:** [`OPEN_FAN_PROJECT_SELECTION_RESEARCH.md`](../../OPEN_FAN_PROJECT_SELECTION_RESEARCH.md) — 774 lines, preserved, **not superseded by this document**
**Authority:** This charter defines *why* the project exists. [`PROJECT_REQUIREMENTS.md`](PROJECT_REQUIREMENTS.md) defines *what may be claimed*. Where they conflict, the requirements document wins.

---

## 6.1 What is the project?

This project designs a **single-rotation open-fan rotor** for high-subsonic cruise from first
principles — actuator-disk sizing followed by blade-element momentum theory under an explicit
helical-tip-Mach constraint — realises it as parametric SolidWorks CAD in which no dimension is
typed by hand, and evaluates it with compressible RANS CFD in ANSYS Fluent. The rotor is first
characterised **isolated** in a uniform free stream, establishing its thrust, torque, propulsive
efficiency and radial loading against the analytical design intent. The same rotor, at the same
design and operating condition, is then evaluated **installed** ahead of a wing, so that the only
variable changed between the two cases is the presence of the airframe. The measured difference —
in net propulsive force, propulsive efficiency, and the radial and circumferential distribution of
blade loading — is the project's output.

> **Scope reality check (read this before the rest of the charter).** The authorised effort is
> approximately **five working days on a personal workstation**. That budget delivers the *design*
> and *isolated* half of the sentence above. The **installed** half is deferred to Stage 3 and is
> **not** claimable until it exists. See [`PROJECT_ROADMAP.md`](PROJECT_ROADMAP.md) §Staging and
> [`PROJECT_REQUIREMENTS.md`](PROJECT_REQUIREMENTS.md) §7.2 Tier 3.

---

## 6.2 What is the engineering problem?

### Why isolated propulsor performance is insufficient

An isolated propulsor is characterised in a **uniform, axisymmetric, unbounded free stream**. Every
term in its performance bookkeeping is unambiguous: the inflow is known, the streamtube is
axisymmetric, thrust is the axial force on the rotating body, and there is no other body whose drag
could be confused with it.

An installed propulsor violates all four of those conditions simultaneously. The specific
consequences — not "installation affects performance", but the actual mechanisms — are:

**M1 — The rotor inflow is no longer uniform or axisymmetric.**
A wing mounted downstream of a tractor rotor imposes an upstream potential field on the rotor disk.
The disk therefore sees a circumferentially varying axial velocity, so each blade experiences a
different incidence at each azimuthal position. In the isolated case, every blade at a given radius
sees identical conditions at every instant; installed, it does not.

**M2 — The slipstream is a swirling, high-dynamic-pressure annulus washing over the wing.**
The rotor adds both axial and tangential momentum. Downstream, the wing is immersed in flow with
elevated `q` and a non-zero swirl angle. On the up-going blade side the swirl raises local wing
incidence; on the down-going side it lowers it. Wing sectional lift and induced drag are
redistributed spanwise, and the redistribution is *asymmetric* about the nacelle centreline.

**M3 — Scrubbing drag.** Wing area immersed in the slipstream sees `q_scrub > q_∞` and therefore
higher skin friction than the same area in the free stream. This is a real force that must be
charged to one side of the thrust–drag ledger.

**M4 — The thrust–drag dividing surface becomes a convention, not a fact.**
An open fan has no nacelle, so there is no natural control surface separating "engine" from
"airframe". The same physical flowfield yields different reported thrust and different reported drag
depending on where the analyst draws the line. Unstated, this makes an installed result
unreproducible.

**M5 — Non-linear interference.** The installed force is not the sum of the isolated parts. The
residual, `F_installed − (F_rotor,isolated + F_wing,isolated)`, is the genuinely coupled term.

### Separation of what is known from what this project measures

| | Mechanism | Status for this project |
|---|---|---|
| M1 | Non-uniform rotor inflow from downstream body | **Known from literature** (Whittle Lab pylon/AoA work, GE 1P-load patents). **To be measured here** as the circumferential variation of blade loading — steady, time-averaged only |
| M2 | Slipstream swirl changing wing sectional incidence | **Known from classical propeller–wing literature.** **To be measured here** as spanwise wing loading with and without the rotor |
| M3 | Scrubbing drag | **Known.** **To be measured here** as `q_scrub/q_∞` and the wing viscous-force delta |
| M4 | Bookkeeping ambiguity | **Known as a discipline-level problem.** **Not measured** — it is *declared* as a convention and its sensitivity tested |
| M5 | Non-linear interference | **Known to exist; magnitude configuration-specific.** **To be measured here** by three-run decomposition |

Nothing in the left column is a discovery claim. The project's contribution is a **controlled,
traceable quantification on a rotor whose every geometric feature the author can derive** — not the
discovery of a new mechanism.

---

## 6.3 Research question

### Primary

> **For a single-rotation open-fan rotor held at a fixed design point and fixed operating condition,
> what is the change in net propulsive force and propulsive efficiency between an isolated
> free-stream installation and a wing-installed configuration, and how does that change decompose
> into altered rotor inflow, altered wing forces, and non-linear interference?**

### Secondary (maximum three, all answerable by the planned methods)

**S1.** Does the rotor designed by blade-element momentum theory achieve, in 3-D compressible RANS,
the radial thrust distribution and total thrust the design method predicted — and where does the
3-D result depart from the 1-D design intent?

**S2.** How does propulsive efficiency vary with helical tip Mach number at fixed thrust, and what
does the acoustically-motivated tip-speed limit therefore cost aerodynamically?

**S3.** How large is the installed circumferential variation in blade loading relative to the
isolated (uniform) case, at the same operating point?

**Deliberately excluded as questions:** anything acoustic, anything structural, anything requiring
a mission or cycle model, and any question of the form "is an open fan better than a ducted fan."

---

## 6.4 Hypothesis

A quantitative hypothesis is **not** justified by the evidence available, and stating one would be
false precision. What can be stated is a **physical expectation with a stated sign and a stated
reason**:

| # | Expectation | Physical basis | Confidence |
|---|---|---|---|
| H1 | Installed **net propulsive force will differ from isolated by a non-zero amount**, and the wing viscous force will increase | Scrubbing (M3) is unambiguously additive drag | High — mechanism is certain, magnitude is not |
| H2 | Installed rotor inflow will show **measurable circumferential non-uniformity** correlated with wing position | Upstream potential field of a lifting body (M1) | High |
| H3 | Wing spanwise loading will be **asymmetric** about the rotor axis, up-going side loaded more | Swirl-induced incidence change (M2) | High |
| H4 | Non-linear interference will be **small relative to the sum of the linear parts** at cruise incidence | Attached flow, moderate disk loading | **Low — this is a guess and is labelled as one** |
| H5 | Propulsive efficiency will **fall** as helical tip Mach rises past the design value | Compressibility/shock loss at the tip | High — but the magnitude is the whole point of S2 |

**H4 is explicitly flagged as weak.** If the project finds large interference, that is a result, not
a failure. No expectation in this table may be reported as a prediction that was "confirmed" — the
CFD measures, the table only records what was expected beforehand so that hindsight cannot be
smuggled in later.

---

## 6.5 Why does this matter now?

Grounded in specific, dated, primary-source activity — not sustainability messaging:

1. **GE Aerospace, Boeing, NASA and Oak Ridge National Laboratory** were awarded **840,000
   supercomputing hours** under the DOE INCITE programme on Aurora and Frontier, explicitly to
   "study the aerodynamics of an Open Fan mounted on an aircraft wing in simulated flight
   conditions" (GE Aerospace press release, Nov 2024). GE framed all prior exascale work as
   *component-level* and this as the step to **airplane–engine integration**.
2. **Airbus had still not chosen** between a reinforced rear-fuselage pylon and the inboard No. 3
   wing position for the A380 Flight Lab open-fan demonstrator as of **July 2026**. The mounting
   position — an installation question — is still open at flight-demonstrator stage.
3. **Boeing patented an overwing strut** designed to accept **either a ducted or an unducted
   engine** on a common wing (US 12,698,086, issued 4 August 2026), while simultaneously issuing an
   RFI for a **ducted** ~30,000 lbf powerplant. Boeing's stated reservation about open fan is
   **integration and programme risk**, not thermodynamics.
4. The publicised A380 flight-test objectives explicitly include "assessment of aircraft/engine
   integration and aerodynamics (thrust, drag, loads)."

**The inference this project rests on:** the *uninstalled* propulsive advantage of a low-disk-loading
open rotor is not in technical dispute — it follows from actuator-disk theory. What is in dispute,
and what is currently governing an airframer's commitment decision, is **how much of it survives
installation**. That is the question this project addresses at student scale.

**What this project does not claim about that context:** it does not reproduce, approximate, predict
or benchmark CFM RISE. It uses the industry context to justify the *choice of question*, never to
lend authority to the *answer*.

---

## 6.6 Why is this the right project for an aerodynamics M.Tech student?

Every layer maps onto core aerodynamics that must be derivable on a whiteboard:

| Fundamental | Where it appears | What the student must be able to do |
|---|---|---|
| **Momentum / actuator-disk theory** | Design point sizing; the `η_p` ceiling; the disk-loading argument | Derive `η_p,ideal = 2/(1+√(1+2T/ρAV₀²))` and explain why open fan exists |
| **Blade-element theory** | Chord, twist and loading distribution | Derive the local velocity triangle and close BEM iteration by hand for one radius |
| **Velocity triangles** | Every radial station; the link between twist and advance ratio | Draw the triangle at hub, mid and tip and explain why twist is non-linear |
| **Compressibility** | The helical-tip-Mach constraint; why the blade is swept | Compose flight and rotational Mach vectorially; justify sweep from the normal-Mach argument |
| **Pressure vs viscous force decomposition** | Thrust and torque integrals; scrubbing drag | Separate pressure and shear contributions and say which dominates where |
| **Wake / slipstream behaviour** | Swirl, contraction, total-pressure deficit | Explain residual swirl as lost work and where it goes |
| **Propulsor–wing interaction** | The entire installed case | Explain up-going vs down-going asymmetry from swirl |
| **Verification vs validation** | The whole V&V plan | State precisely what each earns the right to claim |

The project is deliberately **narrow in physics and deep in rigour** rather than broad and shallow.
It contains one rotor, one design point, one installation change, and a validation chain — not a
survey.

---

## 6.7 Explicit exclusions

The following are **outside the project** and may not enter the baseline silently. Each is
classified. Anything reclassified later requires a Decision Log entry.

| Item | Classification | Reason |
|---|---|---|
| Aeroacoustic prediction (FW-H, broadband, tone) | **EXCLUDED** | No acoustic solver, no validation path, and it would make every conclusion unfalsifiable at this scope |
| Acoustic liners | **EXCLUDED** | Meaningless without a duct |
| Outlet guide vanes / swirl-recovery vanes | **FUTURE WORK** — see ED-008 | Research showed swirl recovery is a +0.2–3 % second-order effect; an OGV doubles CFD cost and is not required by the research question |
| Counter-rotating configuration | **EXCLUDED** | Not the architecture under study; RISE is single-rotation |
| Aeroelasticity / FSI / blade structural sizing | **EXCLUDED** | Different discipline; no structural solver in scope |
| Blade-off, containment, certification | **EXCLUDED** | Not aerodynamics |
| Gearbox, pitch-change mechanism design | **EXCLUDED** | Mechanical design, not aerodynamics |
| Engine cycle / core / thermodynamic model | **EXCLUDED** | The rotor is analysed as a propulsor, not an engine |
| Aircraft mission or fuel-burn model | **EXCLUDED** | Forbids any fuel-burn claim — see requirements Tier 3 |
| Full-aircraft CFD (fuselage, tail, full span) | **EXCLUDED** | Semi-span wing segment only |
| LES / DES | **EXCLUDED** from baseline; **FUTURE WORK** | Not workstation-feasible |
| Unsteady full-annulus URANS | **FUTURE WORK** | Required for true blade-passing/1P physics; not workstation-feasible in scope |
| Multi-variable / black-box optimisation | **EXCLUDED** | Undefendable in interview; the research explicitly rejected it |
| Angle-of-attack / 1P load study | **FUTURE WORK** | Needs URANS; rejected on method in the parent research (C8) |
| Ducted-vs-open comparison | **EXCLUDED — PERMANENTLY** | Rejected on evidence in the parent research (C1, lowest-scoring candidate). Must not re-enter |
| Proprietary or traced RISE geometry | **FORBIDDEN** | Destroys defensibility; see requirements Tier 3 |
| Institutional HPC use | **EXCLUDED as a dependency** | Not authorised for this project; may not be claimed in portfolio material |

---

## Related documents

- [`PROJECT_REQUIREMENTS.md`](PROJECT_REQUIREMENTS.md) — frozen scope and the claim hierarchy (**controlling document**)
- [`PHYSICS_AND_METRICS_MAP.md`](PHYSICS_AND_METRICS_MAP.md) — geometry → physics → metric → interpretation
- [`ROTOR_DESIGN_METHODOLOGY.md`](ROTOR_DESIGN_METHODOLOGY.md) — how the blade will be designed
- [`DESIGN_POINT_SELECTION.md`](DESIGN_POINT_SELECTION.md) — evidence for every design parameter
- [`INSTALLATION_CONFIGURATION_SELECTION.md`](INSTALLATION_CONFIGURATION_SELECTION.md) — which installation, and why
- [`VALIDATION_AND_VERIFICATION_PLAN.md`](VALIDATION_AND_VERIFICATION_PLAN.md) — what may be called verified vs validated
- [`CFD_METHODOLOGY_ROADMAP.md`](CFD_METHODOLOGY_ROADMAP.md) — numerical method and its consequences
- [`COMPUTATIONAL_FEASIBILITY_AUDIT.md`](COMPUTATIONAL_FEASIBILITY_AUDIT.md) — workstation-feasible levels
- [`PROJECT_ROADMAP.md`](PROJECT_ROADMAP.md) — phases, gates, stop conditions
- [`INTERVIEW_DEFENSIBILITY_MATRIX.md`](INTERVIEW_DEFENSIBILITY_MATRIX.md) — question → answer → evidence
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) — every external source and its exact use
- [`DECISION_LOG.md`](DECISION_LOG.md) — ED-001 onward
