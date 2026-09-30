# Lessons learned

1. **Check the built geometry against the design intent, not only against the build script.** Both geometry
   errors in this project passed their own CAD checks: the sweep built as rake (v02), and the camber on the wrong
   side of the chord (v03). Each was found only by measuring the built geometry against what the design meant.
2. **A mesh can pass volume and connectivity checks and still be unusable.** The first 360° mesh diverged because
   of degenerate surface cells. Mesh quality has to be measured before any force is trusted.
3. **A convergence verdict depends on the window.** All design-RPM cases fail the full second-order history
   window. All of them except V10 pass the five-checkpoint window. Both are reported.
4. **Write the prediction before the run.** The three experiments around V08 each missed the prediction written
   down beforehand, and that is what made them informative. V10 also shows the cost of not exporting the data
   needed to test a mechanism: the prediction failed, but the mechanism was never checked.
5. **The CAD value is not the meshed value.** Across cases that share the same 0.012c trailing-edge parameter, the
   meshed trailing edge differed by up to 0.009c from the CAD value. PRIME's own trailing edge could not be
   meshed at all.
