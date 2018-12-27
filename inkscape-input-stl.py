#! /usr/bin/python 
#
# inkscape-input-stl.py
# (C) 2018 juergen@fabmail.org, distribute under GPLv2 or ask
#
# This is an input extension for inkscape to read STL files.
#
# Requires: (python-lxml | python3-lxml), slic3r
# For optional(!) rotation support:
#   Requires: (python-numpy-stl | python3-numpy-stl)
#   If you get ImportError: cannot import name 'mesh'
#   although an stl module is installed, then you have the wrong stl module.
#   Try 'pip3 uninstall stl; pip3 install numpy-stl'
#
# 2018-12-22 jw, v0.1 Initial draught
#                v0.1 First working standalone tool.
# 2018-12-26 jw, v0.3 Mesh rotation support via numpy-stl. Fully optional.

from __future__ import print_function
import sys, os, re, argparse
import subprocess
from lxml import etree

_version = '0.3'

sys_platform = sys.platform.lower()
if sys_platform.startswith('win'):
  slic3r = 'slic3r-console.exe'
elif sys_platform.startswith('darwin'):
  slic3r = 'slic3r'
else:   # Linux
  slic3r = os.environ['HOME']+ '/Downloads/Slic3r-1.3.0-x86_64.AppImage'
  if not os.path.exists(slic3r):
    slic3r = 'slic3r'

parser = argparse.ArgumentParser(description='convert an STL file to a nice SVG for inkscape. The STL object is projected onto the X-Y plane.')
parser.add_argument('--layer-height', '-l', default=None, help='slic3r layer height, probably in mm. Default: per slic3r config')
parser.add_argument('--rx', default=None, help='Rotate STL object around X-Axis before importing.')
parser.add_argument('--ry', default=None, help='Rotate STL object around Y-Axis before importing.')
parser.add_argument('--slic3r-cmd', '-s', default=slic3r, help='Command to invoke slic3r. Default is "'+slic3r+'"')
parser.add_argument('--output', '-o', default=None, help='SVG output file name. Default: name derived from STL input.') 
parser.add_argument('stlfile', type=str, help='STL input file to convert to SVG with the samename, but ".svg" suffix.');

args = parser.parse_args()

if sys_platform.startswith('win'):
  # assert we run the commandline version of slic3r
  args.slic3r_cmd = re.sub('slic3r(\.exe)?$', 'slic3r-console.exe', args.slic3r_cmd, flags=re.I)

stlfile = args.stlfile
tmpstlfile = None

if args.rx or args.ry:
  try:
    import tempfile
    import numpy, stl, math

    mesh = stl.Mesh.from_file(stlfile)
    if args.rx: mesh.rotate([1.0, 0.0, 0.0], math.radians(float(args.rx)))
    if args.ry: mesh.rotate([1.0, 0.0, 0.0], math.radians(float(args.ry)))
    stlfile = tmpstlfile = tempfile.gettempdir() + os.path.sep + 'ink-stl-' + str(os.getpid()) + '.stl'
    mesh.save(stlfile)
  except Exception as e:
    print("Rotate failed: " + str(e), file=sys.stderr)

svgfile = re.sub('\.stl', '.svg', args.stlfile, flags=re.IGNORECASE)
if args.output is not None: svgfile = args.output

cmd = [args.slic3r_cmd, '--no-gui']
if args.layer_height is not None:
  cmd += ['--layer-height', args.layer_height, '--first-layer-height', args.layer_height+'mm']
cmd += ['--export-svg', '-o', svgfile, stlfile]

try:
  tty = open("/dev/tty", "w")
except:
  tty = subprocess.PIPE

try:
  proc = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except OSError as e:
  raise OSError("{0} failed: errno={1} {2}".format(' '.join(cmd), e.errno, e.strerror))
stdout, stderr = proc.communicate()

if tmpstlfile and os.path.exists(tmpstlfile):
  os.unlink(tmpstlfile)

if not b'Done.' in stdout:
  print("Command failed: {0}".format(' '.join(cmd)))
  print("OUT: " + str(stdout), file=sys.stderr)
  print("ERR: " + str(stderr), file=sys.stderr)
  sys.exit(1)

# slic3r produces correct svg files, but with polygons instead of paths, and with undefined strokes.
# When opened with inkscape, most lines are invisible and polygons cannot be edited.
# To fix these issues, we postprocess the svg file:
# * replace polygon nodes with corresponding path nodes.
# * replace style attribute in polygon nodes with one that has a black stroke

stream = open(svgfile, 'r')
p = etree.XMLParser(huge_tree=True)
doc = etree.parse(stream, parser=p)
stream.close()

## To change the document units to mm, insert directly after the root node:
# e.tag = '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview'
# e.attrib['id'] = "base"
# e.attrib['{http://www.inkscape.org/namespaces/inkscape}document-units'] = "mm"

layercount = 0
for e in doc.iterfind('//{*}g'):
  if e.attrib['{http://slic3r.org/namespaces/slic3r}z'] and e.attrib['id']:
    e.attrib['{http://www.inkscape.org/namespaces/inkscape}label'] = e.attrib['id'] + ' slic3r:z=' + e.attrib['{http://slic3r.org/namespaces/slic3r}z']
    layercount+=1

polygoncount = 0
for e in doc.iterfind('//{*}polygon'):
  # e.tag = '{http://www.w3.org/2000/svg}polygon'
  # e.attrib = {'{http://slic3r.org/namespaces/slic3r}type': 'contour', 'points': '276.422496,309.4 260.209984,309.4 260.209984,209.03 276.422496,209.03', 'style': 'fill: white'}
  e.tag = re.sub('polygon$', 'path', e.tag)
  polygoncount += 1
  e.attrib['id'] = 'polygon%d' % polygoncount
  e.attrib['{http://www.inkscape.org/namespaces/inkscape}connector-curvature'] = '0'
  e.attrib['style'] = 'fill:none;fill-opacity:1;stroke:#000000;stroke-opacity:1'        # ;stroke-width:0.1'
  e.attrib['d'] = 'M ' + re.sub(' ', ' L ', e.attrib['points']) + ' Z'
  del e.attrib['points']

print("{0}: {1} polygons in {2} layers converted to paths.".format(svgfile, polygoncount, layercount), file=sys.stderr)
doc.write(svgfile, pretty_print=True)

