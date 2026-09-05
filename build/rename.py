# -*- coding: utf-8 -*-
"""Rename a player everywhere: games, roster, seeds, brackets, archive links,
the import maps and the photo files. Run from build/.

    python rename.py "Sam (mama Smurf)" "Sam"
"""
import json, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def slug(n):
    return re.sub(r'^-+|-+$', '', re.sub(r'[^a-z0-9]+', '-', n.lower()))


def rename(old, new):
    touched = []

    # every game and bye
    p = os.path.join(HERE, 'history.json')
    H = json.load(io.open(p, encoding='utf-8'))
    hits = 0
    for night in H:
        for g in night['games']:
            for i in (0, 1):
                if g[i] == old:
                    g[i] = new
                    hits += 1
        night['byes'] = [new if b == old else b for b in night.get('byes', [])]
    json.dump(H, io.open(p, 'w', encoding='utf-8'), separators=(',', ':'))
    touched.append('history.json (%d game slots)' % hits)

    # roster, seeds, bracket snapshots
    p = os.path.join(HERE, 'roster.json')
    R = json.load(io.open(p, encoding='utf-8'))
    n = 0
    for pl in R['roster']:
        if pl['n'] == old:
            pl['n'] = new
            n += 1
    json.dump(R, io.open(p, 'w', encoding='utf-8'), indent=1)
    touched.append('roster.json (%d)' % n)

    p = os.path.join(HERE, 'seeds.json')
    S = json.load(io.open(p, encoding='utf-8'))
    if old in S:
        S[new] = S.pop(old)
        json.dump(S, io.open(p, 'w', encoding='utf-8'))
        touched.append('seeds.json')

    p = os.path.join(HERE, 'divhistory.json')
    if os.path.exists(p):
        DH = json.load(io.open(p, encoding='utf-8'))
        k = 0
        for s in DH['snapshots']:
            if old in s['div']:
                s['div'][new] = s['div'].pop(old)
                k += 1
        json.dump(DH, io.open(p, 'w', encoding='utf-8'), separators=(',', ':'))
        touched.append('divhistory.json (%d snapshots)' % k)

    # archive links point current name -> old-era name
    p = os.path.join(HERE, 'archive.json')
    A = json.load(io.open(p, encoding='utf-8'))
    if old in A.get('link', {}):
        A['link'][new] = A['link'].pop(old)
        json.dump(A, io.open(p, 'w', encoding='utf-8'), separators=(',', ':'))
        touched.append('archive.json link')

    # so the next import lands on the new name
    for f in ('reimport.py', 'tourneys.py'):
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        if '"%s"' % old in s:
            io.open(p, 'w', encoding='utf-8').write(s.replace('"%s"' % old, '"%s"' % new))
            touched.append(f)

    # photos follow the name
    for d in ('photos', 'originals'):
        a = os.path.join(ROOT, d, slug(old) + '.jpg')
        b = os.path.join(ROOT, d, slug(new) + '.jpg')
        if os.path.exists(a):
            os.replace(a, b)
            touched.append('%s/%s.jpg -> %s.jpg' % (d, slug(old), slug(new)))
    return touched


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(1)
    for line in rename(sys.argv[1], sys.argv[2]):
        print('  ', line)
    print('renamed %r -> %r' % (sys.argv[1], sys.argv[2]))
