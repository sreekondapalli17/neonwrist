# NEON//WRIST ground fix-up: solid pad connections + a ground via next to every isolated GND pad.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/gnd_fixup.py').read())
import pcbnew, math
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
CX, CY = 150.0, 100.0
out = []
gnd = B.FindNet('GND') or B.FindNet('/GND'); G = gnd.GetNetCode()
zones = [z for z in B.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == G]
for z in zones:
    try: z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    except Exception as e: out.append('pad connection: %s' % e)
    try: z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
    except Exception as e: out.append('island mode: %s' % e)
    z.SetMinThickness(mm(0.12))
filler = pcbnew.ZONE_FILLER(B); filler.Fill(B.Zones())
out.append('GND pads now connect solid to the copper (no thin spokes)')

VR, VD, CL = 0.225, 0.2, 0.12
segs, boxes, rules, gvias = [], [], [], []
for t in B.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        p = t.GetPosition(); r = um(t.GetWidth())/2
        boxes.append((um(p.x)-r, um(p.y)-r, um(p.x)+r, um(p.y)+r))
        if t.GetNetCode() == G: gvias.append((um(p.x), um(p.y)))
    elif t.GetNetCode() != G:
        a, b = t.GetStart(), t.GetEnd(); segs.append((um(a.x), um(a.y), um(b.x), um(b.y), um(t.GetWidth())/2))
gpads = []
for f in B.GetFootprints():
    for p in f.Pads():
        bb = p.GetBoundingBox(); box = (um(bb.GetLeft()), um(bb.GetTop()), um(bb.GetRight()), um(bb.GetBottom()))
        if p.GetNetCode() == G: gpads.append(p)
        else: boxes.append(box)
for z in B.Zones():
    if z.GetIsRuleArea(): rules.append(z)
zIn = [z for z in zones if z.GetLayer() == pcbnew.In1_Cu]
def segdist(px, py, s):
    x1, y1, x2, y2, w = s; dx, dy = x2-x1, y2-y1; L = dx*dx+dy*dy
    u = 0 if L == 0 else max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/L))
    return math.hypot(px-(x1+u*dx), py-(y1+u*dy)) - w
def free(px, py):
    if math.hypot(px-CX, py-CY) > 19.5: return False
    v = pcbnew.VECTOR2I(mm(px), mm(py))
    for z in rules:
        try:
            if z.GetDoNotAllowVias() and z.Outline().Contains(v): return False
        except Exception: pass
    for (l, t, r, b) in boxes:
        if px > l-VR-CL and px < r+VR+CL and py > t-VR-CL and py < b+VR+CL: return False
    for s in segs:
        if min(abs(px-s[0]), abs(px-s[2])) < 8 and segdist(px, py, s) < VR+CL: return False
    return True
def on_copper(layer, px, py):
    v = pcbnew.VECTOR2I(mm(px), mm(py))
    return any(z.GetLayer() == layer and z.HitTestFilledArea(layer, v) for z in zones)
added = 0
for p in gpads:
    c = p.GetPosition(); cx, cy = um(c.x), um(c.y)
    if any(math.hypot(cx-a, cy-b) < 1.3 for a, b in gvias): continue
    layer = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    done = False
    for r10 in range(5, 22, 2):
        r = r10/10.0
        for k in range(24):
            a = 2*math.pi*k/24; x, y = cx + r*math.cos(a), cy + r*math.sin(a)
            if free(x, y) and on_copper(layer, x, y) and any(z.HitTestFilledArea(pcbnew.In1_Cu, pcbnew.VECTOR2I(mm(x), mm(y))) for z in zIn):
                v = pcbnew.PCB_VIA(B); v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                v.SetWidth(mm(2*VR)); v.SetDrill(mm(VD)); v.SetNetCode(G); B.Add(v)
                boxes.append((x-VR, y-VR, x+VR, y+VR)); gvias.append((x, y)); added += 1; done = True; break
        if done: break
filler.Fill(B.Zones())
out.append('ground vias added next to pads: %d' % added)
try:
    B.BuildConnectivity(); out.append('unrouted connections left: %d' % B.GetConnectivity().GetUnconnectedCount(False))
except Exception: pass
pcbnew.Refresh(); print('\n'.join(out)); print('Now: B, Cmd+S, DRC')
