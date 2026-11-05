# NEON//WRIST ground islands: delete dead copper scraps, stitch every leftover GND island with a via.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/gnd_islands.py').read())
import pcbnew, math
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
CX, CY = 150.0, 100.0
out = []
gnd = B.FindNet('GND') or B.FindNet('/GND'); G = gnd.GetNetCode()
zones = [z for z in B.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == G]
filler = pcbnew.ZONE_FILLER(B)
for z in zones:
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
filler.Fill(B.Zones())
out.append('dead copper scraps removed')

VR, VD, CL = 0.225, 0.2, 0.12
rules = [z for z in B.Zones() if z.GetIsRuleArea()]
def collect():
    segs, boxes, gpts = [], [], []
    for t in B.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            p = t.GetPosition(); r = um(t.GetWidth())/2
            if t.GetNetCode() == G: gpts.append(p)
            else: boxes.append((um(p.x)-r, um(p.y)-r, um(p.x)+r, um(p.y)+r))
        elif t.GetNetCode() != G:
            a, b = t.GetStart(), t.GetEnd(); segs.append((um(a.x), um(a.y), um(b.x), um(b.y), um(t.GetWidth())/2))
    for f in B.GetFootprints():
        for p in f.Pads():
            if p.GetNetCode() == G:
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH: gpts.append(p.GetPosition())
            else:
                bb = p.GetBoundingBox(); boxes.append((um(bb.GetLeft()), um(bb.GetTop()), um(bb.GetRight()), um(bb.GetBottom())))
    return segs, boxes, gpts
def segdist(px, py, s):
    x1, y1, x2, y2, w = s; dx, dy = x2-x1, y2-y1; L = dx*dx+dy*dy
    u = 0 if L == 0 else max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/L))
    return math.hypot(px-(x1+u*dx), py-(y1+u*dy)) - w
def free(px, py, segs, boxes):
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
def inside(poly, i, px, py, m):
    for dx, dy in ((0, 0), (m, 0), (-m, 0), (0, m), (0, -m)):
        if not poly.Contains(pcbnew.VECTOR2I(mm(px+dx), mm(py+dy)), i): return False
    return True
def other_fill(layer, px, py):
    v = pcbnew.VECTOR2I(mm(px), mm(py))
    return any(z.GetLayer() != layer and z.HitTestFilledArea(z.GetLayer(), v) for z in zones)

total = 0
for rnd in range(3):
    segs, boxes, gpts = collect(); added = 0
    for z in zones:
        layer = z.GetLayer(); poly = z.GetFilledPolysList(layer)
        for i in range(poly.OutlineCount()):
            if any(poly.Contains(p, i) for p in gpts): continue
            bb = poly.Outline(i).BBox()
            x0, y0, x1, y1 = um(bb.GetLeft()), um(bb.GetTop()), um(bb.GetRight()), um(bb.GetBottom())
            best = None; y = y0
            while y <= y1 and best is None:
                x = x0
                while x <= x1:
                    if inside(poly, i, x, y, VR) and free(x, y, segs, boxes) and other_fill(layer, x, y):
                        best = (x, y); break
                    x += 0.15
                y += 0.15
            if best:
                x, y = best
                v = pcbnew.PCB_VIA(B); v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                v.SetWidth(mm(2*VR)); v.SetDrill(mm(VD)); v.SetNetCode(G); B.Add(v)
                gpts.append(v.GetPosition()); boxes.append((x-VR, y-VR, x+VR, y+VR)); added += 1
    if not added: break
    total += added; filler.Fill(B.Zones())
out.append('stitching vias added to loose GND islands: %d' % total)
try:
    B.BuildConnectivity(); out.append('unrouted connections left: %d' % B.GetConnectivity().GetUnconnectedCount(False))
except Exception: pass
pcbnew.Refresh(); print('\n'.join(out)); print('Now: B, Cmd+S, DRC')
