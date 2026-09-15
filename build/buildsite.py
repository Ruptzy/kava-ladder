"""Build the public KAVA ladder page (index.html) from history.json + seeds.json + roster.json + archive.json.

The page carries only the raw games and the nightly ratings; every stat, chart,
title and fact is worked out in the browser from those (see ladderbuild.js).
That keeps this build and the phone build identical.
"""
import json, math, datetime, statistics, sys, os, re
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE) if os.path.isdir(os.path.join(os.path.dirname(HERE),'photos')) else HERE
def here(n): return os.path.join(HERE,n)
def slugify(n): return re.sub(r'^-+|-+$','',re.sub(r'[^a-z0-9]+','-',n.lower()))
def ach_art():
    d=os.path.join(ROOT,'achievements')
    if not os.path.isdir(d): return []
    return sorted(f[:-4] for f in os.listdir(d) if f.endswith('.png'))
def tab_art():
    d=os.path.join(ROOT,'tabs')
    if not os.path.isdir(d): return []
    return sorted(f[:-4] for f in os.listdir(d) if f.endswith('.png'))
def photo_slugs():
    d=os.path.join(ROOT,'photos')
    if not os.path.isdir(d): return []
    return sorted(f[:-4] for f in os.listdir(d) if f.endswith('.jpg'))
TAU=0.5; SC=173.7178; RDMIN=30.0; RDMAX=350.0; FLOOR=100.0

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
        # a bye registers the player without touching their rating
        for n in night.get("byes",[]): of(n[0] if isinstance(n,list) else n)
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

def anon_map(hidden):
    """People who have left the club and asked not to be listed. Their games stay
    in the replay, so nobody else's rating or record moves, but the name is
    swapped for a neutral label before anything is written, so it is not in the
    file at all. The page prints these as "Visitor"; the number only exists to
    keep them apart as data.

    The phone build calls this too. It has to: the pairing tool renders the same
    page from its own copy of the history, so a swap that happened only here
    would put every name straight back the first time Harold published from his
    phone."""
    return {n: "Visitor %d" % (i + 1) for i, n in enumerate(sorted(hidden))}


def anonymise(history, seeds, hidden):
    """History and seeds with the names already swapped. Relabelling before the
    replay rather than after it keeps both builds on identical numbers."""
    a = anon_map(hidden)
    if not a:
        return history, seeds
    h = [{"date": n["date"],
          "games": [[a.get(w, w), a.get(b, b), r] for w, b, r in n["games"]],
          # a bye is [name, points]; older files carry a bare name
          "byes": [[a.get(x[0], x[0]), x[1]] if isinstance(x, list) else a.get(x, x)
                   for x in n.get("byes", [])]} for n in history]
    return h, {a.get(k, k): v for k, v in seeds.items()}


SEASON_ANCHOR=(9,"2026-06-01")   # season 9 opens here; three months each
SEASON_MONTHS=3


def season_of(date):
    """Which season a date falls in, and the calendar window it runs over."""
    no,anchor=SEASON_ANCHOR
    y,m=int(date[:4]),int(date[5:7])
    ay,am=int(anchor[:4]),int(anchor[5:7])
    step=((y-ay)*12+(m-am))//SEASON_MONTHS
    sm=am+step*SEASON_MONTHS; sy=ay+(sm-1)//12; sm=(sm-1)%12+1
    em=sm+SEASON_MONTHS; ey=sy+(em-1)//12; em=(em-1)%12+1
    return no+step, "%04d-%02d-01"%(sy,sm), "%04d-%02d-01"%(ey,em)


SEASON_LOOKBACK=2   # seasons a bracket sticks for, counting the current one


def lookback_start(season_start):
    """The first day of the window a bracket is held over: this season and the
    SEASON_LOOKBACK-1 before it."""
    d=season_start
    for _ in range(SEASON_LOOKBACK-1):
        y,m=int(d[:4]),int(d[5:7])
        m-=SEASON_MONTHS
        while m<1: m+=12; y-=1
        d="%04d-%02d-01"%(y,m)
    return d


def window_level(P, frm, to):
    """What each player actually was over the window: the average rating they
    carried into its nights.

    An average rather than a peak, deliberately. A peak promotes somebody on one
    good night and then holds them there - Sonny touched 1024 once, finished the
    season on 942, and was being kept out of the bracket he belonged in. An
    average is also the harder of the two to fake: you can tank a finishing
    number in a fortnight, but not a season's worth of them."""
    out={}
    for n,p in P.items():
        vals=[]
        prev=None
        for date,r,rd in p["hist"]:
            if prev is not None and frm<=date<to:
                vals.append(prev)
            prev=r
        if vals:
            out[n]=round(sum(vals)/len(vals))
    return out


def split_season(history, today=None):
    """The nights of the current season, and everything before them. Ratings
    are built from both; the page only shows the season.

    With `today`, the current season is the calendar's: once a season is over
    the next one has begun, before anybody has played in it, and the ladder
    should say so. Without it (a frozen past season) it is the season of the
    last night."""
    if not history:
        return None, [], []
    no,start,end=season_of(history[-1]["date"])
    if today:
        cno,cstart,cend=season_of(today)
        if cno>no: no,start,end=cno,cstart,cend
    season=[h for h in history if start<=h["date"]<end]
    vault=[h for h in history if h["date"]<start]
    return {"no":no,"from":start,"to":end}, vault, season


def vault_timeline(vault):
    """One row per vaulted night, shaped like the old era's: the club history
    page draws all three eras off the same rows."""
    out=[]
    for night in vault:
        w=d=b=0; who=set()
        for a,c,r in night["games"]:
            who.add(a); who.add(c)
            if r=="w": w+=1
            elif r=="b": b+=1
            else: d+=1
        out.append([night["date"], len(night["games"]), len(who), w, d, b])
    return out


def vault_totals(vault):
    """Each player's record across the vaulted nights, as a total."""
    out={}
    for night in vault:
        for w,b,r in night["games"]:
            for n,k in ((w, 0 if r=="w" else 1 if r=="d" else 2),
                        (b, 0 if r=="b" else 1 if r=="d" else 2)):
                e=out.setdefault(n,[0,0,0,0])
                e[k]+=1; e[3]+=1
    return out


def band_of(r, divisions):
    """The bracket a rating falls in. Thresholds come out of the division names,
    so "over 1400" floors at 1400 and renaming one keeps working."""
    import re
    nums=[int(re.search(r"(\d+)",d).group(1)) if re.search(r"(\d+)",d) else 0 for d in divisions]
    for i,d in enumerate(divisions):
        floor=nums[0] if i==0 else (nums[i+1] if i+1<len(divisions) else None)
        if floor is None or r>=floor:
            return d
    return divisions[-1]


def season_bands(P, season_nights, peaks, divisions):
    """Each player's bracket for the season, fixed on their first night of it.

    Break your section's ceiling mid-season and you still play for its prize,
    then move up when the next season starts - Harold's rule, and the only one
    that does not punish improving. The floor is what they averaged last season,
    so a bad fortnight cannot buy an easier bracket and one good night cannot
    cost them the one they belong in."""
    dates={n["date"] for n in season_nights}
    out={}
    if not dates:
        # before the season's first night: where each returning player will
        # start, which is exactly what their first night fixes - no jump on it
        for n,lvl in peaks.items():
            q=P.get(n)
            if q and q["n"]>0: out[n]=band_of(max(q["r"], lvl), divisions)
        return out
    for n,p in P.items():
        if p["n"]<=0: continue
        inside=[h for h in p["hist"] if h[0] in dates]
        before=[h for h in p["hist"] if h[0] not in dates]
        if not inside: continue
        # a newcomer's seed is untested, so their band comes from their first
        # played night rather than from a number somebody typed
        entry=before[-1][1] if before else inside[0][1]
        out[n]=band_of(max(entry, peaks.get(n, -10**9)), divisions)
    return out


def career_stats(history, arc_matches, link, names):
    """Everything an achievement counts, over every night on record.

    The old era is in here too: `link` maps a current name to whatever the old
    workbook called them, which is the same mapping the All time table trusts.
    Only the accumulating fields are computed - the ones a season can no longer
    reach. Form is left to the season, where it belongs."""
    back = {old: cur for cur, old in (link or {}).items()}
    nights = {}
    for night in history:
        nights.setdefault(night["date"], []).extend(night["games"])
    for d, w, b, r in arc_matches or []:
        nights.setdefault(d, []).append([back.get(w, w), back.get(b, b), r])

    every = sorted(nights)
    idx = {d: i for i, d in enumerate(every)}
    out = {}
    for d in every:
        per = {}
        for w, b, r in nights[d]:
            for me, k in ((w, 0 if r == "w" else 1 if r == "d" else 2),
                          (b, 0 if r == "b" else 1 if r == "d" else 2)):
                e = out.setdefault(me, {"rec": [0, 0, 0], "wh": [0, 0, 0], "bl": [0, 0, 0],
                                        "nights": [], "opp": {}, "full": 0, "sweeps": 0,
                                        "perfect5": False, "maxNight": 0})
                e["rec"][k] += 1
                per.setdefault(me, [0, 0, 0])[k] += 1
            out[w]["wh"][0 if r == "w" else 1 if r == "d" else 2] += 1
            out[b]["bl"][0 if r == "b" else 1 if r == "d" else 2] += 1
            out[w]["opp"][b] = out[w]["opp"].get(b, 0) + 1
            out[b]["opp"][w] = out[b]["opp"].get(w, 0) + 1
        for me, wdl in per.items():
            e = out[me]
            e["nights"].append(idx[d])
            g = sum(wdl)
            if g > e["maxNight"]: e["maxNight"] = g
            if g >= 5: e["full"] += 1
            if wdl[1] == 0 and wdl[2] == 0 and wdl[0] >= 4: e["sweeps"] += 1
            if wdl[1] == 0 and wdl[2] == 0 and wdl[0] >= 5: e["perfect5"] = True

    def days(a, b):
        import datetime
        return (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days

    final = {}
    for n in names:
        e = out.get(n)
        if not e: continue
        ns = e["nights"]
        run = best = 1 if ns else 0
        for i in range(1, len(ns)):
            if ns[i] == ns[i - 1] + 1:
                run += 1; best = max(best, run)
            else:
                run = 1
        gap = 0
        for i in range(1, len(ns)):
            gap = max(gap, days(every[ns[i - 1]], every[ns[i]]))
        first, last = every[ns[0]], every[ns[-1]]
        final[n] = {
            "games": sum(e["rec"]), "rec": e["rec"], "wh": e["wh"], "bl": e["bl"],
            "nights": len(ns), "bestRun": best, "backAfter": gap,
            "months": len({every[i][:7] for i in ns}), "calYears": len({every[i][:4] for i in ns}),
            "first": first, "last": last, "span": days(first, last),
            "opps": len(e["opp"]), "topRival": max(e["opp"].values()) if e["opp"] else 0,
            "full": e["full"], "sweeps": e["sweeps"], "perfect5": e["perfect5"],
            "maxNight": e["maxNight"],
            # what share of the club nights since they started they have turned up to
            "share": len(ns) / max(1, len(every) - ns[0]),
        }
    return final


def ladder_data(P,history,roster,divisions,archive,seeds,built,hidden=(),vault=(),season=None,peaks=None,career=None,bands=None):
    PEAKS=peaks or {}
    VAULT=vault_totals(vault)
    VAULT_SUM={"nights":len(vault),"games":sum(len(n["games"]) for n in vault),
               "from":vault[0]["date"] if vault else None,
               "to":vault[-1]["date"] if vault else None,
               "tl":vault_timeline(vault)}
    dates=[h["date"] for h in history]; last=dates[-1] if dates else None
    names=[]; ni={}
    def id_(n):
        if n not in ni: ni[n]=len(names); names.append(n)
        return ni[n]
    for p in roster: id_(p["n"])
    show=lambda n: n
    games=[]; byes=[]
    for i,h in enumerate(history):
        for w,b,r in h["games"]: games.append([i,id_(show(w)),id_(show(b)),r])
        # one row per bye, carrying what it was worth
        for x in h.get("byes") or []:
            who, pts = (x, 0.5) if isinstance(x, str) else (x[0], x[1])
            byes.append([i, id_(show(who)), pts])
    di={d:i for i,d in enumerate(dates)}
    divOf={p["n"]:p["d"] for p in roster}
    awayOf={p["n"]:bool(p.get("away")) for p in roster}
    activeOf={p["n"]:bool(p.get("active")) for p in roster}
    players=[]
    for n,p in P.items():
        if p["n"]<=0: continue
        n=show(n)
        # hist and seed are trimmed to the nights the page holds, so the
        # journey chart starts where the season does rather than at a rating
        # from a year ago that nothing on this page explains
        before=[h for h in p["hist"] if h[0] not in di]
        rec={"n":n,"d":divOf.get(n,""),"r":round(p["r"]),"rd":round(p["rd"]),
             "seed":round(before[-1][1] if before else seeds.get(n,1000)),
             "hist":[[di[d],round(r),round(rd)] for d,r,rd in p["hist"] if d in di]}
        if not before: rec["nw"]=1     # no rating before this season: seed is a guess
        bd=(bands or {}).get(n)
        if bd: rec["bd"]=bd            # the bracket for this season, fixed on night one
        cr=(career or {}).get(n)
        if cr: rec["c"]=cr             # what they have done, over every night on record
        pk=PEAKS.get(n)
        if pk is not None: rec["pk"]=pk   # best band held over the lookback window
        v=VAULT.get(n)
        if v: rec["v"]=v
        if n not in divOf: rec["gh"]=1        # a visitor: games count, but off the ladder
        if awayOf.get(n): rec["aw"]=1
        if activeOf.get(n): rec["ac"]=1
        players.append(rec)
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
            "dates":dates,"names":names,"games":games,"byes":byes,"players":players,"archive":archive,
            "season":season,"vault":VAULT_SUM}

NIGHTS_DIR='nights'   # build/nights/<date>.json: one file per night the phone submits


def _night_files():
    d=here(NIGHTS_DIR)
    if not os.path.isdir(d): return []
    return [os.path.join(d,f) for f in sorted(os.listdir(d)) if f.endswith('.json')]


def load_history():
    """history.json plus every night the phone has submitted since.

    The phone does not build the site. It saves the night it just played as
    build/nights/<date>.json and GitHub runs this script, so the site is only
    ever built one way. A date already in history.json wins: that file is the
    corrected record, and a night file never overrides a correction."""
    history=json.load(open(here('history.json'),encoding='utf-8'))
    have={h["date"] for h in history}
    for path in _night_files():
        night=json.load(open(path,encoding='utf-8'))
        date=night.get("date")
        for g in night.get("games",[]):
            if not (isinstance(g,list) and len(g)==3 and g[0] and g[1] and g[2] in ("w","b","d")):
                raise ValueError("%s: a game is not [white, black, w|b|d]: %r"%(os.path.basename(path),g))
        if date and date not in have and night.get("games"):
            history.append({"date":date,"games":night["games"],"byes":night.get("byes",[])})
            have.add(date)
    history.sort(key=lambda h:h["date"])
    return history


def night_seeds():
    """Starting ratings for anybody the phone added on a night. A walk-in's
    rating is typed in on the phone; if the replay here started them anywhere
    else, the site and the phone would disagree about that player for good."""
    out={}
    for path in _night_files():
        for n,r in (json.load(open(path,encoding='utf-8')).get("seeds") or {}).items():
            out.setdefault(n,r)
    return out


def night_roster():
    """Players the phone added on a night. A walk-in typed into the phone is a
    new member; without this the site filed them as a visitor, off the ladder."""
    out=[]; seen=set()
    for path in _night_files():
        for q in (json.load(open(path,encoding='utf-8')).get("new") or []):
            if q.get("n") and q["n"] not in seen:
                seen.add(q["n"]); out.append({"n":q["n"],"d":q.get("d") or ""})
    return out


def season_bounds(no):
    """The calendar window of season number no."""
    ano,anchor=SEASON_ANCHOR
    y,m=int(anchor[:4]),int(anchor[5:7])
    m+=(no-ano)*SEASON_MONTHS
    y+=(m-1)//12; m=(m-1)%12+1
    return season_of("%04d-%02d-01"%(y,m))[1:]


def completed_seasons(history, today):
    """Seasons over by the calendar that had at least one night, from the first
    numbered one on. Each gets a frozen page of its own."""
    cur=season_of(today)[0]
    out=[]
    for no in range(SEASON_ANCHOR[0], cur):
        frm,to=season_bounds(no)
        if any(frm<=h["date"]<to for h in history):
            out.append((no,frm,to))
    return out


def page(D):
    src=open(here('ladderbuild.js'),encoding='utf-8').read()
    tpl=src[src.index('return `')+len('return `'):src.rindex('`;')]
    return (tpl.replace('${JSON.stringify(D)}',json.dumps(D,separators=(',',':'),ensure_ascii=False))
               .replace('<\\/script>','</script>'))


def next_night(dates, built):
    """When the next club night should be, from the usual gap between the
    recent nights - over the club's record, not just this season's, so the
    first nights of a season still have an answer."""
    dates=dates[-7:]
    if len(dates)<3: return None
    gaps=sorted((datetime.date.fromisoformat(dates[i])-datetime.date.fromisoformat(dates[i-1])).days
                for i in range(1,len(dates)))
    med=gaps[len(gaps)//2]
    d=datetime.date.fromisoformat(dates[-1])+datetime.timedelta(days=med)
    guard=0
    while built and d.isoformat()<built and guard<12: d+=datetime.timedelta(days=med); guard+=1
    return d.isoformat()


def build_data(HISTORY,SEEDS,ARCHIVE,roster,DIVH,HIDDEN,ARCM,built,calendar=True):
    """Everything the page ships, from one history. The replay reads all of it;
    only the page narrows to the season of the last night."""
    P=run(HISTORY,SEEDS)
    SEASON,VAULTED,SEASON_NIGHTS=split_season(HISTORY, built if calendar else None)
    PEAKS=window_level(P, lookback_start(SEASON["from"]), SEASON["from"])
    CAREER=career_stats(HISTORY, ARCM, ARCHIVE.get('link'), set(P.keys()))
    BANDS=season_bands(P, SEASON_NIGHTS, PEAKS, roster["divisions"])
    D=ladder_data(P,SEASON_NIGHTS,roster["roster"],roster["divisions"],ARCHIVE,SEEDS,built,
                  HIDDEN,VAULTED,SEASON,PEAKS,CAREER,BANDS)
    D["pics"]=photo_slugs()
    # the bracket snapshots name everyone the club had on a sheet, so the people
    # who have left have to come out of those too
    D["divhist"]=[{**s,"div":{k:v for k,v in s["div"].items() if k not in HIDDEN}} for s in DIVH]
    D["tabart"]=tab_art()
    D["achart"]=ach_art()
    # games each player had last season: before a season's first night the board
    # is last season's players, and a rating alone cannot tell who they were -
    # the replay moves everybody's rating every night, played or not
    frm,to=season_bounds(SEASON["no"]-1)
    last={}
    for h in HISTORY:
        if frm<=h["date"]<to:
            for w,b_,r in h["games"]:
                last[w]=last.get(w,0)+1; last[b_]=last.get(b_,0)+1
    for rec in D["players"]:
        if last.get(rec["n"]): rec["ls"]=last[rec["n"]]
    D["next"]=next_night([h["date"] for h in HISTORY], built)
    # no night yet this season: "includes" means the latest night on record
    if not D["date"] and HISTORY: D["date"]=HISTORY[-1]["date"]
    return D,SEASON,VAULTED


SITE_URL="https://ladder.kavasocialchessclub.com/"
HEAD_TITLE="Kava Social Chess Club Ladder &mdash; Bradenton, FL"
HEAD_DESC=("Live ratings, player profiles and full game history for the Kava Social Chess Club "
           "in Bradenton, Florida. Meets Sundays and Tuesdays, 8PM to midnight.")


def champions(Da):
    """Who won each bracket of a finished season, by the same rule the Discord
    finale uses: settled rating (RD <= 110), at least half the season's nights,
    highest rating in the bracket they were fixed in."""
    names=Da["names"]; need=-(-len(Da["dates"])//2)
    nights={}
    for ni,w,b,r in Da["games"]:
        for i in (w,b): nights.setdefault(names[i],set()).add(ni)
    out=[]
    for d in Da["divisions"]:
        best=None
        for q in Da["players"]:
            if q.get("gh") or q.get("bd")!=d or q["rd"]>110: continue
            if len(nights.get(q["n"],()))<need: continue
            if best is None or q["r"]>best["r"]: best=q
        if best: out.append({"d":d,"n":best["n"],"r":best["r"]})
    return out


def archive_head(html,no):
    """A frozen season is its own page: its own title, description and address,
    so a search result for it says what it is."""
    t="Season %d final standings &mdash; Kava Social Chess Club"%no
    d=("Season %d final standings, ratings and every game played, for the Kava Social "
       "Chess Club in Bradenton, Florida.")%no
    u=SITE_URL+"season-%d.html"%no
    for a,b,n in [("<title>%s</title>"%HEAD_TITLE,"<title>%s</title>"%t,1),
                  ('og:title" content="%s"'%HEAD_TITLE,'og:title" content="%s"'%t,1),
                  ('content="%s"'%HEAD_DESC,'content="%s"'%d,2),
                  ('<link rel="canonical" href="%s">'%SITE_URL,'<link rel="canonical" href="%s">'%u,1),
                  ('og:url" content="%s"'%SITE_URL,'og:url" content="%s"'%u,1)]:
        assert html.count(a)==n,(a,html.count(a))
        html=html.replace(a,b)
    return html



if __name__=="__main__":
    HISTORY=load_history(); SEEDS=json.load(open(here('seeds.json')))
    for n,r in night_seeds().items(): SEEDS.setdefault(n,r)
    ARCHIVE=json.load(open(here('archive.json'))); roster=json.load(open(here('roster.json')))
    _have={q["n"] for q in roster["roster"]}
    roster["roster"]+=[q for q in night_roster() if q["n"] not in _have]   # walk-ins join
    try: DIVH=json.load(open(here('divhistory.json')))['snapshots']
    except Exception: DIVH=[]
    try: HIDDEN=json.load(open(here('hidden.json')))
    except Exception: HIDDEN=[]
    try: ARCM=json.load(open(here('archive_raw.json')))['matches']
    except Exception: ARCM=[]
    built=datetime.date.today().isoformat()
    HISTORY,SEEDS=anonymise(HISTORY,SEEDS,HIDDEN)
    # every season over by the calendar gets a frozen page of its own
    PAST=completed_seasons(HISTORY, built)
    D,SEASON,VAULTED=build_data(HISTORY,SEEDS,ARCHIVE,roster,DIVH,HIDDEN,ARCM,built)
    D["past"]=[no for no,_,_ in PAST]
    D["champs"]=[]
    print('season %d: %s .. %s | vault %d nights, %d games'
          % (SEASON["no"], D["dates"][0] if D["dates"] else "no nights yet",
             D["dates"][-1] if D["dates"] else "-", len(VAULTED),
             sum(len(n["games"]) for n in VAULTED)))
    for no,frm,to in PAST:
        cut=[h for h in HISTORY if h["date"]<to]
        Da,Sa,Va=build_data(cut,SEEDS,ARCHIVE,roster,[s for s in DIVH if s.get("date","")<to],
                            HIDDEN,ARCM,built,calendar=False)
        Da["arch"]=no; Da["past"]=D["past"]; Da["next"]=None
        name='season-%d.html'%no
        open(os.path.join(ROOT,name),'w',encoding='utf-8').write(archive_head(page(Da),no))
        print('%s: season %d frozen | %d nights, %d games, %s .. %s'
              % (name,no,len(Da["dates"]),len(Da["games"]),Da["dates"][0],Da["dates"][-1]))
        D["champs"].insert(0,{"no":no,"list":champions(Da)})   # newest first
    html=page(D)
    out=os.path.join(ROOT,'index.html')
    open(out,'w',encoding='utf-8').write(html)
    print('players',len([p for p in D["players"] if not p.get("gh")]),
          '(+%d visitors)'%len([p for p in D["players"] if p.get("gh")]),
          '| games',len(D["games"]),'| nights',len(D["dates"]),
          '| photos',len(D["pics"]),'| ->',out)
    print('index.html',len(html.encode('utf-8')),'bytes | data',len(json.dumps(D,separators=(',',':'))),'bytes')
    vis=[p for p in D["players"] if not p.get("gh")][:5]
    print('top:', ', '.join('%s %d'%(p['n'],p['r']) for p in vis))
    for c in D["champs"]:
        print('season %d champions: %s' % (c["no"], ', '.join('%s %s %d'%(x["d"],x["n"],x["r"]) for x in c["list"])))
