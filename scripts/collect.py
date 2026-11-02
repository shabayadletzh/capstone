import json,glob,re,os,sys
# Scan tool-result files, decode JS return values, find chunk markers "<<CHUNK[:tag] i>>\n...\n<<END>>"
D='/root/.claude/projects/-home-claude/b995b695-eaf3-53dc-b78a-df65cf0b6294/tool-results/'
def decode(f):
    try: d=json.load(open(f))
    except Exception: return None
    if isinstance(d,list):
        t=''.join(x.get('text','') for x in d if isinstance(x,dict))
    else: return None
    if 'truncated: content too large' in t: print('TRUNCATED',f,file=sys.stderr)
    i=t.find('"'); 
    # JS string result is JSON-encoded at start
    s=t
    m=t.rfind('\n\n(captured at origin')
    if m>0: s=t[:m]
    m=s.rfind('\n\nTab Context:')
    if m>0: s=s[:m]
    try: return json.loads(s)
    except Exception:
        try: return json.loads(s.strip())
        except Exception: return s
def chunks(tag):
    out={}
    pat=re.compile(r'<<CHUNK'+(':'+re.escape(tag) if tag else '')+r' (\d+)>>\n(.*?)\n<<END>>',re.S)
    for f in sorted(glob.glob(D+'*')):
        v=decode(f)
        if not isinstance(v,str): continue
        for m in pat.finditer(v): out[int(m.group(1))]=m.group(2)
    return out
if __name__=='__main__':
    tag=sys.argv[1] if sys.argv[1]!='-' else ''
    c=chunks(tag); n=int(sys.argv[3]) if len(sys.argv)>3 else None
    ks=sorted(c); print('chunks',ks[:3],'...',ks[-3:],len(ks),file=sys.stderr)
    if n is not None:
        miss=[i for i in range(n) if i not in c]; print('missing',miss,file=sys.stderr)
    open(sys.argv[2],'w').write(''.join(c[k] for k in ks))
