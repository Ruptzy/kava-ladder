# -*- coding: utf-8 -*-
"""Work out where seasons 1-7 divide, and write it down.

    python old_seasons.py --write

Nothing in the old workbooks records where a season ended: every file from
September 2022 to November 2024 carries the same brackets, the ratings never
reset, and the titles are cumulative - "Chess results through <date>". The
club's own "seasons 1-7" was a label put on afterwards.

So the split is a rule, and Harold picked it: the real nights, divided into
seven equal stretches. It lands on three-to-four-month seasons, which is the
cadence the club runs on now, so seasons 1 to 10 read as one rhythm.

The two backlog dates are not nights - each is a pile of games entered under a
single date - so they take no slot, but their games belong to the season they
fall inside.

The answer is written to old_seasons.json and read from there, so the
boundaries are a fact about the club rather than something that shifts if the
record is ever added to. Correcting a boundary means editing that file.
"""
import json, io, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
def here(n): return os.path.join(HERE, n)

SEASONS = 7
raw = json.load(io.open(here('archive_raw.json'), encoding='utf-8'))
try: BATCH = set(json.load(io.open(here('batch_dates.json'), encoding='utf-8'))['dates'])
except Exception: BATCH = set()

nights = sorted({m[0] for m in raw['matches']})
real = [d for d in nights if d not in BATCH]
N = len(real)
bounds = [round(i * N / SEASONS) for i in range(SEASONS + 1)]

out = []
for i in range(SEASONS):
    ns = real[bounds[i]:bounds[i + 1]]
    last = ns[-1]
    nxt = (datetime.date.fromisoformat(last) + datetime.timedelta(days=1)).isoformat()
    out.append({"no": i + 1, "from": ns[0], "last": last, "to": nxt, "nights": len(ns)})

for s in out:
    inside = [d for d in nights if s['from'] <= d < s['to']]
    g = len([m for m in raw['matches'] if s['from'] <= m[0] < s['to']])
    b = [d for d in inside if d in BATCH]
    print('season %d  %s .. %s  %2d nights  %4d games%s'
          % (s['no'], s['from'], s['last'], s['nights'], g,
             '   (+ backlog %s)' % ', '.join(b) if b else ''))
print('%d nights placed of %d real (%d on record)' % (sum(s['nights'] for s in out), N, len(nights)))

if '--write' in sys.argv:
    json.dump({"why": "seasons 1-7 are not recorded anywhere; the club's real nights split "
                      "into seven equal stretches, backlog dates taking no slot",
               "seasons": out},
              io.open(here('old_seasons.json'), 'w', encoding='utf-8'), indent=1)
    print('-> old_seasons.json')
else:
    print('(nothing written - pass --write)')
