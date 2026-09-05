# -*- coding: utf-8 -*-
"""Build the phone pairing tool (kava-pairings.html at the repo root).

The tool runs the night: check people in, pair the rounds, enter results, then
either copy the results for Discord or publish the whole site straight from the
phone. It carries the same page template as buildsite.py - the ladder it
publishes has to be the identical page - plus the roster, seeds and history it
needs to pair and to replay ratings offline.

It used to be built by hand, which is how its roster drifted a rename and a
removal behind the site, and how it ended up with no charset: every em dash,
middot and half point in the Discord post came out as mojibake.
"""
import json, io, os, base64, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def here(n): return os.path.join(HERE, n)


roster = json.load(io.open(here('roster.json'), encoding='utf-8'))
history = json.load(io.open(here('history.json'), encoding='utf-8'))
seeds = json.load(io.open(here('seeds.json'), encoding='utf-8'))
try:
    hidden = set(json.load(io.open(here('hidden.json'), encoding='utf-8')))
except Exception:
    hidden = set()

# people who have left are not offered for pairing, and their names do not go
# into a file that gets carried about on a phone
DATA = {
    "divisions": roster["divisions"],
    "roster": [p for p in roster["roster"] if p["n"] not in hidden],
    "dormantDays": 90,
    "history": history,
    "seeds": {k: v for k, v in seeds.items() if k not in hidden},
}

logo = base64.b64encode(io.open(os.path.join(ROOT, 'logo.png'), 'rb').read()).decode()
tpl = io.open(here('pairings.tpl.html'), encoding='utf-8').read()

# the page template, shared with the site build so both produce the same ladder
src = io.open(here('ladderbuild.js'), encoding='utf-8').read()
a = tpl.index('/* Builds the public leaderboard')
b = tpl.index('`;\n}\n', a) + len('`;\n}\n')
out = tpl[:a] + src.rstrip() + '\n' + tpl[b:]

out = (out.replace('__DATA__', json.dumps(DATA, separators=(',', ':'), ensure_ascii=False))
          .replace('__LOGO__', 'data:image/png;base64,' + logo))

path = os.path.join(ROOT, 'kava-pairings.html')
io.open(path, 'w', encoding='utf-8').write(out)

for leftover in ('__DATA__', '__LOGO__'):
    assert leftover not in out, leftover
assert '<meta charset="utf-8">' in out[:200], 'no charset: the Discord post will be mojibake'
print('pairings tool -> %s' % path)
print('%d bytes | %d on the roster | %d nights | %d hidden left out'
      % (len(out.encode('utf-8')), len(DATA['roster']), len(history), len(hidden)))
