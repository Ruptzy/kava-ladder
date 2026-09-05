"""Build the public KAVA ladder page (index.html) from history.json + seeds.json + roster.json + archive.json.

The page carries only the raw games and the nightly ratings; every stat, chart,
title and fact is worked out in the browser from those (see ladderbuild.js).
That keeps this build and the phone build identical.
"""
import json, math, datetime, statistics, sys
TAU=0.5; SC=173.7178; RDMIN=30.0; RDMAX=350.0; FLOOR=100.0
SITE="https://ruptzy.github.io/kava-ladder/"

def g(phi): return 1/math.sqrt(1+3*phi*phi/(math.pi**2))
def E(mu,muj,phij): return 1/(1+math.exp(-g(phij)*(mu-muj)))
def newvol(phi,v,delta,sigma):
    a=math.log(sigma*sigma)
    def f(x):
        ex=math.exp(x); d2=delta*delta; p2=phi*phi
        return (ex*(d2-p2-v-ex))/(2*(p2+v+ex)**2)-(x-a)/(TAU*TAU)
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

def run(history,seeds):
    P={}
    def of(n):
        if n not in P:
            P[n]=dict(r=float(seeds.get(n,1000)),rd=RDMAX,vol=0.06,n=0,hist=[])
        return P[n]
    for night in history:
        res={}
        for w,b,r in night["games"]:
            pw,pb=of(w),of(b)
            sw=1.0 if r=="w" else (0.0 if r=="b" else 0.5)
            res.setdefault(w,[]).append((pb["r"],pb["rd"],sw))
            res.setdefault(b,[]).append((pw["r"],pw["rd"],1-sw))
            pw["n"]+=1; pb["n"]+=1
        for n in night.get("byes",[]): of(n)
        snap={n:(p["r"],p["rd"],p["vol"]) for n,p in P.items()}
        for n,p in P.items():
            if n in res:
                mu=(snap[n][0]-1500)/SC; phi=snap[n][1]/SC; sigma=snap[n][2]
                vinv=0.0; dsum=0.0
                for orr,ordd,s in res[n]:
                    muj=(orr-1500)/SC; phij=ordd/SC
                    gj=g(phij); Ej=E(mu,muj,phij)
                    vinv+=gj*gj*Ej*(1-Ej); dsum+=gj*(s-Ej)
                v=1/vinv if vinv>0 else 1e6
                delta=v*dsum; sig=newvol(phi,v,delta,sigma)
                ps=math.sqrt(phi*phi+sig*sig)
                pn=1/math.sqrt(1/(ps*ps)+1/v)
                mn=mu+pn*pn*dsum
                p["r"]=max(FLOOR,mn*SC+1500); p["rd"]=min(RDMAX,max(RDMIN,pn*SC)); p["vol"]=sig
            elif p["n"]>0:
                phi=p["rd"]/SC
                p["rd"]=min(RDMAX,math.sqrt(phi*phi+p["vol"]*p["vol"])*SC)
            if p["n"]>0: p["hist"].append((night["date"],p["r"],p["rd"]))
    return P

def ladder_data(P,history,roster,divisions,archive,seeds,built):
    dates=[h["date"] for h in history]; last=dates[-1] if dates else None
    names=[]; ni={}
    def id_(n):
        if n not in ni: ni[n]=len(names); names.append(n)
        return ni[n]
    for p in roster: id_(p["n"])
    games=[]; byes=[]
    for i,h in enumerate(history):
        for w,b,r in h["games"]: games.append([i,id_(w),id_(b),r])
        if h.get("byes"): byes.append([i]+[id_(x) for x in h["byes"]])
    di={d:i for i,d in enumerate(dates)}
    divOf={p["n"]:p["d"] for p in roster}
    players=[]
    for n,p in P.items():
        if p["n"]<=0: continue
        players.append({"n":n,"d":divOf.get(n,""),"r":round(p["r"]),"rd":round(p["rd"]),"seed":round(seeds.get(n,1000)),
                        "hist":[[di[d],round(r),round(rd)] for d,r,rd in p["hist"]]})
    players.sort(key=lambda x:-x["r"])
    nxt=None
    if len(dates)>=3:
        gaps=sorted((datetime.date.fromisoformat(dates[i])-datetime.date.fromisoformat(dates[i-1])).days for i in range(1,len(dates)))
        med=gaps[len(gaps)//2]
        d=datetime.date.fromisoformat(last)+datetime.timedelta(days=med)
        guard=0
        while built and d.isoformat()<built and guard<12: d+=datetime.timedelta(days=med); guard+=1
        nxt=d.isoformat()
    return {"club":"KAVA Social Chess Club","built":built,"date":last,"next":nxt,"divisions":divisions,
            "dates":dates,"names":names,"games":games,"byes":byes,"players":players,"archive":archive}

if __name__=="__main__":
    HISTORY=json.load(open('history.json')); SEEDS=json.load(open('seeds.json'))
    ARCHIVE=json.load(open('archive.json')); roster=json.load(open('roster.json'))
    built=datetime.date.today().isoformat()
    P=run(HISTORY,SEEDS)
    D=ladder_data(P,HISTORY,roster["roster"],roster["divisions"],ARCHIVE,SEEDS,built)
    DESC="Club ladder · %d games over %d nights · latest night %s"%(len(D["games"]),len(D["dates"]),D["date"])
    src=open('ladderbuild.js',encoding='utf-8').read()
    tpl=src[src.index('return `')+len('return `'):src.rindex('`;')]
    html=(tpl.replace('${JSON.stringify(D)}',json.dumps(D,separators=(',',':'),ensure_ascii=False))
             .replace('${SITE}',SITE).replace('${DESC}',DESC).replace('<\\/script>','</script>'))
    open("index.html","w",encoding="utf-8").write(html)
    print('players',len(D["players"]),'| games',len(D["games"]),'| nights',len(D["dates"]),'| next',D["next"])
    print('index.html',len(html.encode('utf-8')),'bytes | data',len(json.dumps(D,separators=(',',':'))),'bytes')
    print('top:', ', '.join('%s %d'%(p['n'],p['r']) for p in D["players"][:5]))
