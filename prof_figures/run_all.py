# Runs every figure script in this folder. From the repository root: python3 prof_figures/run_all.py
import os, glob, runpy, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
for f in sorted(glob.glob(os.path.join(here, 'fig*.py'))):
    print('\n=== ' + os.path.basename(f))
    runpy.run_path(f, run_name='__main__')
