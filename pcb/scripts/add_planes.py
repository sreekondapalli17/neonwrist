# Step B: after the second Freerouting pass, add GND copper everywhere it fits.
import pcbnew, math
B = pcbnew.GetBoard(); mm = pcbnew.FromMM
CX, CY, R = 150.0, 100.0, 20.7
gnd = B.FindNet('GND') or B.FindNet('/GND')
for z in list(B.Zones()):
    if not z.GetIsRuleArea() and z.GetNetname().endswith('GND'): B.Remove(z)
for layer in (pcbnew.In1_Cu, pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(B); z.SetLayer(layer); z.SetNetCode(gnd.GetNetCode())
    pts = [pcbnew.VECTOR2I(mm(CX + R*math.cos(math.radians(a))), mm(CY + R*math.sin(math.radians(a)))) for a in range(0, 360, 5)]
    z.AppendCorner(pts[0], -1)
    for p in pts[1:]: z.AppendCorner(p, 0)
    z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(0.2))
    try: z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    except Exception: pass
    try: z.SetAssignedPriority(1 if layer == pcbnew.In1_Cu else 0)
    except Exception: pass
    B.Add(z)
pcbnew.ZONE_FILLER(B).Fill(B.Zones()); pcbnew.Refresh()
print('GND copper added on In1, F.Cu and B.Cu and filled. Save, then run DRC.')
