# NEON//WRIST finishing pass: fix thin tracks, add GND copper on 3 layers, stitch with vias.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/finish.py').read())
import pcbnew, math
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
CX, CY, RZ = 150.0, 100.0, 20.7
out = []
gnd = B.FindNet('GND') or B.FindNet('/GND'); G = gnd.GetNetCode()

# 1) no track thinner than 0.1 mm
n = 0
for t in B.GetTracks():
    if t.GetClass() == 'PCB_TRACK' and t.GetWidth() < mm(0.1):
        t.SetWidth(mm(0.1)); n += 1
out.append('widened %d thin track pieces to 0.1 mm' % n)

# 2) GND copper on In1, F.Cu, B.Cu
for z in list(B.Zones()):
    if not z.GetIsRuleArea() and z.GetNetCode() == G: B.Remove(z)
for layer in (pcbnew.In1_Cu, pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(B); z.SetLayer(layer); z.SetNetCode(G)
    pts = [pcbnew.VECTOR2I(mm(CX + RZ*math.cos(math.radians(a))), mm(CY + RZ*math.sin(math.radians(a)))) for a in range(0, 360, 5)]
    z.AppendCorner(pts[0], -1)
    for p in pts[1:]: z.AppendCorner(p, 0)
    z.SetMinThickness(mm(0.15)); z.SetLocalClearance(mm(0.15))
    try: z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    except Exception: pass
    B.Add(z)
filler = pcbnew.ZONE_FILLER(B); filler.Fill(B.Zones())
out.append('GND copper added on In1, F.Cu, B.Cu')

# 3) stitching vias wherever they fit
VR, VD, CL = 0.225, 0.2, 0.12           # via radius, drill, clearance (mm)
segs, boxes, rules = [], [], []
for t in B.GetTracks():
    if t.GetNetCode() == G: continue
    if t.GetClass() == 'PCB_VIA':
        p = t.GetPosition(); boxes.append((um(p.x)-um(t.GetWidth())/2, um(p.y)-um(t.GetWidth())/2, um(p.x)+um(t.GetWidth())/2, um(p.y)+um(t.GetWidth())/2))
    else:
        a, b = t.GetStart(), t.GetEnd(); segs.append((um(a.x), um(a.y), um(b.x), um(b.y), um(t.GetWidth())/2))
for f in B.GetFootprints():
    for p in f.Pads():
        if p.GetNetCode() == G and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD: continue
        bb = p.GetBoundingBox(); boxes.append((um(bb.GetLeft()), um(bb.GetTop()), um(bb.GetRight()), um(bb.GetBottom())))
for z in B.Zones():
    if z.GetIsRuleArea(): rules.append(z)
def segdist(px, py, s):
    x1, y1, x2, y2, w = s; dx, dy = x2-x1, y2-y1; L = dx*dx+dy*dy
    u = 0 if L == 0 else max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/L))
    return math.hypot(px-(x1+u*dx), py-(y1+u*dy)) - w
def free(px, py):
    if math.hypot(px-CX, py-CY) > RZ-1.2: return False
    v = pcbnew.VECTOR2I(mm(px), mm(py))
    for z in rules:
        try:
            if z.GetDoNotAllowVias() and z.Outline().Contains(v): return False
        except Exception: pass
    for (l, t, r, b) in boxes:
        if px > l-VR-CL and px < r+VR+CL and py > t-VR-CL and py < b+VR+CL: return False
    for s in segs:
        if abs(px-s[0]) < 6 or abs(px-s[2]) < 6:
            if segdist(px, py, s) < VR+CL: return False
    return True
added = []
step = 1.1
y = CY - RZ
while y <= CY + RZ:
    x = CX - RZ
    while x <= CX + RZ:
        if free(x, y) and all(math.hypot(x-a, y-b) > 1.0 for a, b in added):
            v = pcbnew.PCB_VIA(B); v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            v.SetWidth(mm(2*VR)); v.SetDrill(mm(VD)); v.SetNetCode(G); B.Add(v)
            added.append((x, y)); boxes.append((x-VR, y-VR, x+VR, y+VR))
        x += step
    y += step
filler.Fill(B.Zones())
# keep only vias that actually tie the inner plane to outer copper
kept = 0
zIn = [z for z in B.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == G and z.GetLayer() == pcbnew.In1_Cu]
zOut = [z for z in B.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == G and z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu)]
for t in list(B.GetTracks()):
    if t.GetClass() != 'PCB_VIA' or t.GetNetCode() != G: continue
    p = t.GetPosition()
    if any(abs(um(p.x)-a) < 0.001 and abs(um(p.y)-b) < 0.001 for a, b in added):   # only the vias this script added
        inner = any(z.HitTestFilledArea(pcbnew.In1_Cu, p) for z in zIn)
        outer = any(z.HitTestFilledArea(z.GetLayer(), p) for z in zOut)
        if inner and outer: kept += 1
        else: B.Remove(t)
filler.Fill(B.Zones())
out.append('stitching vias placed: %d' % kept)
try:
    B.BuildConnectivity(); out.append('unrouted connections left: %d' % B.GetConnectivity().GetUnconnectedCount(False))
except Exception as e:
    out.append('(run DRC to see what is left)')
pcbnew.Refresh(); print('\n'.join(out)); print('Now: Tools > Cleanup Tracks & Vias, Cmd+S, DRC')
