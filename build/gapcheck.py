# -*- coding: utf-8 -*-
"""Check every imported night against that tournament's own standings.

Score by score, player by player, byes counted at half a point. This is the
check that caught the missing byes the first time round, so it runs over every
link on record, not only the ones most recently added.
"""
import re, io, html, json, os, collections

from gap2025 import LINKS, canon, cache  # one definition of each, shared

HERE = os.path.dirname(os.path.abspath(__file__))
# the site writes Dave; the club writes his full name
SAME = {"Dave": "Dave Kecthum"}


def standings(tid):
    date = LINKS[tid]
    doc = io.open(cache(tid, 'rating_'), encoding='utf-8').read()
    nm = html.unescape(re.search(r"Tournament name:\s*([^<\n]+)", doc).group(1)).strip()
    out = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, re.S):
        tds = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
               for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) < 3 or not tds[1]:
            continue
        for c in tds[2:]:
            try:
                out[canon(tds[1], date)] = float(c)
                break
            except ValueError:
                continue
    return nm, {SAME.get(k, k): v for k, v in out.items()}


H = {n['date']: n for n in json.load(io.open(os.path.join(HERE, 'history.json'), encoding='utf-8'))}
bad = checked = 0
for tid, d in sorted(LINKS.items(), key=lambda kv: kv[1]):
    nm, site = standings(tid)
    if d not in H:
        print('%s  %-24s not imported (seasons 1-7 has it)' % (d, nm))
        continue
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
