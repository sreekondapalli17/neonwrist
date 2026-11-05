# NEON//WRIST factory files: adds the face logo, then writes Gerbers + drill files and a JLCPCB-ready zip.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/fab_out.py').read())
import pcbnew, os, zipfile
B = pcbnew.GetBoard(); mm = pcbnew.FromMM
OUT = os.path.join(os.path.dirname(B.GetFileName()), '..', 'fab', 'gerbers')
OUT = os.path.abspath(OUT); os.makedirs(OUT, exist_ok=True)

# face logo, in the bare antenna window on the LED side
for d in list(B.GetDrawings()):
    if d.GetClass() == 'PCB_TEXT' and d.GetText() in ('NEON//WRIST', 'MK-II'):
        B.Remove(d)
def text(s, x, y, h, w):
    t = pcbnew.PCB_TEXT(B); t.SetText(s); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(w))
    t.SetTextAngle(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); B.Add(t)
text('NEON//WRIST', 149.6, 100.0, 1.1, 0.18)
text('MK-II', 151.4, 100.0, 0.8, 0.13)
pcbnew.Refresh()

pc = pcbnew.PLOT_CONTROLLER(B); po = pc.GetPlotOptions()
po.SetOutputDirectory(OUT); po.SetPlotFrameRef(False); po.SetUseAuxOrigin(False)
for name, arg in (('SetSubtractMaskFromSilk', True), ('SetUseGerberProtelExtensions', True),
                  ('SetCreateGerberJobFile', False), ('SetUseGerberX2format', False)):
    try: getattr(po, name)(arg)
    except Exception: pass
LAYERS = [(pcbnew.F_Cu, 'F_Cu'), (pcbnew.In1_Cu, 'In1_Cu'), (pcbnew.In2_Cu, 'In2_Cu'), (pcbnew.B_Cu, 'B_Cu'),
          (pcbnew.F_Mask, 'F_Mask'), (pcbnew.B_Mask, 'B_Mask'), (pcbnew.F_SilkS, 'F_Silkscreen'),
          (pcbnew.B_SilkS, 'B_Silkscreen'), (pcbnew.F_Paste, 'F_Paste'), (pcbnew.B_Paste, 'B_Paste'),
          (pcbnew.Edge_Cuts, 'Edge_Cuts')]
for layer, nm in LAYERS:
    pc.SetLayer(layer); pc.OpenPlotfile(nm, pcbnew.PLOT_FORMAT_GERBER, nm); pc.PlotLayer()
pc.ClosePlot()
ew = pcbnew.EXCELLON_WRITER(B)
ew.SetOptions(False, False, pcbnew.VECTOR2I(0, 0), False)
ew.SetFormat(True)
ew.CreateDrillandMapFilesSet(OUT, True, False)

files = [f for f in os.listdir(OUT) if not f.endswith('.zip')]
zp = os.path.join(OUT, '..', 'neonwrist_mk2_gerbers.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files: z.write(os.path.join(OUT, f), f)
print('logo added on the face')
print('files written: %d' % len(files)); print('zip: %s' % os.path.abspath(zp))
print('Now: Cmd+S')
