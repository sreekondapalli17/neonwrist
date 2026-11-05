# NEON//WRIST routing prep. Run in PCB Editor > Tools > Scripting Console:
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/prep_routing.py').read())
import pcbnew, math
B = pcbnew.GetBoard(); mm = pcbnew.FromMM
CX, CY, R = 150.0, 100.0, 20.7
out = []

# 1) wider tracks for power nets
POWER = ['GND', 'VBUS', 'VBAT', 'SYS', '3V3', '5V_LED', 'BOOST_SW']
ds = B.GetDesignSettings(); ns = ds.m_NetSettings
try:
    nc = pcbnew.NETCLASS('Power'); nc.SetTrackWidth(mm(0.4)); nc.SetClearance(mm(0.15))
    nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))
    try: ns.SetNetclass('Power', nc)
    except Exception: ns.m_NetClasses['Power'] = nc
    for n in POWER:
        try: ns.SetNetclassPatternAssignment(n, 'Power')
        except Exception: ns.m_NetClassPatternAssignments.append((pcbnew.EDA_COMBINED_MATCHER(n, pcbnew.CTX_NETCLASS), 'Power'))
    out.append('Power net class: 0.4 mm tracks on ' + ', '.join(POWER))
except Exception as e:
    out.append('Power net class FAILED (%s). Do it by hand: Board Setup > Net Classes > add "Power", 0.4 mm track, assign GND VBUS VBAT SYS 3V3 5V_LED BOOST_SW' % e)
try:
    dn = ns.GetDefaultNetclass(); dn.SetViaDiameter(mm(0.45)); dn.SetViaDrill(mm(0.2))
    out.append('Default vias: 0.45 mm pad, 0.2 mm drill')
except Exception as e:
    out.append('via size not set: %s' % e)

# 2) solid GND plane on inner layer 1 (antenna keepout is cut out automatically)
gnd = B.FindNet('GND') or B.FindNet('/GND')
for z in list(B.Zones()):
    if z.GetLayer() == pcbnew.In1_Cu: B.Remove(z)
z = pcbnew.ZONE(B); z.SetLayer(pcbnew.In1_Cu); z.SetNetCode(gnd.GetNetCode())
pts = [pcbnew.VECTOR2I(mm(CX + R*math.cos(math.radians(a))), mm(CY + R*math.sin(math.radians(a)))) for a in range(0, 360, 5)]
z.AppendCorner(pts[0], -1)
for p in pts[1:]: z.AppendCorner(p, -1)
try: z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
except Exception: pass
z.SetMinThickness(mm(0.2)); B.Add(z)
pcbnew.ZONE_FILLER(B).Fill(B.Zones())
out.append('GND plane on In1.Cu added and filled')

# 3) export for the autorouter
path = '/Users/sreevardhankondapalli/neonwrist/pcb/neonwrist/neonwrist.dsn'
try:
    ok = pcbnew.ExportSpecctraDSN(B, path)
except TypeError:
    ok = pcbnew.ExportSpecctraDSN(path)
out.append('DSN exported: %s (%s)' % (path, ok))
pcbnew.Refresh()
print('\n'.join(out))
