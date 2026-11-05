# NEON//WRIST: removes dead-end trace stubs and a loose via, bumps the MK-II logo text to the 0.8 mm minimum.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/stub_clean.py').read())
import pcbnew
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
NETS = set()
for n in ('/BOOST_SW', 'BOOST_SW', '/5V_LED', '5V_LED'):
    ni = B.FindNet(n)
    if ni: NETS.add(ni.GetNetCode())
key = lambda p: (round(um(p.x), 3), round(um(p.y), 3))
removed = 0
for t in list(B.GetTracks()):
    if t.GetClass() == 'PCB_VIA' and t.GetNetCode() in NETS:
        p = t.GetPosition()
        if abs(um(p.x)-159.592) < 0.01 and abs(um(p.y)-88.6819) < 0.01: B.Remove(t); removed += 1
pads = [p for f in B.GetFootprints() for p in f.Pads() if p.GetNetCode() in NETS]
for _ in range(30):
    segs = [t for t in B.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetNetCode() in NETS]
    vias = [t for t in B.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetCode() in NETS]
    cnt = {}
    for s in segs:
        for p in (s.GetStart(), s.GetEnd()): k = (key(p), s.GetLayer(), s.GetNetCode()); cnt[k] = cnt.get(k, 0) + 1
    def anchored(s, p):
        if cnt[(key(p), s.GetLayer(), s.GetNetCode())] > 1: return True
        for v in vias:
            if v.GetNetCode() == s.GetNetCode() and abs(um(v.GetPosition().x-p.x)) < 0.01 and abs(um(v.GetPosition().y-p.y)) < 0.01: return True
        for pd in pads:
            if pd.GetNetCode() == s.GetNetCode() and pd.IsOnLayer(s.GetLayer()) and pd.HitTest(p): return True
        for o in segs:
            if o is not s and o.GetNetCode() == s.GetNetCode() and o.GetLayer() == s.GetLayer() and o.HitTest(p): return True
        return False
    dead = [s for s in segs if not (anchored(s, s.GetStart()) and anchored(s, s.GetEnd()))]
    if not dead: break
    for s in dead: B.Remove(s); removed += 1
for d in B.GetDrawings():
    if d.GetClass() == 'PCB_TEXT' and d.GetText() == 'MK-II':
        d.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); d.SetTextThickness(mm(0.13))
pcbnew.ZONE_FILLER(B).Fill(B.Zones())
B.BuildConnectivity()
print('dead stubs/vias removed: %d' % removed)
print('unrouted connections: %d' % B.GetConnectivity().GetUnconnectedCount(False))
pcbnew.Refresh(); print('Now: B, Cmd+S, DRC')
