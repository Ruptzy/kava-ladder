# -*- coding: utf-8 -*-
"""Import nights exported from the pairing app the club tried in 2025.

The app exports one `rounds.csv` per tournament - Round;Board;White;Black;Result
- and no date, so the dates come from Harold in a small JSON map:

    python build/import_rounds.py dates.json

    {"C:/Users/17862/Downloads/rounds.csv": "2025-04-13", ...}

Names follow Harold's readings of the exports (Sept 2026): Benjamin, Ben and
Benny are Benji; Briwn is Brian; every spelling of Jonathan is Johnathon;
Andrys is Andres; Schmerick is Derek; David is Dave Kecthum; Haleugh is
Haleigh; plain Omar is Omar Cruz (Omar Azab only arrives in 2026); Dan is a
different person from Daniel; plain Sam is Sam, "Sam j" is Sam J.; Myles is
the same Myles as 2022-23. Kandee, Tanner, Juan, Isa, Ayeh and Shawn stay
visitors: their games count, they are not put on the ladder. A blank result
is an unplayed game and is skipped; "Bye" is a half-point bye, the club's
rule before September 2026. An "F" on a result (forfeit) still counts.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALIAS = {'benjamin': 'Benji', 'ben': 'Benji', 'benny': 'Benji', 'briwn': 'Brian',
         'jona': 'Johnathon', 'jonathan': 'Johnathon', 'jonathon': 'Johnathon', 'johnathan': 'Johnathon',
         'andrys': 'Andres', 'schmerick': 'Derek', 'david': 'Dave Kecthum', 'dave': 'Dave Kecthum',
         'haleugh': 'Haleigh', 'omar': 'Omar Cruz', 'omar new': 'Omar Azab', 'sam j': 'Sam J.'}


def norm(n):
    n = ' '.join(n.split())
    return ALIAS.get(n.lower(), n)


def read_night(path):
    games, byes, skipped = [], [], 0
    with open(path, encoding='utf-8-sig') as fh:
        for row in csv.DictReader(fh, delimiter=';'):
            w, b, res = norm(row['White']), norm(row['Black']), (row['Result'] or '').strip()
            if res.lower() == 'bye' or not b:
                byes.append([w, 0.5]); continue
            if not res:
                skipped += 1; continue
            res = res.replace('F', '')
            r = {'1-0': 'w', '0-1': 'b', '0.5-0.5': 'd'}[res]
            games.append([w, b, r])
    return games, byes, skipped


def main(map_path):
    dates = json.load(open(map_path, encoding='utf-8'))
    hp = os.path.join(HERE, 'history.json')
    history = json.load(open(hp, encoding='utf-8'))
    have = {n['date'] for n in history}
    added = []
    for path, date in sorted(dates.items(), key=lambda kv: kv[1]):
        assert date not in have, '%s is already on record' % date
        games, byes, skipped = read_night(path)
        assert games, path
        night = {'date': date, 'games': games}
        if byes: night['byes'] = byes
        history.append(night); have.add(date)
        added.append((date, os.path.basename(path), len(games), len(byes), skipped))
    history.sort(key=lambda n: n['date'])
    json.dump(history, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for d, f, g, b, s in added:
        print('%s  %-16s %3d games  %d byes  %d unplayed skipped' % (d, f, g, b, s))
    print('history.json: %d nights' % len(history))


if __name__ == '__main__':
    main(sys.argv[1])
