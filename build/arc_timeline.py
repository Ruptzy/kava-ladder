# -*- coding: utf-8 -*-
"""Add a per-night timeline for seasons 1-7 to archive.json.

archive_raw.json still holds every old game with its date, so the club history
page can chart the whole run rather than only the current era. Totals are
recomputed from those games so every number on the page comes from one source.
"""
import json, io, collections

raw = json.load(io.open('archive_raw.json', encoding='utf-8'))
A = json.load(io.open('archive.json', encoding='utf-8'))

by = collections.OrderedDict()
for date, w, b, res in raw['matches']:
    e = by.setdefault(date, {'g': 0, 'w': 0, 'd': 0, 'b': 0, 'p': set()})
    e['g'] += 1
    e['p'].add(w)
    e['p'].add(b)
    if res == 'w':
        e['w'] += 1
    elif res == 'b':
        e['b'] += 1
    else:
        e['d'] += 1

tl = [[d, e['g'], len(e['p']), e['w'], e['d'], e['b']] for d, e in sorted(by.items())]
A['tl'] = tl
A['nights'] = len(tl)
A['games'] = sum(x[1] for x in tl)
A['from'] = tl[0][0]
A['to'] = tl[-1][0]
A['players'] = A['players']
A['everPlayed'] = len({n for _d, w, b, _r in raw['matches'] for n in (w, b)})

json.dump(A, io.open('archive.json', 'w', encoding='utf-8'), separators=(',', ':'))
print('seasons 1-7: %d nights, %d games, %s to %s, %d players ever'
      % (A['nights'], A['games'], A['from'], A['to'], A['everPlayed']))
print('busiest night:', max(tl, key=lambda x: x[1]))
print('white %d, drawn %d, black %d'
      % (sum(x[3] for x in tl), sum(x[4] for x in tl), sum(x[5] for x in tl)))
