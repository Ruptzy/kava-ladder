import zipfile,re,json,math,datetime
from xml.etree import ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
PATH="D:/Desktop_Moved/Chess/Chess league Kava Social/Chess rankings NEW 2025/2026-04-05 2026-03-22 2025-11-30 11_2_2025 chess ranking Backup (1) Backup - Copy Backup.xlsx"
import os
print("workbook:", os.path.basename(PATH))
z=zipfile.ZipFile(PATH)
ss=[''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
wb=ET.fromstring(z.read('xl/workbook.xml'))
rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
SH={sh.get('name'):(lambda t: t if t.startswith('xl/') else 'xl/'+t.lstrip('/'))(rels[sh.get('{%s}id'%NS['r'])]) for sh in wb.find('m:sheets',NS)}
def grid(name):
    out={}
    for row in ET.fromstring(z.read(SH[name])).iter('{%s}row'%NS['m']):
        rn=int(row.get('r')); cells={}
        for c in row.findall('m:c',NS):
            col=re.sub(r'\d+','',c.get('r')); t=c.get('t'); v=c.find('m:v',NS)
            if v is None: continue
            if t=='s': cells[col]=ss[int(v.text)]
            else:
                try: cells[col]=float(v.text)
                except: cells[col]=v.text
        if cells: out[rn]=cells
    return out
def unser(n): return datetime.date(1899,12,30)+datetime.timedelta(days=int(n))

# ---------- inputs ----------
init={}
for rn,c in grid('Player List').items():
    if rn==1 or not isinstance(c.get('A'),str): continue
    init[c['A']]=float(c.get('B',1000))
matches=[]
for rn,c in grid('Matches').items():
    if rn==1: continue
    d,w,b,win=c.get('A'),c.get('C'),c.get('D'),c.get('E')
    if not(isinstance(d,float) and isinstance(w,str) and isinstance(b,str)): continue
    matches.append((int(d),w,b,win))
matches.sort(key=lambda m:m[0])
nights=sorted({m[0] for m in matches})
print('players with initial rating:',len(init),'| matches:',len(matches),'| nights:',len(nights))

# ---------- Glicko-2 ----------
TAU=0.5; SC=173.7178; RD_MIN=30.0; RD_MAX=350.0; FLOOR=100.0
class P:
    def __init__(s,r): s.r=r; s.rd=350.0; s.vol=0.06; s.n=0; s.hist=[]; s.pidx=[]; s.peak=r; s.rdBefore=None
def g(phi): return 1/math.sqrt(1+3*phi*phi/(math.pi**2))
def E(mu,muj,phij): return 1/(1+math.exp(-g(phij)*(mu-muj)))
def newvol(phi,v,delta,sigma):
    a=math.log(sigma**2)
    def f(x):
        ex=math.exp(x); d2=delta*delta; ph2=phi*phi
        return (ex*(d2-ph2-v-ex))/(2*(ph2+v+ex)**2)-(x-a)/(TAU*TAU)
    A=a
    if delta*delta>phi*phi+v: B=math.log(delta*delta-phi*phi-v)
    else:
        k=1
        while f(a-k*TAU)<0: k+=1
        B=a-k*TAU
    fA,fB=f(A),f(B)
    for _ in range(100):
        if abs(B-A)<=1e-6: break
        C=A+(A-B)*fA/(fB-fA); fC=f(C)
        if fC*fB<=0: A,fA=B,fB
        else: fA/=2
        B,fB=C,fC
    return math.exp(A/2)

pl={}
def get(n):
    if n not in pl: pl[n]=P(init.get(n,1000.0))
    return pl[n]

deltas_last={}
for ni,night in enumerate(nights):
    todays=[m for m in matches if m[0]==night]
    results={}
    for _,w,b,win in todays:
        pw,pb=get(w),get(b)
        if win==w: sw,sb=1.0,0.0
        elif win==b: sw,sb=0.0,1.0
        else: sw,sb=0.5,0.5
        results.setdefault(w,[]).append((pb.r,pb.rd,sw))
        results.setdefault(b,[]).append((pw.r,pw.rd,sb))
    snap={n:(p.r,p.rd,p.vol) for n,p in pl.items()}
    for n,p in pl.items():
        if n in results:
            p.pidx.append(ni)
            if ni==len(nights)-1: p.rdBefore=snap[n][1]
            mu=(snap[n][0]-1500)/SC; phi=snap[n][1]/SC; sigma=snap[n][2]
            vinv=0.0; dsum=0.0
            for (orr,ordd,s) in results[n]:
                muj=(orr-1500)/SC; phij=ordd/SC
                gj=g(phij); Ej=E(mu,muj,phij)
                vinv+=gj*gj*Ej*(1-Ej); dsum+=gj*(s-Ej)
            v=1/vinv if vinv>0 else 1e6
            delta=v*dsum
            sig=newvol(phi,v,delta,sigma)
            phistar=math.sqrt(phi*phi+sig*sig)
            phinew=1/math.sqrt(1/(phistar*phistar)+1/v)
            munew=mu+phinew*phinew*dsum
            newr=max(FLOOR,munew*SC+1500)
            newrd=min(RD_MAX,max(RD_MIN,phinew*SC))
            deltas_last[n]=newr-p.r
            p.r,p.rd,p.vol=newr,newrd,sig
            p.peak=max(p.peak,newr)
            p.n+=len(results[n])
        else:
            if p.n>0:  # inactivity inflates RD only
                phi=p.rd/SC
                p.rd=min(RD_MAX,math.sqrt(phi*phi+p.vol*p.vol)*SC)
        if p.n>0: p.hist.append({"d":unser(night).isoformat(),"r":round(p.r,1),"rd":round(p.rd,1)})

played_last={m[1] for m in matches if m[0]==nights[-1]}|{m[2] for m in matches if m[0]==nights[-1]}
tab=sorted(((n,p) for n,p in pl.items() if p.n>0),key=lambda kv:-kv[1].r)
print('\nGlicko-2 replay — top 15 (CRA rating in brackets):')
cra={}
for div in json.load(open('kava.json'))['divisions']:
    for rn,c in grid(div).items():
        if rn>=7 and isinstance(c.get('C'),str): cra[c['C']]=round(c.get('D',0),1)
for i,(n,p) in enumerate(tab[:15],1):
    print('  %2d %-22s %7.1f ±%-5.1f n=%-4d [CRA %s]'%(i,n,p.r,p.rd,p.n,cra.get(n,'—')))
json.dump({n:{"r":round(p.r,1),"rd":round(p.rd,1),"vol":round(p.vol,4),"n":p.n,
              "peak":round(p.peak,1),"rdBefore":round(p.rdBefore,1) if p.rdBefore else None,
              "gap":(p.pidx[-1]-p.pidx[-2]) if len(p.pidx)>1 else None,
              "hist":p.hist[-24:],"delta":round(deltas_last.get(n,0),1),
              "played":n in played_last} for n,p in pl.items() if p.n>0},
          open('glicko2.json','w'))
print('\nwrote glicko2.json for',sum(1 for p in pl.values() if p.n>0),'rated players')
