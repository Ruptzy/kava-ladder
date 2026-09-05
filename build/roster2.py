import json, re
from buildsite import run, HISTORY, SEEDS      # reuse the same Glicko-2 engine
k=json.load(open('kava.json'))
divs=list(k['divisions'])                      # already ordered strongest-first
tag={r['name']:d for d,rows in k['divisions'].items() for r in rows}

# a bracket name carries its own threshold: "over 1400" = 1400 and up, "U1400" = under 1400
def bounds(name):
    m=re.search(r'(\d+)',name)
    n=int(m.group(1)) if m else 0
    return ('over' if re.search(r'over|above|\+',name,re.I) else 'under'), n
BOUND=[(d,)+bounds(d) for d in divs]
OVERS=sorted([b for b in BOUND if b[1]=='over'], key=lambda b:-b[2])   # highest first
UNDERS=sorted([b for b in BOUND if b[1]=='under'], key=lambda b:b[2])  # tightest first
def bandFor(r):
    for d,_,n in OVERS:
        if r>=n: return d
    for d,_,n in UNDERS:
        if r<n: return d
    return divs[-1]

P=run(HISTORY,SEEDS)
roster=[]
for n,p in P.items():
    if p['n']<=0: continue
    r=round(p['r'])
    roster.append({"n":n,"r":r,"d":tag.get(n) or bandFor(r),"idle":0,"tagged":n in tag})
roster.sort(key=lambda x:-x['r'])
json.dump({"divisions":divs,"roster":[{k2:v for k2,v in x.items() if k2!='tagged'} for x in roster]},
          open('roster.json','w'),separators=(',',':'))
print('roster now',len(roster),'players (was 27)')
from collections import Counter
print('by bracket:',dict(Counter(x['d'] for x in roster)))
print('auto-placed (no tag in the workbook):',sum(1 for x in roster if not x['tagged']))
