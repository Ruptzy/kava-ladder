# -*- coding: utf-8 -*-
"""Fill the Feb-March 2025 gap, and put back the byes on two nights.

Harold sent seven tournament links. Five are nights nobody had ever imported:
23 Feb, 9, 16, 23 and 30 March 2025, 114 games between them. The other two turn
out to be nights already on record (5 and 19 October 2025) and their games match
exactly, so nothing is touched there except the byes, which the workbook import
never carried.

Names follow the club's own records. "Bejamin" is Benji, plain "Omar" is Omar
Cruz (Omar Azab does not turn up until January 2026), and "Ben (new)" stays as
written: the club has always used that suffix for a second person with the same
first name, and Benji is on the same night. Anyone with no other appearance in
either era stays a visitor: their games count, but they never join the ladder.
"""
import re, io, html, json, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GAP = os.path.join(HERE, 'gap')

# the seven Harold sent, cached on first run so a rebuild needs no network
LINKS = ["d73fe2352b8f43ebacd03a4bfa1a7e0e", "f6658a12ca8e41389ebc397975db5e8b",
         "098f3d98ebd5440bb909ab4587038b23", "9ef50d5756444cd1a5f55076237c2c6f",
         "78ed8b30c8f743c092f3cf38abaadf22", "36753ce96104430eb84d8e6816af8c06",
         "5155fee756d54125b9b8740a282aed5a"]


def cache():
    if not os.path.isdir(GAP):
        os.makedirs(GAP)
    for i in LINKS:
        f = os.path.join(GAP, i + '.html')
        if os.path.exists(f):
            continue
        u = "https://swissonlinetournament.com/Tournament/Details/%s?allRounds=true" % i
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        io.open(f, 'w', encoding='utf-8').write(
            urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace"))
        print('fetched', i[:8])

DATE = {"Bracket 2/23/25": "2025-02-23", "3/9/25": "2025-03-09", "03/16/25": "2025-03-16",
        "3/23/25 swiss": "2025-03-23", "3/30/25": "2025-03-30",
        "Kava social": "2025-10-05", "Kava social chess club": "2025-10-19"}
CANON = {"bejamin": "Benji", "benji": "Benji", "ben": "Benji",
         "omar": "Omar Cruz", "omar cruz": "Omar Cruz"}


def canon(n):
    return CANON.get(n.strip().lower(), n.strip())


def parse(path):
    doc = io.open(path, encoding='utf-8').read()
    nm = html.unescape(re.search(r"Tournament name:\s*([^<\n]+)", doc).group(1)).strip()
    games, byes = [], []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", doc, re.S):
        tds = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
               for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) >= 4 and re.search(r"\bbye\b", " ".join(tds), re.I):
            if tds[1]:
                byes.append(canon(tds[1]))
            continue
        # a pairing with no result is a round that was set up but never played
        if len(tds) >= 6 and tds[1] and tds[5] and tds[3]:
            games.append([canon(tds[1]), canon(tds[5]),
                          "w" if tds[3] == "1-0" else ("b" if tds[3] == "0-1" else "d")])
    return DATE[nm], nm, games, byes


def scrape():
    cache()
    out = {}
    for i in LINKS:
        d, nm, g, b = parse(os.path.join(GAP, i + '.html'))
        out[d] = (nm, g, b)
    return out

def main():
    scraped = scrape()
    H = json.load(io.open(os.path.join(HERE, 'history.json'), encoding='utf-8'))
    have = {n['date']: n for n in H}

    print('%-12s %-24s %s' % ('date', 'tournament', 'what happened'))
    added = 0
    for d in sorted(scraped):
        nm, g, b = scraped[d]
        if d in have:
            old = have[d]['games']
            same = len(old) == len(g)
            if not same:
                raise SystemExit('%s: %d games on record, %d in the link' % (d, len(old), len(g)))
            was = list(have[d].get('byes') or [])
            have[d]['byes'] = b
            print('%-12s %-24s already on record, byes %s -> %s' % (d, nm, was or '[]', b or '[]'))
        else:
            H.append({"date": d, "games": g, "byes": b})
            added += len(g)
            print('%-12s %-24s NEW: %d games, %d byes' % (d, nm, len(g), len(b)))

    H.sort(key=lambda n: n['date'])
    json.dump(H, io.open(os.path.join(HERE, 'history.json'), 'w', encoding='utf-8'), separators=(',', ':'))
    print('\n%d games added, %d nights now on record (%s .. %s)'
          % (added, len(H), H[0]['date'], H[-1]['date']))


if __name__ == '__main__':
    main()
