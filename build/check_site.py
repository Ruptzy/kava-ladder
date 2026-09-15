"""Refuse to publish a broken build.

The workflow runs this after building and before committing. If anything here
fails, nothing is pushed: the site stays as it was, and the phone's Submit
reports a failed build rather than Discord linking to a broken page. Run it
locally the same way: python build/check_site.py
"""
import io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fail = []


def read(name):
    return io.open(os.path.join(ROOT, name), encoding='utf-8').read()


def data_of(html):
    i = html.index('const D=')
    j = html.index('\nconst $=', i)
    return json.loads(html[i + 8:j].strip().rstrip(';'))


def parses(html, name):
    m = re.search(r'<script>(.*?)</script>', html, re.S)
    if not m:
        fail.append(name + ': no script')
        return
    tmp = os.path.join(ROOT, 'build', '.check-' + re.sub(r'\W', '_', name) + '.js')
    io.open(tmp, 'w', encoding='utf-8').write(m.group(1))
    try:
        r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
        if r.returncode:
            fail.append(name + ': script does not parse: ' + r.stderr.strip()[:300])
    finally:
        os.remove(tmp)


# the ladder
h = read('index.html')
parses(h, 'index.html')
D = data_of(h)
if not D.get('season'):
    fail.append('index.html: no season')
members = [p for p in D['players'] if not p.get('gh')]
if len(members) < 10:
    fail.append('index.html: only %d members on the ladder' % len(members))
photos = [f for f in os.listdir(os.path.join(ROOT, 'photos')) if f.endswith('.jpg')]
if len(D.get('pics', [])) != len(photos):
    fail.append('index.html: %d photos listed, %d in photos/' % (len(D.get('pics', [])), len(photos)))
if len(D.get('tabart', [])) < len(D.get('divisions', [])) + 1:
    fail.append('index.html: bracket artwork missing')
for leftover in ('${DESC}', '${SITE}', '${JSON'):
    if leftover in h:
        fail.append('index.html: unfilled ' + leftover)

# every frozen season it links to
for no in D.get('past', []):
    name = 'season-%d.html' % no
    if not os.path.exists(os.path.join(ROOT, name)):
        fail.append(name + ': missing, but the ladder links to it')
        continue
    ha = read(name)
    parses(ha, name)
    if data_of(ha).get('arch') != no:
        fail.append(name + ': not frozen as season %d' % no)

# the phone tool
t = read('kava-pairings.html')
parses(t, 'kava-pairings.html')
if '__DATA__' in t or '__LOGO__' in t:
    fail.append('kava-pairings.html: data not filled in')
if 'async function publishNight' not in t:
    fail.append('kava-pairings.html: Submit is missing')

if fail:
    print('BUILD REFUSED:')
    for f in fail:
        print('  - ' + f)
    sys.exit(1)
print('build checked: season %s, %d members, %d photos, %d frozen season(s), tool ok'
      % (D['season']['no'], len(members), len(photos), len(D.get('past', []))))
