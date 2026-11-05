# NEON//WRIST boost fix: places the new 5 V divider (R18 1M, R19 249k) next to U7 and clears room for routing.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/boost_fix.py').read())
import pcbnew, math
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
gnd = B.FindNet('GND') or B.FindNet('/GND'); G = gnd.GetNetCode()
out = []
def side_back(f):
    if f.IsFlipped(): return
    try: f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    except Exception: f.Flip(f.GetPosition(), False)
SPOTS = {'R18': (153.95, 92.45, 0), 'R19': (155.50, 92.45, 90)}
ok = True
for ref, (x, y, r) in SPOTS.items():
    f = B.FindFootprintByReference(ref)
    if f is None:
        out.append('%s missing: do Tools > Update PCB from Schematic (F8) first' % ref); ok = False; continue
    side_back(f)
    try: f.SetOrientationDegrees(r)
    except Exception: f.SetOrientation(pcbnew.EDA_ANGLE(r, pcbnew.DEGREES_T))
    f.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    for fld in (f.Reference(), f.Value()): fld.SetVisible(False)
    out.append('%s placed at (%.2f, %.2f)' % (ref, x, y))
if ok:
    ends = set()
    for t in B.GetTracks():
        if t.GetClass() != 'PCB_VIA':
            for p in (t.GetStart(), t.GetEnd()): ends.add((round(um(p.x), 2), round(um(p.y), 2)))
    killed = kept = 0
    for t in list(B.GetTracks()):
        if t.GetClass() == 'PCB_VIA' and t.GetNetCode() == G:
            p = t.GetPosition(); px, py = um(p.x), um(p.y)
            if 153.0 < px < 156.3 and 91.3 < py < 93.6:
                if (round(px, 2), round(py, 2)) in ends: kept += 1; continue
                B.Remove(t); killed += 1
    out.append('stitching vias cleared: %d (kept %d with traces)' % (killed, kept))
    pcbnew.ZONE_FILLER(B).Fill(B.Zones())
pcbnew.Refresh(); print('\n'.join(out)); print('Now: Cmd+S, then run Freerouting')
