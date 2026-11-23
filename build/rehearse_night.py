# -*- coding: utf-8 -*-
"""Rehearse a club night, start to finish, without touching the real records.

Submit on the phone is a chain: the night file lands in build/nights/, the
workflow folds it into the records, builds the site and the phone tool, and
check_site refuses anything broken. Every link has failed on a real night, and
each time the first anybody knew was at midnight with the room still full.

This runs the same chain on a made-up night, in a throwaway copy of the repo:
last night's players, two rounds, a bye, a walk-in with a typed rating, and
somebody already on record "added" again with a new rating (the 27 September
fault - their old games must not be re-rated). It fails loudly if any step
does. The workflow runs it on every change to the builders and on the morning
of club night; run it here the same way:  python build/rehearse_night.py
"""
import datetime, io, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WALKIN = "Rehearsal Walk-in"
WALKIN_SEED = 900


def load(root, name):
    return json.load(io.open(os.path.join(root, 'build', name), encoding='utf-8'))


def step(label, cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        tail = ((r.stdout or '') + (r.stderr or '')).strip().splitlines()[-15:]
        raise SystemExit('REHEARSAL FAILED at: %s\n  %s' % (label, '\n  '.join(tail)))
    print('ok   ' + label)


def main():
    tmp = tempfile.mkdtemp(prefix='kava-rehearsal-')
    work = os.path.join(tmp, 'repo')
    try:
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.tmp', 'node_modules'))
        history = load(work, 'history.json')
        roster = load(work, 'roster.json')
        seeds_before = load(work, 'seeds.json')
        on_record = {h["date"] for h in history}

        # the night is dated today, as a real one is; if today is already a
        # night, the next free day
        day = datetime.date.today()
        while day.isoformat() in on_record:
            day += datetime.timedelta(days=1)
        date = day.isoformat()

        # last night's players, in the order they sat down
        last = max(history, key=lambda h: h["date"])
        who = []
        for g in last["games"]:
            for n in g[:2]:
                if n not in who: who.append(n)
        if len(who) < 8:
            raise SystemExit('REHEARSAL FAILED: the last night has fewer than 8 players to borrow')
        p = who[:8]
        games = [[p[0], p[1], "w"], [p[2], p[3], "b"], [p[4], p[5], "d"], [p[6], WALKIN, "w"],
                 [p[0], p[2], "d"], [p[1], p[3], "w"], [WALKIN, p[4], "b"], [p[5], p[6], "w"]]
        night = {"date": date, "games": games, "byes": [[p[7], 2]],
                 # the walk-in starts where they were typed in; the member "added"
                 # again must keep their record, typed rating ignored
                 "seeds": {WALKIN: WALKIN_SEED, p[0]: 500},
                 "new": [{"n": WALKIN, "d": roster["divisions"][-1]}, {"n": p[0], "d": roster["divisions"][0]}]}
        nights_dir = os.path.join(work, 'build', 'nights')
        os.makedirs(nights_dir, exist_ok=True)
        io.open(os.path.join(nights_dir, date + '.json'), 'w', encoding='utf-8').write(json.dumps(night, indent=1))
        print('rehearsing a night dated %s: %d games, a bye, a walk-in, a returning name' % (date, len(games)))

        py = sys.executable
        build = os.path.join(work, 'build')
        step('fold the night into the club records', [py, 'promote_nights.py'], build)
        step('build the site', [py, 'buildsite.py'], build)
        step('build the phone tool', [py, 'buildpairings.py'], build)
        step('refuse a broken build (check_site)', [py, os.path.join('build', 'check_site.py')], work)

        # and what a passing build must also have done
        wrong = []
        hist = load(work, 'history.json')
        mine = [h for h in hist if h["date"] == date]
        if len(mine) != 1 or len(mine[0]["games"]) != len(games):
            wrong.append('the night is not in history.json exactly once')
        if [f for f in os.listdir(nights_dir) if f.endswith('.json')]:
            wrong.append('the night file was not cleared after folding in')
        seeds = load(work, 'seeds.json')
        if seeds.get(WALKIN) != WALKIN_SEED:
            wrong.append('the walk-in did not start at the typed rating')
        if seeds.get(p[0]) != seeds_before.get(p[0]):
            wrong.append('%s is already on record and was given a new starting rating' % p[0])
        if WALKIN not in {q["n"] for q in load(work, 'roster.json')["roster"]}:
            wrong.append('the walk-in did not join the roster')
        for page in ('index.html', 'kava-pairings.html'):
            html = io.open(os.path.join(work, page), encoding='utf-8').read()
            if date not in html: wrong.append('%s does not carry the night' % page)
            if WALKIN not in html: wrong.append('%s does not carry the walk-in' % page)
        if wrong:
            raise SystemExit('REHEARSAL FAILED: the build passed but\n  ' + '\n  '.join(wrong))
        print('REHEARSAL PASSED: a night submitted now would save, build and publish')
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
