# -*- coding: utf-8 -*-
"""Check every imported tournament night against that tournament's own standings.

Score by score, player by player, byes included at half a point. This is the
check that caught the missing byes the first time round, so it runs over all
seven of the 2025 links, not only the five that were new.
"""
import re, io, html, json, os, collections, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GAP = os.path.join(HERE, 'gap')
from gap2025 import LINKS, DATE, canon  # one definition of each, shared


def standings(tid):
    f = os.path.join(GAP, 'rating_%s.html' % tid)
    if not os.path.exists(f):
        u = "https://swissonlinetournament.com/Tournament/Rating/%s" % tid
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        io.open(f, 'w', encoding='utf-8').write(
            urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace"))
    doc = io.open(f, encoding='utf-8').read()
    nm = html.unescape(re.search(r"Tournament name:\s*([^<\n]+)", doc).group(1)).strip()
    out = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, re.S):
        tds = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
               for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) < 3 or not tds[1]:
            continue
        for c in tds[2:]:
            try:
                out[canon(tds[1])] = float(c)
                break
            except ValueError:
                continue
    return nm, out


# the site writes Dave, the club writes his full name
SAME = {"Dave": "Dave Kecthum"}

H = {n['date']: n for n in json.load(io.open(os.path.join(HERE, 'history.json'), encoding='utf-8'))}
bad = checked = 0
for tid in LINKS:
    nm, site = standings(tid)
    d = DATE[nm]
    site = {SAME.get(k, k): v for k, v in site.items()}
    mine = collections.Counter()
    for w, b, r in H[d]['games']:
        mine[w] += 1.0 if r == 'w' else (0.5 if r == 'd' else 0.0)
        mine[b] += 1.0 if r == 'b' else (0.5 if r == 'd' else 0.0)
    for x in H[d].get('byes', []):
        mine[x] += 0.5
    names = set(site) | set(mine)
    off = [n for n in names if abs(site.get(n, -1) - mine.get(n, 0.0)) > 1e-6]
    checked += len(names)
    bad += len(off)
    print('%s  %-24s %2d players  %s' % (d, nm, len(names),
          'ok' if not off else 'MISMATCH: ' + ', '.join(
              '%s site=%s ours=%s' % (n, site.get(n), mine.get(n, 0.0)) for n in sorted(off))))
print('\n%d player-scores checked, %d mismatches' % (checked, bad))
raise SystemExit(1 if bad else 0)
