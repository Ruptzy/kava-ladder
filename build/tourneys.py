import json, re, urllib.request, html

IDS=["3ca0c80134a04a8283ce5d1c0ba29e06","fa6d602e9d0e46ef804402fcb372062e","05a85e44bca944c18a11d83d315ae2e6",
     "4f411905ea4d45cba7dc56d0c551995d","9345919bb81f4e19bb99f113e2220bd0","5628305c74d542a28e6ffd1426fa3a65",
     "b860f2bcb4904af88ec6717c539b5090","50a2c38c48dc4616a2d6e0a7f79262ff","1bace22971eb4e478dbd812080864525",
     "6df3764bf2fa4a589f547664821374d7"]
# tournament name -> real date (Harold: the last one is 8/30, not 9/30)
DATE={"4/19/26":"2026-04-19","5/3/26":"2026-05-03","5/17/26":"2026-05-17",
      "Kava social summer 5/31/26":"2026-05-31","Kava social summer 6/14/26":"2026-06-14",
      "Bracket 6/27/26":"2026-06-27","Bracket 7/12/26":"2026-07-12","08/2/26":"2026-08-02",
      "8/16/26":"2026-08-16","9/30/26":"2026-08-30"}
CANON={"omar":"Omar Cruz","omar cruz":"Omar Cruz","omar og":"Omar Cruz","og omar":"Omar Cruz",
       "omar azab":"Omar Azab","omar a":"Omar Azab",
       "vinny":"Vinny","vinnie":"Vinny","vinyy":"Vinny","vincent":"Vinny",
       "mathew":"Mathew UF","matthew":"Mathew UF","mathew uf":"Mathew UF",
       "sam":"Sam (mama Smurf)","brian bellamy":"Brian","brian":"Brian","brian o":"Brian O",
       "ben":"Benji","benji":"Benji","schmerick":"Derek","derek":"Derek",
       "anothny":"Anthony","anthony":"Anthony","diegi":"Diego","diego":"Diego"}
DROP={"brad","gabe","mike","deshawn","fernando","dennis","artem","drake","haleigh","robert"}
def canon(n):
    k=n.strip().lower()
    if k in DROP: return None
    return CANON.get(k, n.strip())

def fetch(u):
    req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
    return urllib.request.urlopen(req,timeout=30).read().decode("utf-8","replace")

nights=[]; dropped=0; blank=0; seen=set()
for i in IDS:
    doc=fetch("https://swissonlinetournament.com/Tournament/Details/%s?allRounds=true"%i)
    nm=html.unescape(re.search(r"Tournament name:\s*([^<\n]+)",doc).group(1)).strip()
    date=DATE[nm]
    games=[]; byes=[]
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, re.S):
        tds=[html.unescape(re.sub(r"<[^>]+>","",c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>",tr,re.S)]
        if len(tds)<4: continue
        row=" ".join(tds)
        if re.search(r"\bbye\b",row,re.I):
            b=canon(tds[1])
            if b: byes.append(b)
            continue
        if len(tds)<6: continue
        w,res,b=tds[1],tds[3],tds[5]
        if not res: blank+=1; continue
        cw,cb=canon(w),canon(b)
        if cw is None or cb is None: dropped+=1; continue
        r = "w" if res=="1-0" else ("b" if res=="0-1" else "d")
        games.append([cw,cb,r]); seen.add(cw); seen.add(cb)
    nights.append({"date":date,"games":games,"byes":byes})
nights.sort(key=lambda n:n["date"])
json.dump(nights,open('tournaments.json','w'),separators=(',',':'))
print("nights %d | games %d | skipped-blank %d | dropped (guests) %d | players %d"
      % (len(nights), sum(len(n["games"]) for n in nights), blank, dropped, len(seen)))
for n in nights: print("  %s  %2d games  %2d byes" % (n["date"], len(n["games"]), len(n["byes"])))
print("\nnames:", ", ".join(sorted(seen)))
