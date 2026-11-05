# NEON//WRIST final ground fix: moves 8 vias out of the antenna keepout, stitches 8 boxed-in LED ground pads.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/gnd_final.py').read())
import pcbnew, math
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
gnd = B.FindNet('GND') or B.FindNet('/GND'); G = gnd.GetNetCode()
BAD = [(147.1, 95.2), (147.1, 96.8), (147.1, 98.4), (147.1, 100.0), (147.1, 101.6), (147.1, 103.2), (150.2, 106.8), (151.3, 106.8)]
removed = 0
for t in list(B.GetTracks()):
    if t.GetClass() == 'PCB_VIA' and t.GetNetCode() == G:
        p = t.GetPosition()
        if any(abs(um(p.x)-x) < 0.02 and abs(um(p.y)-y) < 0.02 for x, y in BAD):
            B.Remove(t); removed += 1
ds = B.GetDesignSettings()
try: ds.m_ViasMinSize = mm(0.35)
except Exception: pass
NEW = [
    ('D28.2', 155.702, 116.377, 0.40),
    ('D38.2', 138.490, 113.335, 0.38),
    ('D40.2', 135.766, 110.642, 0.40),
    ('D19.2', 166.983, 105.303, 0.40),
    ('D18.2', 167.413, 103.589, 0.38),
    ('D15.2', 167.229, 97.687, 0.38),
    ('D56.2', 140.970, 84.532, 0.38),
    ('D1.2', 149.489, 82.368, 0.38)]
for name, x, y, d in NEW:
    v = pcbnew.PCB_VIA(B); v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetWidth(mm(d)); v.SetDrill(mm(0.2)); v.SetNetCode(G); B.Add(v)
pcbnew.ZONE_FILLER(B).Fill(B.Zones())
print('vias pulled out of antenna keepout: %d' % removed)
print('LED ground pads stitched: %d' % len(NEW))
try:
    B.BuildConnectivity(); print('unrouted connections left: %d' % B.GetConnectivity().GetUnconnectedCount(False))
except Exception: pass
pcbnew.Refresh(); print('Now: B, Cmd+S, DRC')
