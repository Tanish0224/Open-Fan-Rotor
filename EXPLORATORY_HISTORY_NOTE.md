# A note on what this repository does and does not include

This repository is a curated subset of a larger working project history. Alongside the
first-principles design, verified CAD, and verified CFD-preprocessing content included here, the
full project history also contains roughly 19 MB of raw ANSYS Fluent Meshing exploration —
numbered trial journals, raw session transcripts, process-cleanup scripts, and TUI-prompt
discovery probes generated while working out the correct boundary-zone classification and
periodic-pairing procedure — plus a similar set of undirected CAD loft-geometry debugging probes.
That raw material is not included here because publishing dozens of intermediate trial files
would bury the actual result, not reinforce it.

What **is** included in full is the *outcome* of that debugging: the one working, reproducible
Fluent journal (`03_cfd/setup/boundary_zone_setup.jou`) that regenerates the verified boundary
mesh end-to-end, and the complete CAD failure-and-recovery story — the first construction attempt
that failed its own verification gate, the root-cause diagnosis, and the corrected, independently
re-verified master — in `02_cad/failure_history/` and `02_cad/CAD_CHECK2_DIAGNOSTIC.md`. Nothing
about the debugging process is hidden; only the raw trial-and-error volume is left out.
