import sys,base64,gzip
sys.path.insert(0,'/home/claude/capstone/scripts'); import collect
tag,out,n=sys.argv[1],sys.argv[2],int(sys.argv[3])
c=collect.chunks(tag); miss=[i for i in range(n) if i not in c]
if miss: print('MISSING',miss); sys.exit(1)
b=''.join(c[i] for i in range(n)); raw=gzip.decompress(base64.b64decode(b))
open(out,'wb').write(raw); print(out,len(raw))
