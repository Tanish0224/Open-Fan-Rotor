# EVIDENCE INDEX
### BA-OF-01 — every external source, and the exact use it is put to

**Created:** 22 August 2026 · **Phase:** 0

**Rule:** a source that supports no specific project decision does not belong here. Nothing in this
index is decorative. If a source is listed, the "Exact project use" column names where it acts.

**Evidence strength**
- **S1** — primary/authoritative, directly states the claim
- **S2** — peer-reviewed or government technical, directly states the claim
- **S3** — primary source, but the project **infers** rather than reads the claim
- **S4** — technical press; context only
- **S5** — **asserted but not yet verified by this project** — may not be relied upon

---

## A. SOURCES THAT SET THE PROJECT QUESTION

| Source | Date | Organisation | Claim it supports | Exact project use | Strength |
|---|---|---|---|---|---|
| *GE Aerospace, Boeing and NASA to study performance of installed Open Fan engine design* | Nov 2024 | GE Aerospace | GE+Boeing+NASA+ORNL awarded **840 000 INCITE hours** on Aurora/Frontier to model an Open Fan **mounted on an aircraft wing** | **The single load-bearing justification for choosing installation as the project question.** Charter §6.5 item 1 | **S1** |
| *Boeing Keeps an Open Mind on Open-fan Engine…* / Leeham coverage | 16 Jul 2026 | AIN / Leeham (reporting Boeing) | Boeing has not ruled out open fan but prefers lower-risk propulsion; issued a **ducted** ~30 klbf RFI | Establishes that Boeing's reservation is **integration risk, not thermodynamics** — Charter §6.5 item 3 | **S4** |
| US Patent **12,698,086**, *Aircraft with overwing engine position* | 4 Aug 2026 | Boeing | Overwing strut acting as a common platform for **either** a ducted or unducted engine | Evidence that installation compatibility is the live variable. Also the basis for evaluating and **rejecting** the over-wing configuration | **S3** — patent record confirmed; claim detail read via Aviation Week, **full text not retrieved** |
| *Open Fan Advances Toward Flight Test Demonstration* | 18 Jul 2026 | GE Aerospace / CFM / Safran | ~500 test campaigns; Open Fan and **OGV** PDRs complete; wind-tunnel aeroacoustics exceeded objectives | Establishes programme maturity and that **no installed performance is public** | **S1** |
| *Gaining Altitude: A380 to Test CFM's Open-Fan* + Farnborough 2026 material | Jul 2026 | GE Aerospace / Airbus | A380 Flight Lab; **wing vs rear-fuselage mounting still undecided**; test objectives include "aircraft/engine integration and aerodynamics (thrust, drag, loads)" | Charter §6.5 items 2 and 4 | **S1** |

## B. SOURCES THAT SET DESIGN PARAMETERS

| Source | Organisation | Claim | Exact project use | Strength |
|---|---|---|---|---|
| CFM *Engine Architecture* page; *5 Things to Know About RISE* | CFM / GE | Single rotating variable-pitch fan + stationary variable-pitch OGV; geared; blades **"over 1.6 m"**; OGVs close as an air brake | Architecture definition (rotor + OGV, single rotation). **Blade length ⇒ D ≈ 3.5–4 m is an inference by this project, not a CFM statement** | **S1** for architecture; **S3** for diameter |
| CFM public statements on operating range | CFM | Open fan designed for normal operation **M0.75–0.85** | Justifies `M₀` = 0.75 as inside the stated range | **S1** |
| NASA propfan programme (SR-2 / SR-3 results) | NASA | SR-3: 45° tip sweep, area-ruled spinner, **78.7 % net efficiency at M0.8**; design altitude 10.68 km | (a) qualitative anchor for the **sweep** argument; (b) corroborates the 35 000 ft altitude choice; (c) cross-check that `J` ≈ 3 is the propfan regime | **S2** |
| Classical propfan practice | Literature | Rotational tip Mach kept near 0.8 for compressibility and noise | Justifies the tip-Mach constraint | **S2** |
| Adkins & Liebeck, *Design of Optimum Propellers* (1983) | Journal of Propulsion & Power | Closed-form minimum-induced-loss propeller design formulation | **The selected design method** (ED-004) | **S2** |

## C. SOURCES THAT SET THE VALIDATION STRATEGY

| Source | Organisation | What is public | Exact project use | Strength |
|---|---|---|---|---|
| **Caradonna & Tung, NASA TM-81232** (NTRS 19820004169) | NASA Ames / US Army | Blade surface `Cp` at multiple radial stations; tip-vortex surveys; tip Mach to **0.877**; rectangular untwisted untapered NACA 0012, AR 6, R = 1.143 m, c = 0.191 m. **US Government work, public use** | **MANDATORY validation case** — validation axis A (compressible rotating blade, transonic tip). Geometry is reconstructable from the published definition, so **no access request is needed** | **S2** |
| **UIUC Propeller Database**, Vols 1–4 (Brandt, Deters, Dantsker) | Univ. of Illinois | Geometry (`r/R`, `c/R`, `β`) **and** measured `C_T`, `C_P` vs `J` for ~250 propellers; **freely downloadable** | **RECOMMENDED validation case** — validation axis B (axial-flight performance bookkeeping) | **S2** |
| *An Open Virtual Test Case for Open Fans*, J. Turbomach. 148(6):061019 | PANDORA consortium / UPM | An open-access open-fan geometry with pitch settings and **RANS** results | **REJECTED as validation** (it is CFD, not experiment). Retained only as an optional solver cross-check | **S5** — open-access status stated by the publication; **download terms not verified by this project** |
| TUD-PROWIM-TIP (Zenodo 18599612); TUD-XPROP-3 (Zenodo 13645390) | TU Delft | Propeller / propeller–wing CAD and experimental datasets | **REJECTED** — CC-BY-NC-ND, **restricted, released only on request**. Project deliberately designed not to depend on it *(user decision, 22 Aug 2026)* | **S2** for existence; access **not obtained** |
| NASA F31/A31 Open Rotor Propulsion Rig data (NTRS 20150000320) | NASA | Extensive aero and acoustic data | **REJECTED as validation** — blade **geometry** not established as public, so the case cannot be reproduced | **S2** for data; geometry **S5** |

> **Correction to the parent research, recorded here.** The parent research recommended NASA
> SR-2/SR-3 and F31/A31 as the validation path. Investigation established that their **performance
> data** is public but their **blade coordinate geometry** is not confirmed obtainable. Since
> validation requires reproducing the geometry, that path is **not reliable** and has been replaced
> by Caradonna–Tung + UIUC. The parent research is **not edited**; this index records the correction.

## D. SOURCES THAT SET SCOPE BOUNDARIES (used to *exclude* things)

| Source | Claim | Exact project use | Strength |
|---|---|---|---|
| TU Delft swirl-recovery body of work (incl. *J. Propulsion & Power*, 10.2514/1.B36877) | SRV gains **+0.20 %, +0.39 %** cruise; **+2.62 %, +3.07 %** high thrust; another study **+2.4 %**; another **+0.7 %**; **+20 dB** axial noise penalty | **The evidence base for rejecting the OGV and swirl recovery** (ED-008). The *spread* is as important as the values — it shows no consensus figure exists | **S2** |
| *The Influence of an Upstream Pylon on Open Rotor Aerodynamics at Angle of Attack*, J. Turbomach. 141(2):021006 | Blade passing a pylon wake sees a sudden incidence rise; requires **full-annulus URANS**; produces side-band tones | **The evidence for rejecting the pusher/pylon configuration on method** (ED-005) | **S2** |
| AIAA 2023-3305, *Angle of Attack Effects on Open Fan Propulsion Systems at Take-Off*; GE patents US 12,221,893 / 12,421,864 | Oblique inflow ⇒ 1P loads; GE patents circumferentially non-uniform pitch | Evidence that AoA/1P is a real industry problem — and the basis for **excluding** it as requiring URANS | **S1** (patents) / **S2** (paper) |
| *Civil turbofan propulsion aerodynamics: thrust–drag accounting…*, Aerosp. Sci. Technol. | Thrust–drag bookkeeping is convention-dependent and installation-position-dependent | **The basis for declaring convention BK-1 in advance** and for the BK-1/BK-2 sensitivity | **S2** |
| NASA NTRS 20130013993, open-rotor installation aeroacoustics | Rotor ahead of a wing ⇒ ~**+10 dB**; over-wing gives substantial shielding | Explains *why* over-wing is industrially attractive — and is cited **only** to justify considering and then rejecting it, since acoustics is excluded | **S2** |
| AIAA *J. Aircraft*, overwing vs underwing nacelle optimisation | Over-wing disturbs the transonic upper surface; risk of wave drag | Supports rejecting the over-wing configuration as "two theses" | **S2** |
| NASA TM-20220015470, open-rotor braced-wing transport | Scrubbing drag modelled via elevated `q_scrub`; charged to the airframe | Basis for mechanism M3 and for the BK-1 convention placing scrubbing on the airframe | **S2** |

## E. INTERNAL SOURCES

| Artifact | Use | Strength |
|---|---|---|
| `../../OPEN_FAN_PROJECT_SELECTION_RESEARCH.md` | Parent research: candidate generation, decision matrix, geometry-provenance rule, "what not to do" list | Internal — **preserved, cited, not superseded** |
| `../../CLAUDE.md` §36 | SolidWorks automation is fully capable; reference-plane-only sketching rule; save/reopen verification rule; `None` ≠ broken API | Governs Phase 2 method | Internal, authoritative |

---

## F. CLAIMS THIS PROJECT MAKES THAT HAVE **NO** EXTERNAL SOURCE

Listed explicitly so they cannot be mistaken for sourced facts:

| Claim | Status |
|---|---|
| Design thrust of 20 kN | **UNSOURCED placeholder.** Blocking item B1 |
| Blade count of 12 | **UNSOURCED placeholder** — must become a Phase 1 output |
| Hub/tip ratio | Not yet chosen |
| NACA 16-series suitability | Reasoned, but **polar data availability unverified.** Blocking item B2 |
| That D ≈ 3.5 m follows from "blade over 1.6 m" | **An inference by this project**, not a CFM statement |
| Runtime and cell-count estimates | **Estimates**, not measurements. Superseded by the mandatory calibration run |
| Workstation core count and RAM | **NOT MEASURED.** Open item O1; must be confirmed directly before the fine mesh is attempted |
