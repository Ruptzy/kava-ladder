# -*- coding: utf-8 -*-
"""Take somebody off the site.

    python hide.py "Name"        stop listing them
    python hide.py --show "Name" list them again
    python hide.py               show who is hidden

Their games stay in history.json and in the rating replay, so nobody else's
rating, record or game count moves. What goes is the name: out of the roster,
out of the seasons 1-7 table, and - because buildsite.py swaps it for a neutral
label - out of index.html entirely. Run buildsite.py afterwards.

Seeds are left alone. The replay still needs them and seeds.json never reaches
the page.
"""
import json, io, sys


def load(n): return json.load(io.open(n, encoding='utf-8'))
def save(n, d, sep=(',', ': ')): json.dump(d, io.open(n, 'w', encoding='utf-8'), separators=sep)


hidden = load('hidden.json')
args = sys.argv[1:]

if not args:
    print('hidden:', ', '.join(hidden) if hidden else '(nobody)')
    raise SystemExit

show = args[0] == '--show'
name = args[1] if show else args[0]

if show:
    if name not in hidden:
        raise SystemExit('%s is not hidden' % name)
    hidden.remove(name)
    print('%s will be listed again. Put them back in roster.json to give them a '
          'ladder row; without one they show as a visitor.' % name)
else:
    if name in hidden:
        raise SystemExit('%s is already hidden' % name)
    R = load('roster.json')
    n0 = len(R['roster'])
    R['roster'] = [p for p in R['roster'] if p['n'] != name]
    save('roster.json', R)

    A = load('archive.json')
    a0 = len(A['players'])
    A['players'] = [p for p in A['players'] if p['n'] != name]
    A['link'].pop(name, None)
    save('archive.json', A, (',', ':'))

    hidden.append(name)
    print('%s hidden. roster %d -> %d, seasons 1-7 table %d -> %d'
          % (name, n0, len(R['roster']), a0, len(A['players'])))

hidden.sort()
json.dump(hidden, io.open('hidden.json', 'w', encoding='utf-8'), indent=0)
print('now hidden:', ', '.join(hidden) if hidden else '(nobody)')
print('run: python buildsite.py')
