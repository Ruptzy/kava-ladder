import json
A=json.load(open('archive.json'))
by={p['n']:p for p in A['players']}

REMOVE=["Gilner","Charle","Vincent","Bobman, Michael","Nick (Orlando)","Tucker (low tide)","Joey","jack",
"Sharf, Sam","Cameron","Joe","Smith, Mike","Hall, Alex","Tyler","Gavin","Huxtable, Andrew","Johnson, Bryson",
"Ryan","Bryson","Albert","Dumpling, Alex","Michael","Gabe","Devon","Zo","chess.com Above 1000","Eddie (lowtide)",
"Crow, Danny","Michael (new)","Sam J.","Anthony","Benny","Giovanni","Asia","Hasoi, Todoroki","Steven N","Bob",
"Rost, Devin","Jesse","Mario","Brandon B.","Charle (albert friend)","Wernstrom, Maya","CamK","Brennan","Arabella",
"Hannah","Trinnity","Wesley","Ru","Naya","Tall Brian","Kimberlee","Abe","Jakob (guest)","Roman","Eduardo","Somarie",
"Noah","Cody (she)","Milcar","Sean (New)","Gabe - Under 800","Haleigh","Codi","Samael","Ricky","Jeff","Hunter",
"Nick","Isaac","Tim","Jared","Natalia","Sam G","John","Chance","JD","Left","Ocean","Emma","Sage","Richard",
"Rayelle","pilpe","Daniel","Quintent","Axel","Drake","Bohdi","Aaron","Erick","Austin","Lane","Seth","Pat","Angel",
"Hunter B","Joy","Juniper","Taylor","Rome","Austin (new)","Katie","Christian","Yovani","Emily","Alaska","Olivia",
"Null","Brandon","Josue","Kaden","Kandee","Zander","Gaeo","Sophie","Ella"]
DORMANT=["Robert","J","Brione","Joseph","Amanda","Sam (Mable)","Tanner","Cody","Beltran, Lyon"]
RENAME={"Brian":"Brian Bellamy"}

missing=[n for n in REMOVE+DORMANT if n not in by]
kept=[]
for p in A['players']:
    if p['n'] in REMOVE: continue
    p['st']="dormant" if p['n'] in DORMANT else ""
    if p['n'] in RENAME: p['was']=p['n']; p['n']=RENAME[p['n']]
    kept.append(p)

# relink: only surviving archive names, and follow the rename
link=json.load(open('archive_link.json'))
link={c:RENAME.get(a,a) for c,a in link.items() if a not in REMOVE}
link["Alex"]="Alex - Tampa"                     # the other two Alexes are gone, so this one is him
names={p['n'] for p in kept}
link={c:a for c,a in link.items() if a in names}

A['players']=kept; A['link']=link
json.dump(A,open('archive.json','w'),separators=(',',':'))
print("kept %d of 147 | removed %d | dormant %d | linked %d" % (len(kept),len(REMOVE),len(DORMANT),len(link)))
if missing: print("!! not found in archive:", missing)
cur={p['n'] for p in json.load(open('roster.json'))['roster']}
unaddressed=[p['n'] for p in kept if p['n'] not in link.values() and not p['st']]
print("\nkept but not linked / not marked dormant:")
for n in unaddressed: print("   %-24s %3dg" % (n, by.get(n,{}).get('g', by.get(RENAME.get(n,n),{}).get('g',0))))
print("\nlinks:", ", ".join("%s→%s"%(c,a) for c,a in sorted(link.items())))
