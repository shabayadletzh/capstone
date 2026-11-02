# Unzips raw/*.gz and data/*/*.csv.gz next to themselves so every script can read them.
# Run once from the repository root: python3 scripts/unpack_raw.py
import glob, gzip, os, shutil
for gz in sorted(glob.glob('raw/*.gz') + glob.glob('data/*/*.csv.gz')):
    out = gz[:-3]
    if os.path.exists(out): continue
    with gzip.open(gz, 'rb') as f, open(out, 'wb') as g: shutil.copyfileobj(f, g)
    print('unpacked', out)
