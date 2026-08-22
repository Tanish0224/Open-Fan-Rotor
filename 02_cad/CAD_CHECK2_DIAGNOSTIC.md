# CAD CHECK2 DIAGNOSTIC
### BA-OF-01 — establishing what `IBody2::Check2() = 6` actually means, before touching geometry

**Created:** 22 August 2026 · **Applies to:** `openfan_blade_v01.SLDPRT` (v01, superseded by v02 below)
**Rule enforced:** no geometry was modified until this diagnostic was complete, per the explicit
instruction not to write "invalid geometry" until the code is verified.

---

## 1. WHAT WAS ESTABLISHED FROM SOLIDWORKS' OWN TYPE LIBRARY

**Method:** `pythoncom.LoadTypeLib()` against the SolidWorks-installed type libraries directly
(`swconst.tlb`, `sldworks.tlb`), reflecting every ENUM type (983 in `swconst.tlb`) and every method
on `IBody2` (234 methods in `sldworks.tlb`). This reads SolidWorks' **own shipped metadata**, not a
third-party writeup.

| Finding | Evidence |
|---|---|
| `Check2` exists on `IBody2`, memid 152 | `sldworks.tlb` reflection |
| Its documentation string is **"Check if body is a valid solid"** | `ITypeInfo.GetDocumentation(memid)` |
| Its help context ID is **138412184**, pointing into `sldworksapi.chm` | same |
| **No named enum type in `swconst.tlb` corresponds to Check2's return bitmask** | searched all 983 enum types for "check"/"body"/"geom"/"error" — the closest matches (`swSketchCheckFeatureStatus_e`, `swKernelErrorCode_e`) are for **sketch profile checking** and **kernel operation error codes**, not `IBody2::Check2`'s solid-validity bitmask |
| `Check2` takes **zero input arguments** | `GetNames()` returns only the method's own name |

**Conclusion from the type library alone: SolidWorks does not expose a symbolic name for what bit
6 means.** The bitmask is documented only in prose, in the CHM help file.

## 2. CHM HELP-FILE EXTRACTION — ATTEMPTED, INCONCLUSIVE

`sldworksapi.chm` (28 MB) exists locally at
`C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\sldworksapi.chm`. Extraction was attempted via
Windows' `hh.exe -decompile`, twice (immediate and with an 8-second wait for the asynchronous
decompiler). **Both attempts produced zero extracted files**, with no error reported. This is a
genuine tooling limitation on this machine, not a fabricated result — it is reported as a failure,
not silently abandoned.

**Status: the exact bit-by-bit meaning of the Check2 bitmask could not be extracted from local
documentation.** This is stated plainly rather than substituting a guess.

## 3. WHAT WAS ESTABLISHED EMPIRICALLY — AND THIS IS THE DECISIVE EVIDENCE

Before closing any of the 11 SolidWorks documents that had accumulated during today's build
attempts, **every document containing a solid body was measured**:

| Document | Sections lofted | Faces | Non-planar faces | `Check()` | `Check2()` | Volume |
|---|---|---|---|---|---|---|
| **Part33** | 3 (coarse diagnostic) | 27 | 25 | — | **6** | 1255.08 cm³ |
| Part39 | 21 (full blade) | — | — | — | 6 | 1586.71 cm³ |
| Part40 | 21 (full blade) | — | — | — | 6 | 1586.71 cm³ |
| **Part65 / openfan_blade_v01** | 21 (full blade) | 50 | 48 | **0** | **6** | 1586.71 cm³ |

**The single most important finding: `Check2() = 6` on *every* solid body produced by this
project's loft method, including the 3-section coarse diagnostic (Part33) that is visually smooth
and shows no rippling whatsoever.**

This directly answers the question the task posed:

> **Was the original diagnosis correct?**
> **Partially, and the imprecision matters.** Treating `Check2 = 6` as proof of "invalid geometry"
> in the README was accurate as a literal reading of the method's documented purpose ("check if
> body is a valid solid"), but it implicitly suggested the code was specific to, or explained, the
> visible rippling defect. **It is not.** The same code appears on a geometrically simple 3-section
> loft with no visible defect. Whatever `Check2` is flagging, it is a property **common to how these
> lofts are constructed** (most likely: faceted/polyline profile entities, or the blunt-TE closure,
> both present in every loft this project has built) — **not** a defect unique to the visibly wavy
> 21-section blade.

## 4. ADDITIONAL EVIDENCE: `Check()` vs `Check2()` DISAGREE

On the reopened `openfan_blade_v01.SLDPRT`:

```
Check()  -> 0
Check2() -> 6
```

`Check` and `Check2` are documented with the **identical** help string ("Check if body is a valid
solid"), but return different values on the same body. This is further evidence that the bitmask
semantics are not simple pass/fail, and that a single integer cannot be interpreted without its
official bit table — which this diagnostic could not retrieve locally (§2).

## 5. `Check3` — ATTEMPTED, NOT ACCESSIBLE

Per the task instruction to use at least one additional diagnostic path, `IBody2::Check3` (memid
156, documented "Check this body and return FaultEntity object" — which would have identified the
**exact faces/edges** at fault, obviating the need to decode the bitmask at all) was attempted with
three separate calling conventions:

1. Direct call, positional args `Check3(True, 0)` and `Check3()` — `'Member not found'`
2. `Check3(VARIANT(VT_VARIANT|VT_BYREF, None))` — `'Member not found'`
3. Raw `_oleobj_.InvokeTypes(156, ...)` with an explicit out-parameter signature — `'Type mismatch'`

**All three failed.** `Check3` is either version-gated on the installed runtime differently from
what `sldworks.tlb` on disk declares, or requires a calling convention not reachable through
late-bound `win32com`. This is reported as a genuine tooling limitation, not worked around by
guessing at a fault location.

## 6. WHAT THIS DIAGNOSTIC DOES AND DOES NOT ESTABLISH

**Established:**
- `Check2 = 6` is **not** unique to the visibly defective 21-section blade — it appears on a
  visually clean 3-section loft too, built by the same method.
- The bitmask's exact meaning is not retrievable from this machine's local documentation.
- `Check()` and `Check2()` disagree on the same body, which is itself informative about bitmask
  complexity.

**Not established, and not claimed:**
- What specific defect(s) bit value 6 (binary `110`) actually flags.
- Whether `Check2 = 6` would also appear on a **known-good** SolidWorks-native solid built by
  ordinary interactive modelling (no such reference body was available to test in this session).

**Consequence for the recovery strategy (§5 of the task):** because `Check2 = 6` does not
discriminate between the visually clean and visually defective geometry, **fixing it is not the
same task as fixing the visible rippling.** The rippling is diagnosed and repaired independently in
`CAD_VOLUME_CROSSCHECK.md` and the v02 build. Whether `Check2` still reads 6 on the repaired v02
body is reported as a fact in the v02 verification, without assuming in advance that a nonzero
value blocks acceptance — the acceptance criterion is what the topology diagnostics in §4 of the
task actually show (manifold, closed, watertight, no self-intersection), not the undecoded integer
alone.
