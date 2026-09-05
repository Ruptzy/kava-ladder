# -*- coding: utf-8 -*-
"""Albert and Amanda link back to seasons 1-7.

Both were dropped from the old-era table when it was pruned, on the reasoning
that nobody by those names was still playing. The February-March 2025 nights
show otherwise: 19 games for Albert and 12 for Amanda. Amanda's row was kept
(marked dormant) and only needs the link; Albert's was removed outright, so it
comes back from the club's own match record in archive_raw.json.
"""
import json, io

A = json.load(io.open('archive.json', encoding='utf-8'))
raw = json.load(io.open('archive_raw.json', encoding='utf-8'))
by = {p['n']: p for p in A['players']}

if 'Albert' not in by:
    s = raw['stats']['Albert']
    A['players'].append({"n": "Albert", "r": round(s['rating']), "g": s['games'],
                         "rec": [s['w'], s['d'], s['l']], "wh": s['wh'], "bl": s['bl'], "st": ""})
    A['players'].sort(key=lambda p: -p['r'])
    print('Albert restored: %d games, %d-%d-%d, old rating %d'
          % (s['games'], s['w'], s['d'], s['l'], round(s['rating'])))

for cur, old in (("Albert", "Albert"), ("Amanda", "Amanda")):
    if cur not in A['link']:
        A['link'][cur] = old
        print('linked %s -> %s' % (cur, old))

# Amanda is playing again, so she is no longer dormant
for p in A['players']:
    if p['n'] == 'Amanda' and p.get('st') == 'dormant':
        p['st'] = ''
        print('Amanda no longer marked dormant')

json.dump(A, io.open('archive.json', 'w', encoding='utf-8'), separators=(',', ':'))
print('archive now lists %d players, %d linked' % (len(A['players']), len(A['link'])))
