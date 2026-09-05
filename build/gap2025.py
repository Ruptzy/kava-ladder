# -*- coding: utf-8 -*-
"""Import club nights from their tournament pages.

Harold sent these in two batches. The first filled February and March 2025 and
put back the byes on two October nights the workbook import had lost. The second
carried the run from December 2024 up to that, closing the gap between the end
of the old records and the start of these.

The date comes from this file, not from the tournament's title, because the club
names them by hand and gets it wrong often enough to matter: two of the December
batch are titled "1/19/24" and "2/2/24" but fall on the club's own fortnightly
Sundays in 2025, and neither of those days in 2024 was a Sunday at all.

24 November 2024 is deliberately not imported. It is the last night of the old
records and is already counted there; bringing it in again would have the club
play it twice.

Names follow the club's own records. "Bejamin" is Benji, plain "Omar" is Omar
Cruz because Omar Azab does not turn up until January 2026, and plain "Sam" is
the Sam who is still playing - 24 November proves that one, being the single
night held by both the old records and a link, so the two name sets can be lined
up by the games themselves. "Ben (new)" stays as written: the club has always
used that suffix for a second person with the same first name. Anyone with no
appearance in either era stays a visitor - their games count, they never join
the ladder.
"""
import re, io, html, json, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GAP = os.path.join(HERE, 'gap')

# tournament id -> the night it actually was
LINKS = {
    "39ed8e601d164845a8d2ea10d6d63209": "2024-11-24",   # already in the old records
    "aa6015b586a2493aa985d6af36ff7b1f": "2024-12-08",
    "e632d3124d8343c4af45ee9202493a54": "2024-12-22",
    "2cbdd8ed26c74773849ead26949f2498": "2025-01-05",
    "e62f6b622039413591d3b1351ea4f1ef": "2025-01-19",   # titled 1/19/24
    "1a2de3126a3e4172856d4bcfe0dbf904": "2025-02-02",   # titled 2/2/24
    "d73fe2352b8f43ebacd03a4bfa1a7e0e": "2025-02-23",
    "f6658a12ca8e41389ebc397975db5e8b": "2025-03-09",
    "098f3d98ebd5440bb909ab4587038b23": "2025-03-16",
    "9ef50d5756444cd1a5f55076237c2c6f": "2025-03-23",
    "78ed8b30c8f743c092f3cf38abaadf22": "2025-03-30",
    "36753ce96104430eb84d8e6816af8c06": "2025-10-05",
    "5155fee756d54125b9b8740a282aed5a": "2025-10-19",
}
# the last night of seasons 1-7, counted there already
ARCHIVED = {"2024-11-24"}

CANON = {"bejamin": "Benji", "benji": "Benji", "ben": "Benji",
         "omar": "Omar Cruz", "omar cruz": "Omar Cruz",
         "jona": "Johnathon", "jonathan": "Johnathon",
         "kande": "Kandee", "soma": "Somarie",
         "sam j": "Sam", "sam": "Sam",
         "dave": "Dave Kecthum"}

# Two people, one first name. The Anthony on these winter nights went 2-10 and
# lost to Maddie, Taylor and Amanda; the Anthony who joined in April 2026 is the
# third strongest player in the club. Everybody else who appears on both sides
# of the gap scores within a few points of their usual rate, so the merge is
# only wrong for this one. He is kept apart until somebody who was there says
# otherwise.
SPLIT = [("anthony", "2026-01-01", "Anthony (2024)")]


def canon(n, date=None):
    k = n.strip().lower()
    for who, before, instead in SPLIT:
        if k == who and date and date < before:
            return instead
    return CANON.get(k, n.strip())


def cache(tid, kind=''):
    """Pages are kept so a rebuild needs no network, and so the club still has
    the record if the tournament site ever loses it."""
    if not os.path.isdir(GAP):
        os.makedirs(GAP)
    f = os.path.join(GAP, kind + tid + '.html')
    if not os.path.exists(f):
        u = ("https://swissonlinetournament.com/Tournament/" +
             ("Rating/%s" % tid if kind else "Details/%s?allRounds=true" % tid))
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        io.open(f, 'w', encoding='utf-8').write(
            urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace"))
        print('fetched', kind + tid[:8])
    return f


def parse(tid):
    date = LINKS[tid]
    doc = io.open(cache(tid), encoding='utf-8').read()
    nm = html.unescape(re.search(r"Tournament name:\s*([^<\n]+)", doc).group(1)).strip()
    games, byes = [], []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, re.S):
        tds = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
               for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) >= 4 and re.search(r"\bbye\b", " ".join(tds), re.I):
            if tds[1]:
                byes.append(canon(tds[1], date))
            continue
        # a pairing with no result is a round that was set up but never played
        if len(tds) >= 6 and tds[1] and tds[5] and tds[3]:
            games.append([canon(tds[1], date), canon(tds[5], date),
                          "w" if tds[3] == "1-0" else ("b" if tds[3] == "0-1" else "d")])
    return nm, games, byes


def scrape():
    return {d: (tid,) + parse(tid) for tid, d in LINKS.items()}


def main():
    scraped = scrape()
    path = os.path.join(HERE, 'history.json')
    H = json.load(io.open(path, encoding='utf-8'))
    have = {n['date']: n for n in H}

    print('%-12s %-24s %s' % ('date', 'tournament', 'what happened'))
    added = 0
    for d in sorted(scraped):
        tid, nm, g, b = scraped[d]
        if d in ARCHIVED:
            print('%-12s %-24s left out: seasons 1-7 already has it' % (d, nm))
        elif d in have:
            if len(have[d]['games']) != len(g):
                raise SystemExit('%s: %d games on record, %d in the link'
                                 % (d, len(have[d]['games']), len(g)))
            # the link is the authority, so the night is taken from it wholesale.
            # The count has to match first, so this only ever changes spelling.
            changed = sum(1 for i in range(len(g)) if tuple(have[d]['games'][i]) != tuple(g[i]))
            was = list(have[d].get('byes') or [])
            have[d]['games'] = g
            have[d]['byes'] = b
            note = 'byes %s -> %s' % (was or '[]', b or '[]')
            if changed:
                note += ', %d name%s corrected' % (changed, '' if changed == 1 else 's')
            print('%-12s %-24s already on record, %s' % (d, nm, note))
        else:
            H.append({"date": d, "games": g, "byes": b})
            added += len(g)
            print('%-12s %-24s NEW: %d games, %d byes' % (d, nm, len(g), len(b)))

    H.sort(key=lambda n: n['date'])
    json.dump(H, io.open(path, 'w', encoding='utf-8'), separators=(',', ':'))
    print('\n%d games added, %d nights now on record (%s .. %s)'
          % (added, len(H), H[0]['date'], H[-1]['date']))


if __name__ == '__main__':
    main()
