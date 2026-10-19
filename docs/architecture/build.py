"""Build reviewed architecture snapshots into a new directory."""
from pathlib import Path
import argparse,shutil,subprocess
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True,help='New output directory; refuses overwrite')
a=p.parse_args()
if a.output.exists():p.error('Use a new output directory to preserve prior variants.')
a.output.mkdir(parents=True)
shutil.copyfile(ROOT/'spec.json',a.output/'deck.json')
node=shutil.which('node')
if not node:raise SystemExit('Install Node.js and the renderer dependencies first.')
subprocess.run([node,str(ROOT/'renderer/build.cjs'),str(a.output/'deck.json')],check=True)
