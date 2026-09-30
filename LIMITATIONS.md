# Limitations

## Scope

- The 0.75 propulsive-efficiency target was not reached; the highest design-RPM value is 0.572 (V08).
- The design was not optimised. The campaign is a sequence of design iterations and a few experiments around
  V08.
- The CFD results are not compared with experimental or published benchmark data. None exists for this regime:
  compressible flow in axial flight with a supersonic helical tip Mach.
- The structural FEA is screening-level only.

## CFD numerics

1. **Convergence.** No design-RPM case meets the full-history criterion (1 % peak-to-peak on thrust and torque
   over S2–S10). All of them except V10 pass the rolling last-five-checkpoint window. Only V11, the 1000 rpm
   off-design case, passes both. The rolling window was introduced during the campaign. The original target was thrust
   and torque stationary over the final 500+ iterations, and the full-history window is the closer of the two to
   that. ([`RESULTS.md`](RESULTS.md), `cfd_campaign/campaign_summary.json`)
2. **Mesh independence was not assessed.** Each case ran on one mesh of about 6–7 M cells. A 9.1 M-cell mesh
   exceeded the available memory, so a refinement study on the 360° domain was not feasible on this hardware.
   Cell counts also vary between cases relative to V08: −0.4 % to +9.1 % across V10, V12 and V15, and −1.5 % to
   +1.9 % for V05n16 and V06e. These differences are uncontrolled.
3. **Residuals** drop about 3 orders, against a 4-order target
   (`cfd_campaign/*/residuals_*.csv`).
4. **No prism layers.** The blade y⁺ node median is about 430–440, with more than 90 % of blade nodes above 300
   (`cfd_campaign/*/blade_yplus_node_statistics_*.json`). The wall treatment is outside its intended range, so
   separation onset and skin-friction drag are not resolved.

Together these mean the original convergence target (G2 in [`cfd_method/`](cfd_method/README.md)) was not met.

## Models

5. **BEM is the design model, not a prediction of the CFD.** The CFD never reaches the design thrust. The cases
   reach 22–45 % of it, so BEM and CFD efficiencies are not directly comparable. BEM uses a closed-form NACA
   4-digit drag estimate, while the CFD sections from V05n16 on are NACA 16-series.
6. **The design sweep law over-credits Mach relief.** It uses the flat-wing relation M_n = M·cos Λ. For a
   circumferentially swept blade the relief is smaller, and the analysed sections run above their own critical
   Mach at the design condition. (Design checks listed in the unpublished-evidence register.)
7. **Sectional quantities are inferred.** Section lift and drag come from a blade-element inversion of the CFD
   surface data. The polars for V04cf, V05n16 and V06e use a zero-induction basis that was later found to be
   wrong, and they were not regenerated. Absolute incidence carries about ±1° uncertainty from the blade-angle
   reference.

## Geometry in CFD

8. **The CFD blades are not PRIME.** V03 to V05n16 use PRIME's design table; V06e onward use the v06 table. The
   trailing edge was thickened for meshing, and the meshed thickness differs from the CAD value: a 0.012c CAD
   edge meshed as 0.0161c–0.0212c depending on the case ([`cad/README.md`](cad/README.md)). PRIME's own 0.006c
   edge could not be volume-meshed (V09, V13), and a 0.008c edge meshed but the solve diverged (V09b).
9. **Span.** The CFD blade covers r = 0.565–1.725 m against a design span of 0.490–1.750 m, so thrust and torque
   are each about 3 % low.
10. **PRIME still has the camber error** found in V03, because it uses the same section-placement code. PRIME
    is retained unchanged as the record of the built design.

## Individual cases

11. **V10:** the planned mechanism check (sectional drag should fall) could not be done, because sectional data
    were not exported. The prediction failed, but the mechanism was neither confirmed nor ruled out.
12. **V12:** the mesh has 9.1 % more cells and a different meshed trailing edge (0.0212c vs 0.0188c), so the
    sweep effect is not isolated.
13. **V15:** the incidence change was measured at one station over one small blade-angle change, and the only
    lift-slope estimate is a two-point difference. That argues against a stalled root at r/R 0.40, but it does
    not show what correction the root needs. The opposite-sign case (V16) was not solved.
14. **V11** changes speed and twist together and runs at 1000 rpm, so it is not comparable with the design-RPM
    cases.
15. **V14** is a boundary-condition test on V08, not a design.
16. **V13 and V16 have no CFD result.**

## Structural work

17. **The FEA is screening-level.** Loads were partly carried over from an earlier sizing step, and the
    allowables were provisional. The governing stresses in Stages 18 and 19 were not mesh-converged, and the
    full-rotor model (Stage 20) did not close its global moment balance. Stages 24 and 26 were benchmarks on test
    blocks. There is no fatigue, flutter or bird-strike analysis. ([`structural/README.md`](structural/README.md))
18. **The CAD assembly is a geometry lock,** not a manufacturing design. The drawings are reference drawings,
    not for manufacture.

## Reproducibility

19. **Not everything is in the repository.** The mesh, case and solution files are 0.12–0.20 GB each, too large
    to publish. Solver logs and field exports are summarised as derived files, and some records are identified
    only by hash. See [`reproducibility/REPRODUCE.md`](reproducibility/REPRODUCE.md).
