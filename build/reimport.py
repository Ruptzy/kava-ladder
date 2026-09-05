# -*- coding: utf-8 -*-
"""Re-import the tournament nights keeping every game, guests included.

Dropping one-off visitors from the import also deleted the games regulars played
against them: 39 games, hitting 19 players. Scott's 5-0 on 31 May showed as 4-0
because his first round was against Dennis, and his draw with Deshawn on 16 Aug
vanished the same way. Visitors stay out of the ladder, but their games count.
"""
import re, io, html, glob, json, collections

DATE = {"4/19/26": "2026-04-19", "5/3/26": "2026-05-03", "5/17/26": "2026-05-17",
        "Kava social summer 5/31/26": "2026-05-31", "Kava social summer 6/14/26": "2026-06-14",
        "Bracket 6/27/26": "2026-06-27", "Bracket 7/12/26": "2026-07-12", "08/2/26": "2026-08-02",
        "8/16/26": "2026-08-16", "9/30/26": "2026-08-30"}
CANON = {"omar": "Omar Cruz", "omar cruz": "Omar Cruz", "omar og": "Omar Cruz", "og omar": "Omar Cruz",
         "omar azab": "Omar Azab", "omar a": "Omar Azab",
         "vinny": "Vinny", "vinnie": "Vinny", "vinyy": "Vinny", "vincent": "Vinny",
         "mathew": "Mathew", "matthew": "Mathew", "mathew uf": "Mathew",
         "sam": "Sam", "brian bellamy": "Brian", "brian": "Brian", "brian o": "Brian O",
         "ben": "Benji", "benji": "Benji", "schmerick": "Derek", "derek": "Derek",
         "anothny": "Anthony", "anthony": "Anthony", "diegi": "Diego", "diego": "Diego"}
# visitors: their games count, but they never join the ladder
GUESTS = {"gabe", "mike", "deshawn", "fernando", "dennis", "artem", "drake", "haleigh", "robert"}


def canon(n, night_names=None):
    """Plain "Omar" is Omar Cruz, except on a night where Cruz is already named
    in full ("Omar og"): then the bare name belongs to the other Omar. 17 May is
    the one night both played and only one of them was written out."""
    k = n.strip().lower()
    if k == 'omar' and night_names and any(x in night_names for x in ('omar og', 'og omar', 'omar cruz')):
        return 'Omar Azab'
    return CANON.get(k, n.strip())


nights, guests_seen = {}, set()
for f in sorted(glob.glob('scrape_*.html')):
    doc = io.open(f, encoding='utf-8').read()
    nm = html.unescape(re.search(r"Tournament name:\s*([^<\n]+)", doc).group(1)).strip()
    date = DATE[nm]
    games, byes = [], []
    seen_raw = set()
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, re.S):
        tds = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) >= 4 and tds[1]:
            seen_raw.add(tds[1].strip().lower())
            if len(tds) >= 6 and tds[5]: seen_raw.add(tds[5].strip().lower())
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, re.S):
        tds = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) < 4:
            continue
        if re.search(r"\bbye\b", " ".join(tds), re.I):
            b = canon(tds[1], seen_raw)
            if b:
                byes.append(b)
            continue
        if len(tds) < 6:
            continue
        w, res, b = tds[1], tds[3], tds[5]
        if not res or not w or not b:
            continue
        cw, cb = canon(w, seen_raw), canon(b, seen_raw)
        for raw, c in ((w, cw), (b, cb)):
            if raw.strip().lower() in GUESTS:
                guests_seen.add(c)
        games.append([cw, cb, "w" if res == "1-0" else ("b" if res == "0-1" else "d")])
    nights[date] = {"games": games, "byes": byes}

H = json.load(io.open('history.json', encoding='utf-8'))
before = {n['date']: len(n['games']) for n in H}
for night in H:
    src = nights.get(night['date'])
    if src:
        night['games'] = src['games']
        night['byes'] = src['byes']
missing = [d for d in nights if d not in before]
if missing:
    raise SystemExit('tournament night not in history.json: %s' % missing)

json.dump(H, io.open('history.json', 'w', encoding='utf-8'), separators=(',', ':'))
json.dump(sorted(guests_seen), io.open('guests.json', 'w', encoding='utf-8'))

print('night          before  after')
tot_b = tot_a = 0
for n in H:
    a = len(n['games'])
    b = before[n['date']]
    tot_b += b
    tot_a += a
    if n['date'] in nights:
        print('  %s   %3d    %3d %s' % (n['date'], b, a, '' if a == b else '  <-- %+d' % (a - b)))
print('  total          %3d    %3d' % (tot_b, tot_a))
print('\nvisitors kept in the games but off the ladder:', ', '.join(sorted(guests_seen)))
