import zipfile, json, re, datetime
from xml.etree import ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
PATH="D:/Desktop_Moved/Chess/Chess league Kava Social/Chess rankings NEW 2025/2026-04-05 2026-03-22 2025-11-30 11_2_2025 chess ranking Backup (1) Backup - Copy Backup.xlsx"
import os
print("workbook:", os.path.basename(PATH))
z=zipfile.ZipFile(PATH)
ss=[]
root=ET.fromstring(z.read('xl/sharedStrings.xml'))
for si in root.findall('m:si',NS):
    ss.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
wb=ET.fromstring(z.read('xl/workbook.xml'))
rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
sheets={}
for sh in wb.find('m:sheets',NS):
    t=rels[sh.get('{%s}id'%NS['r'])]
    sheets[sh.get('name')]= t if t.startswith('xl/') else 'xl/'+t.lstrip('/')

def grid(name):
    """sheet -> {rownum: {colletter: value}}"""
    out={}
    sr=ET.fromstring(z.read(sheets[name]))
    for row in sr.iter('{%s}row'%NS['m']):
        rn=int(row.get('r')); cells={}
        for c in row.findall('m:c',NS):
            col=re.sub(r'\d+','',c.get('r')); t=c.get('t'); v=c.find('m:v',NS)
            if t=='s' and v is not None: val=ss[int(v.text)]
            elif t=='inlineStr':
                isn=c.find('m:is',NS); val=''.join(x.text or '' for x in isn.iter('{%s}t'%NS['m'])) if isn is not None else None
            elif v is not None:
                try: val=float(v.text)
                except: val=v.text
            else: val=None
            if val is not None: cells[col]=val
        if cells: out[rn]=cells
    return out

def serial(d): return (d-datetime.date(1899,12,30)).days
def unserial(n): return datetime.date(1899,12,30)+datetime.timedelta(days=int(n))

# ---- Ratings by Player: full stats ----
stats={}
g=grid('Ratings by Player')
for rn,c in g.items():
    if rn==1 or 'A' not in c: continue
    n=c['A']
    if not isinstance(n,str): continue
    stats[n]=dict(rating=round(c.get('B',0),1), games=int(c.get('C',0)),
        w=int(c.get('D',0)), l=int(c.get('E',0)), d=int(c.get('F',0)),
        wh=[int(c.get('H',0)),int(c.get('I',0)),int(c.get('J',0))],
        bl=[int(c.get('L',0)),int(c.get('M',0)),int(c.get('N',0))],
        whN=int(c.get('G',0)), blN=int(c.get('K',0)))

# ---- division sheets ----
DIV={}
divmeta={}
# Division sheets are whatever sits between "Ratings by Player" and "Day last played"
# in the workbook — true for both the 2025 and the current Nov-2025 layout, so the
# bracket rename (Over 1000/U1000/U800 -> over 1400/U1400/U1000) needs no code change.
_names=list(sheets)
_a=_names.index('Ratings by Player')+1
_b=next(i for i,n in enumerate(_names) if n.lower()=='day last played')
DIVSHEETS=[n for n in _names[_a:_b]]
# order strongest-first by mean member rating, so tone tiers and tab order follow
# strength rather than whatever order the sheets happen to sit in
def _mean(d):
    g=grid(d); v=[c['D'] for rn,c in g.items() if rn>=7 and isinstance(c.get('D'),float)]
    return sum(v)/len(v) if v else 0
DIVSHEETS.sort(key=_mean, reverse=True)
print('division sheets detected:',DIVSHEETS)
for div in DIVSHEETS:
    g=grid(div)
    hdr=g.get(6,{})
    # column letters -> opponent name for h2h block (from J onward)
    h2hcols={k:v for k,v in hdr.items() if k>='J' and isinstance(v,str)}
    rows=[]
    for rn in sorted(g):
        if rn<7: continue
        c=g[rn]
        if 'C' not in c or not isinstance(c['C'],str): continue
        rows.append(dict(
            divRank=int(c.get('A',0)), overallRank=int(c.get('B',0)), name=c['C'],
            rating=round(c.get('D',0),1),
            chgPrev=round(c['E'],1) if 'E' in c else None,
            chg3mo=round(c['F'],1) if 'F' in c else None,
            lastWDL=c.get('G'), past3=c.get('H'), overall=c.get('I'),
            h2h={h2hcols[k]:c[k] for k in c if k in h2hcols}))
    DIV[div]=rows
    divmeta[div]=len(rows)

# ---- Matches: most recent night ----
g=grid('Matches')
rows=[(c.get('A'),c.get('B'),c.get('C'),c.get('D'),c.get('E')) for rn,c in g.items() if rn>1 and isinstance(c.get('A'),float)]
rows=[r for r in rows if isinstance(r[2],str) and isinstance(r[3],str)]
latest=max(r[0] for r in rows)
night=[r for r in rows if r[0]==latest]
night.sort(key=lambda r:(r[1] or 0))
print('LATEST NIGHT', unserial(latest).isoformat(), 'games:',len(night))
allnights=sorted({r[0] for r in rows})
print('total nights:',len(allnights),'first:',unserial(allnights[0]),'last:',unserial(allnights[-1]),'total games:',len(rows))

out=dict(asOf=unserial(latest).isoformat(),
         divisions=DIV, stats=stats,
         night=[dict(white=w,black=b,winner=win) for _,_,w,b,win in night],
         counts=divmeta, totalGames=len(rows), totalNights=len(allnights))
json.dump(out,open('kava.json','w'),indent=0)
print('divisions:',divmeta)
print('sample night:',out['night'][:6])
