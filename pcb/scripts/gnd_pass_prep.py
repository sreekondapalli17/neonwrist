# Step A: fix fab rules and get ready for a second Freerouting pass that routes GND.
import pcbnew
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; ds = B.GetDesignSettings(); out = []
for name, val in [('m_TrackMinWidth', 0.1), ('m_ViasMinSize', 0.4), ('m_MinThroughDrill', 0.2),
                  ('m_ViasMinAnnularWidth', 0.1), ('m_HoleClearance', 0.2), ('m_HoleToHoleMin', 0.25)]:
    try: setattr(ds, name, mm(val)); out.append('%s = %.2f mm' % (name, val))
    except Exception as e: out.append('could not set %s: %s' % (name, e))
try:
    ds.m_NetSettings.GetNetclassByName('Power').SetTrackWidth(mm(0.3)); out.append('Power tracks 0.3 mm')
except Exception as e:
    out.append('Power width unchanged: %s' % e)
n = 0
for z in list(B.Zones()):
    if not z.GetIsRuleArea() and z.GetNetname().endswith('GND'):
        B.Remove(z); n += 1
out.append('removed %d GND zone(s) so Freerouting routes GND as normal tracks' % n)
pcbnew.Refresh(); print('\n'.join(out)); print('Now run Freerouting again.')
