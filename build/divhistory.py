# -*- coding: utf-8 -*-
"""Read real bracket membership out of every workbook backup.

Each backup carries the three division sheets as they stood on its own date, so
several backups give a timeline of who was in which bracket. That beats guessing
a bracket from a rating: the club's brackets are hand-assigned and do not follow
the numbers exactly.

Writes divhistory.json: {"snapshots": [{"date": ..., "div": {player: bracket}}]}
"""
import zipfile, json, io, re, os, datetime
from xml.etree import ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
BASE = r'D:/Desktop_Moved/Chess/Chess league Kava Social/Chess rankings NEW 2025'
FILES = [
    ('Season fall_winter 2026/11_2_2025 chess ranking.xlsx', None),
    ('Season fall_winter 2026/2025-11-30 11_2_2025 chess ranking Backup.xlsx', None),
    ('2026-03-22 2025-March 31 backup.xlsx', None),
    ('2026-03-22 2025-11-30 11_2_2025 chess ranking Backup (1) Backup - Copy.xlsx', None),
    ('2026-04-05 2026-03-22 2025-11-30 11_2_2025 chess ranking Backup (1) Backup - Copy Backup.xlsx', None),
]
# the same rename map the game import used, so brackets line up with the ladder
CANON = {'Omar': 'Omar Cruz', 'Brian New': 'Brian O', 'Brian bellamy': 'Brian'}
MONTHS = ('January February March April May June July August September October November December').split()


def sheet_rows(z, rels, name):
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    tgt = None
    for sh in wb.find('m:sheets', NS):
        if sh.get('name') == name:
            tgt = rels[sh.get('{%s}id' % NS['r'])]
    if not tgt:
        return []
    if not tgt.startswith('xl/'):
        tgt = 'xl/' + tgt.lstrip('/')
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall('m:si', NS):
            ss.append(''.join(x.text or '' for x in si.iter('{%s}t' % NS['m'])))
    out = []
    sr = ET.fromstring(z.read(tgt))
    for row in sr.iter('{%s}row' % NS['m']):
        cells = {}
        for c in row.findall('m:c', NS):
            ref = re.sub(r'\d+', '', c.get('r'))
            v = c.find('m:v', NS)
            t = c.get('t')
            if v is None:
                continue
            cells[ref] = ss[int(v.text)] if t == 's' else v.text
        out.append(cells)
    return out


snaps = []
for rel, _ in FILES:
    path = os.path.join(BASE, rel)
    if not os.path.exists(path):
        print('missing', rel)
        continue
    z = zipfile.ZipFile(path)
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    names = [sh.get('name') for sh in wb.find('m:sheets', NS)]
    divs = [n for n in names if re.match(r'^(over|u)\s?\d+$', n.strip(), re.I)]
    div = {}
    asof = None
    for d in divs:
        rows = sheet_rows(z, rels, d)
        for cells in rows:
            a = (cells.get('A') or '').strip()
            if a.startswith('Chess results through') and not asof:
                m = re.search(r'through\s+(\w+)\s+(\d+),\s*(\d{4})', a)
                if m and m.group(1) in MONTHS:
                    asof = datetime.date(int(m.group(3)), MONTHS.index(m.group(1)) + 1, int(m.group(2))).isoformat()
            name = (cells.get('C') or '').strip()
            if name and re.match(r'^\d+$', a or ''):
                div[CANON.get(name, name)] = d
    if not asof:
        m = re.match(r'.*?(\d{4}-\d{2}-\d{2})', os.path.basename(rel))
        asof = m.group(1) if m else None
    snaps.append({'date': asof, 'file': os.path.basename(rel), 'div': div})
    print('%s  as of %s  %d players  %s' % (os.path.basename(rel)[:46], asof, len(div),
                                            {d: sum(1 for v in div.values() if v == d) for d in divs}))

snaps = [s for s in snaps if s['date']]
snaps.sort(key=lambda s: s['date'])
# drop a snapshot that says nothing new
uniq = []
for s in snaps:
    if uniq and uniq[-1]['div'] == s['div']:
        print('   (same as previous, skipping %s)' % s['file'][:40])
        continue
    uniq.append(s)
json.dump({'snapshots': [{'date': s['date'], 'div': s['div']} for s in uniq]},
          io.open('divhistory.json', 'w', encoding='utf-8'), separators=(',', ':'))
print('\nwrote divhistory.json with %d snapshots: %s' % (len(uniq), ', '.join(s['date'] for s in uniq)))

# what actually changed between them
for i in range(1, len(uniq)):
    a, b = uniq[i - 1], uniq[i]
    moved = {n: (a['div'].get(n), b['div'][n]) for n in b['div']
             if a['div'].get(n) and a['div'][n] != b['div'][n]}
    added = [n for n in b['div'] if n not in a['div']]
    print('%s -> %s : %d moved %s | %d new' % (a['date'], b['date'], len(moved), moved or '', len(added)))
