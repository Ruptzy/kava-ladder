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
import json, io, os, base64
import buildsite

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

# The phone renders the same page from its own copy of the history, so it has to
# arrive already relabelled. Doing the swap only in the site build put every
# removed name straight back the moment Harold published from his phone.
def band_of(r, divisions):
    """Same rule as the page: the bracket is the rating band, and the numbers
    come out of the division names so renaming one keeps working."""
    import re
    nums = [int(re.search(r"(\d+)", d).group(1)) if re.search(r"(\d+)", d) else 0
            for d in divisions]
    for i, d in enumerate(divisions):
        floor = nums[0] if i == 0 else (nums[i + 1] if i + 1 < len(divisions) else None)
        if floor is None or r >= floor:
            return d
    return divisions[-1]


history, seeds = buildsite.anonymise(history, seeds, hidden)

# The roster file carries the club's hand-kept numbers, which drift behind the
# replayed ones - up to sixty points, which is enough to pair two people who
# should not meet. Pair on the same rating the site shows.
rated = buildsite.run(history, seeds)
# the same season bands the site ships, so the phone cannot disagree with it
_season, _vault, _nights = buildsite.split_season(history)
_peaks = buildsite.window_level(rated, buildsite.lookback_start(_season["from"]), _season["from"])
BANDS = buildsite.season_bands(rated, _nights, _peaks, roster["divisions"])
board = []
for p in roster["roster"]:
    if p["n"] in hidden:
        continue
    q = dict(p)
    r = rated.get(p["n"])
    if r and r["n"] > 0:
        q["r"] = round(r["r"])
        q["d"] = BANDS.get(p["n"]) or band_of(q["r"], roster["divisions"])
    board.append(q)
board.sort(key=lambda p: -p["r"])

# people who have left are not offered for pairing, and their names do not go
# into a file that gets carried about on a phone
DATA = {
    "divisions": roster["divisions"],
    "roster": board,
    "dormantDays": 90,
    "history": history,
    # seeds keep every player: dropping the ones who left would change the
    # replay for everybody else. They are relabelled, not removed.
    "seeds": seeds,
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
