import zipfile,re,json,datetime
from xml.etree import ElementTree as ET
P=r"C:\Users\17862\Desktop\Chess EXCEL\Old info\2024-11-24 2023-06-04 Swiss_Bracket_April_18_2024 Backup Backup.xlsx"
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
z=zipfile.ZipFile(P)
ss=[''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
wb=ET.fromstring(z.read('xl/workbook.xml'))
rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
SH={sh.get('name'):(lambda t:t if t.startswith('xl/') else 'xl/'+t.lstrip('/'))(rels[sh.get('{%s}id'%NS['r'])]) for sh in wb.find('m:sheets',NS)}
def grid(n):
    out={}
    for row in ET.fromstring(z.read(SH[n])).iter('{%s}row'%NS['m']):
        rn=int(row.get('r')); c={}
        for cell in row.findall('m:c',NS):
            col=re.sub(r'\d+','',cell.get('r')); t=cell.get('t'); v=cell.find('m:v',NS)
            if v is None: continue
            if t=='s': c[col]=ss[int(v.text)]
            else:
                try: c[col]=float(v.text)
                except: c[col]=v.text
        if c: out[rn]=c
    return out
def unser(n): return datetime.date(1899,12,30)+datetime.timedelta(days=int(n))

stats={}
for rn,c in grid('Ratings by Player').items():
    if rn==1 or not isinstance(c.get('A'),str): continue
    stats[c['A']]=dict(rating=round(c.get('B',0),1),games=int(c.get('C',0)),
        w=int(c.get('D',0)),l=int(c.get('E',0)),d=int(c.get('F',0)),
        wh=[int(c.get('H',0)),int(c.get('I',0)),int(c.get('J',0))],
        bl=[int(c.get('L',0)),int(c.get('M',0)),int(c.get('N',0))])
rows=[]
for rn,c in grid('Matches').items():
    if rn==1: continue
    d,w,b,win=c.get('A'),c.get('C'),c.get('D'),c.get('E')
    if isinstance(d,float) and isinstance(w,str) and isinstance(b,str): rows.append((int(d),w,b,win))
rows.sort()
nights=sorted({r[0] for r in rows})
print('players in Ratings by Player :',len(stats))
print('with at least one game       :',sum(1 for s in stats.values() if s['games']>0))
print('matches                      :',len(rows))
print('club nights                  :',len(nights))
print('date range                   :',unser(nights[0]),'->',unser(nights[-1]))
top=sorted(((n,s) for n,s in stats.items() if s['games']>0),key=lambda kv:-kv[1]['rating'])
print('\ntop 12 by final rating:')
for n,s in top[:12]:
    print('   %-24s %7.1f  %3d games  %d-%d-%d' % (n,s['rating'],s['games'],s['w'],s['d'],s['l']))
json.dump({"stats":stats,"matches":[[unser(d).isoformat(),w,b,('w' if win==w else ('b' if win==b else 'd'))] for d,w,b,win in rows],
           "nights":[unser(n).isoformat() for n in nights]},open('archive_raw.json','w'),separators=(',',':'))
