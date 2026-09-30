"""
independent_extract.py -- INDEPENDENT extraction of T and Q straight from a Fluent
transcript, as an independent cross-check of the force extraction.

WHY IT EXISTS AND WHY IT IS INDEPENDENT
---------------------------------------
compute_performance.py is the project's primary extractor. Running a second wrapper
around the SAME parsing code would not be independent verification. This module was written from the raw transcript FORMAT alone and
deliberately does NOT import, call or consult compute_performance.py. It re-derives the
zone force and moment tables itself.

It was written during the v05 forensic audit and reproduced that run's
T = 4997.5534 N and Q = 16379.4400 N.m exactly from the transcript.

SIGN CONVENTION -- the trap this is designed to catch
-----------------------------------------------------
The rotor axis is -z and the flow is +z, so THRUST T = -F_z, taken over the BLADE zones
only. Fluent prints the Forces block FIRST and the Moments block SECOND; they are read
here BY HEADER, never by position, because a positional read silently swaps T and Q.

USAGE
    python independent_extract.py <fluent_transcript.trn|.log>

Prints every axial force/moment report block with its preceding MARK_, so a checkpoint
series can be audited one by one rather than trusting a single summary number.
"""
import re, sys, pathlib

def blocks(txt):
    """Yield (kind, marker_before, dict(zone -> (pres,visc,tot))) for each axial report."""
    lines = txt.splitlines()
    out = []
    last_mark = None
    i = 0
    while i < len(lines):
        L = lines[i]
        m = re.match(r'^MARK_(\S+)\s*$', L.strip())
        if m:
            last_mark = m.group(1)
        # axial force sub-table
        if L.startswith('Forces - Direction Vector (0 0 1)'):
            out.append(('F', last_mark, parse_table(lines, i)))
        if L.startswith('Moments - Moment Center (0 0 0) Moment Axis (0 0 1)'):
            out.append(('M', last_mark, parse_table(lines, i)))
        i += 1
    return out

def parse_table(lines, i):
    """Table layout: header, col-names, then zone rows, dashed rule, Net."""
    d = {}
    j = i + 2                       # skip the two header lines
    assert lines[j].lstrip().startswith('Zone'), lines[j]
    j += 1
    while j < len(lines):
        s = lines[j].rstrip()
        if not s.strip():
            break
        if s.startswith('---'):
            j += 1
            continue
        parts = s.split()
        if len(parts) >= 7:          # zone + 3 dimensional + 3 coefficients
            name = parts[0]
            try:
                d[name] = tuple(float(x) for x in parts[1:4])
            except ValueError:
                pass
            if name == 'Net':
                break
        j += 1
    return d

def main(path):
    txt = pathlib.Path(path).read_text(errors='ignore')
    bl = blocks(txt)
    print("transcript: %s" % pathlib.Path(path).name)
    print("axial report blocks found: %d force, %d moment"
          % (sum(1 for k, _, _ in bl if k == 'F'), sum(1 for k, _, _ in bl if k == 'M')))
    zones = sorted({z for _, _, d in bl for z in d})
    print("zones seen: %s" % ", ".join(zones))
    print()
    hdr = "%-10s %-6s | %12s %12s %12s | %12s" % (
        "mark", "kind", "blade_tot", "hub_tot", "hub008_tot", "NET_tot")
    print(hdr); print("-" * len(hdr))
    for kind, mark, d in bl:
        g = lambda z: d.get(z, (float('nan'),) * 3)[2]
        print("%-10s %-6s | %12.4f %12.4f %12.4f | %12.4f"
              % (mark, kind, g('blade'), g('hub'), g('hub:008'), g('Net')))

if __name__ == '__main__':
    main(sys.argv[1])
