"""Fold each night the phone submitted into the club's own records.

The phone saves a night as build/nights/<date>.json. That file is a hand-off,
not the record: this moves what it carries into history.json (the games and
byes), roster.json (anyone added on the phone that night, as a member) and
seeds.json (the starting rating typed in for them), then removes the file.
The workflow runs it before every build, so the records are always the
whole story and the night files are always empty after a build.

Idempotent: a night already in history.json (same date, or the same games
under a corrected date) is not added twice, a name already on the roster is
left alone, and a seed already set is kept.
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
def here(n): return os.path.join(HERE, n)


def load(name, default):
    try: return json.load(io.open(here(name), encoding='utf-8'))
    except FileNotFoundError: return default


def save(name, data):
    tmp = here(name) + '.tmp'
    io.open(tmp, 'w', encoding='utf-8').write(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
    os.replace(tmp, here(name))


def main():
    d = here('nights')
    files = sorted(f for f in os.listdir(d)) if os.path.isdir(d) else []
    files = [f for f in files if f.endswith('.json')]
    if not files:
        print('no nights to promote'); return 0
    history = load('history.json', [])
    roster = load('roster.json', {"roster": []})
    seeds = load('seeds.json', {})
    dates = {h["date"] for h in history}
    games_seen = {json.dumps(h["games"], sort_keys=True) for h in history}
    names = {p["n"] for p in roster["roster"]}
    done = []
    for f in files:
        night = json.load(io.open(os.path.join(d, f), encoding='utf-8'))
        date = night.get("date")
        for g in night.get("games", []):
            if not (isinstance(g, list) and len(g) == 3 and g[0] and g[1] and g[2] in ("w", "b", "d")):
                print('refusing %s: a game is not [white, black, w|b|d]: %r' % (f, g)); return 1
        key = json.dumps(night.get("games", []), sort_keys=True)
        added = []
        if date and night.get("games") and date not in dates and key not in games_seen:
            history.append({"date": date, "games": night["games"], "byes": night.get("byes", [])})
            dates.add(date); games_seen.add(key); added.append('%d games' % len(night["games"]))
        for q in night.get("new") or []:
            n = q.get("n")
            if not n: continue
            seed = (night.get("seeds") or {}).get(n)
            if n not in names:
                roster["roster"].append({"n": n, "r": int(seed or 1000), "d": q.get("d") or "", "idle": 0})
                names.add(n); added.append('member ' + n)
            if seed is not None and n not in seeds:
                seeds[n] = int(seed)
        os.remove(os.path.join(d, f))
        done.append('%s: %s' % (f, ', '.join(added) or 'already on record'))
    history.sort(key=lambda h: h["date"])
    save('history.json', history); save('roster.json', roster); save('seeds.json', seeds)
    for line in done: print('promoted ' + line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
