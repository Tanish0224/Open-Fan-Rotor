# Limitations

This file lists what the work in this repository does **not** demonstrate. Each item links to where the evidence
lives.

## CFD convergence and verification

1. **No design-RPM case satisfies full-history convergence.** Every design-RPM case with a full checkpoint
   history passes the rolling last-five-checkpoint window, except V10, which fails both. All of them fail the full second-order history
   (S2–S10) against a 1 % bound on thrust and torque. The only case that passes both windows is **V11, which is a
   1000 rpm off-design case**. ([`RESULTS.md`](RESULTS.md), `cfd_campaign/campaign_summary.json`)
2. **The rolling-window criterion was introduced during the campaign.** The pre-registered plan asked for thrust
   and torque to be stationary over the final 500+ iterations, which the full-history window approximates and
   the design-RPM cases fail.
3. **No mesh-independence study exists.** Each case was solved on one mesh of about 6–7 M cells. A 9.1 M-cell mesh
   exceeded the available memory, so a refinement ladder on the 360° domain was not feasible on this hardware.
   Mesh-count differences relative to V08 (−0.4 % to +9.1 % across the controlled experiments V10, V12 and V15;
   −1.5 % to +1.9 % for V05n16 and V06e) are uncontrolled confounds.
4. **The residual drop is about 3 orders**, against the ≥ 4 orders required
   (`cfd_campaign/*/residuals_*.csv`).
5. **There are no prism layers.** Blade y⁺ is high: the node-based median is about 430–440 and more than 90 % of
   blade nodes are above 300 (`cfd_campaign/*/blade_yplus_node_statistics_*.json`). The wall treatment is
   therefore outside its intended range, and separation onset and skin-friction drag are not resolved.
6. **Gate G2 was not achieved.** The criteria are mesh independence, the residual drop, stationarity and the y⁺
   requirement. **No CFD number in this repository is validated performance.** The numbers are recorded CFD
   observations from an investigative campaign.

## Physical validation

7. **No experimental or published-benchmark comparison exists** for this operating regime: compressible, axial
   flight, supersonic helical tip Mach. No CFD result has been physically validated.

## Models

8. **BEM is a reference design model only.** It is not a CFD validation or a performance prediction, and it is
   never at matched thrust with the CFD (the CFD reached 22–45 % of design thrust). Its section-drag model is a
   closed-form NACA 4-digit estimate, while the CFD sections from V05n16 on are NACA 16-series.
9. **The design sweep law over-credits Mach relief.** It uses the flat-wing relation M_n = M·cos Λ; for a
   circumferentially swept blade the actual relief is smaller, and the analysed sections operate above their own
   critical Mach at the design condition (the design audits in the unpublished-evidence register).
10. **Sectional quantities are inferred.** Section lift and drag come from a blade-element inversion of the CFD
    surface data, not from direct measurement. The polars for V04cf, V05n16 and V06e use a zero-induction basis
    that was later found to be defective and has not been regenerated for those cases. Absolute incidence carries
    about ±1° uncertainty from the blade-angle reference used.

## Geometry used in CFD

11. **The CFD blades are separate CFD geometries, not PRIME.** (V03 to V05n16 keep PRIME's design table; V06e onward
    use the v06-family table.) The trailing edge was thickened for meshing, and the
    CAD thickness does not equal the meshed thickness: CAD 0.012c meshed as 0.0161c–0.0212c depending on the case
    ([`cad/README.md`](cad/README.md)). PRIME's own 0.006c edge could not be volume-meshed (V09, V13), and 0.008c
    meshed but the solve diverged (V09b).
12. **The CFD blade wets r = 0.565–1.725 m** against a design span of 0.490–1.750 m, so thrust and torque are each
    about 3 % low.
13. **The camber-side error found in V03 also exists in PRIME** (same section-placement code). PRIME has not been
    corrected; it is kept unchanged as the record of the design as built.

## Case-specific interpretation limits

14. **V10:** the pre-registered mechanism test (sectional drag must fall) was **not performed**, because
    sectional data were not exported. The prediction failed; the mechanism was neither confirmed nor falsified.
15. **V12:** the mesh has +9.1 % cells and a different meshed trailing edge (0.0212c vs 0.0188c). The result is
    not a clean single-variable comparison.
16. **V15:** the conclusion about the root is limited. The incidence change was measured at one station, over
    one small blade-angle change, and the only lift-slope estimate is a single two-point difference. It argues
    against a stalled root at r/R 0.40 but does not establish what correction the root needs. The
    opposite-sign experiment (V16) was not solved.
17. **V11** is a 1000 rpm off-design case with two coupled changes (speed and twist). It is not a design-RPM
    result and is not comparable with the design-RPM cases.
18. **V14** is a boundary-condition diagnostic on the V08 case, not a design.
19. **V13 and V16 have no CFD result.**

## Structural work

20. **The FEA is screening only.**
    - Loads were partly assumed (a centrifugal load from an earlier sizing step) and allowables were provisional.
    - The governing stresses in Stages 18 and 19 were not mesh-converged.
    - The full-rotor model (Stage 20) did not close its global moment balance.
    - Stages 24 and 26 were benchmarks on disposable test blocks, not design evidence.
    - No structural validation, fatigue, flutter or bird-strike analysis exists.
    ([`structural/README.md`](structural/README.md))
21. **The CAD lock is a geometry and assembly lock.** It is not a structural or manufacturing validation. The
    drawings are reference drawings, not for manufacture.

## Reproducibility

22. **Some inputs and records are not in this repository.** The mesh, case and solution files are too large to
    publish (0.12–0.20 GB each). Solver logs and field exports are summarised as derived files, and some records
    are identified only by hash. See [`reproducibility/REPRODUCE.md`](reproducibility/REPRODUCE.md).
