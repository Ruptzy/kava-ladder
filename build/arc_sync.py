# -*- coding: utf-8 -*-
"""Put the seasons 1-7 table back on the club's own season 7 records.

    python arc_sync.py            show what would change
    python arc_sync.py --write    write it

Harold spotted this against the last workbook of season 7 (24 November 2024):
Josh read 58-4-37 on the site and 49-3-32 in the file, Cade 23-1-21 against
15-1-14. Every one of those gaps is that player's December 2024 and January
2025 ladder games - archive.json had been built from the January 2025 workbook
rather than the November one, so four nights that live in history.json were
counted a second time in the old era. The all-time table adds the archive to
the vault, so those 124 games were counted twice there too. It also carried a
name that only exists in the later file: the workbook calls him Brian.

archive_raw.json is the November workbook, read straight out of the sheet by
archive.py, and 145 of its 147 players reconcile exactly with its own match
list - so it is the source of truth here. Nothing else moves: the replay reads
history.json, never this file.
"""
import json, io, sys

A = json.load(io.open('archive.json', encoding='utf-8'))
raw = json.load(io.open('archive_raw.json', encoding='utf-8'))
stats = raw['stats']
back = {old: cur for cur, old in A['link'].items()}   # old-era name -> name now

rows, renames, missing = [], {}, []
for p in A['players']:
    # the workbook's own spelling: the row's name, or the name the club uses now
    name = p['n'] if p['n'] in stats else (back.get(p['n']) if back.get(p['n']) in stats else None)
    if not name:
        missing.append(p['n']); continue
    s = stats[name]
    rows.append((p, name, {"n": name, "r": round(s['rating']), "g": s['games'],
                           "rec": [s['w'], s['d'], s['l']], "wh": s['wh'], "bl": s['bl'],
                           "st": p.get('st', "")}))
    if name != p['n']: renames[p['n']] = name

print('%-18s %-14s %-14s %-11s %s' % ('seasons 1-7', 'on the site', 'season 7 file', 'games', 'old rating'))
moved = 0
for p, name, new in rows:
    a, b = p['rec'], new['rec']
    if a == b and p['g'] == new['g'] and p['r'] == new['r']:
        continue
    moved += 1
    print('%-18s %-14s %-14s %-11s %s' % (
        name[:18], '%d-%d-%d' % tuple(a), '%d-%d-%d' % tuple(b),
        '%d → %d' % (p['g'], new['g']), '%d → %d' % (p['r'], new['r'])))
print('\n%d of %d rows corrected.' % (moved, len(rows)))
if renames: print('renamed to the workbook spelling:', ', '.join('%s -> %s' % kv for kv in renames.items()))
if missing: print('NOT in the season 7 workbook, left alone:', ', '.join(missing))
print('games in the old era: %d over %d nights (unchanged)' % (A['games'], A['nights']))

if '--write' in sys.argv:
    A['players'] = sorted([new for _, _, new in rows], key=lambda p: -p['r'])
    for old, name in renames.items():
        cur = back.get(old)
        if cur:
            A['link'][cur] = name   # the link points at the spelling the row now uses
    json.dump(A, io.open('archive.json', 'w', encoding='utf-8'), separators=(',', ':'))
    print('\narchive.json written. Run buildsite.py.')
else:
    print('\n(nothing written - pass --write)')
