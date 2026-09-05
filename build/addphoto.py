"""Add or replace a player's photo on the ladder site.

    python build/addphoto.py "Player Name" path/to/picture.jpg [--focus X,Y]

Writes photos/<slug>.jpg (400x400, square-cropped, ~30 KB). The page finds it by
name on its own, so there is nothing to rebuild: just commit and push photos/.
--focus is where the face is, as fractions of width and height (default 0.5,0.4,
a touch above centre, which suits most portraits). Use 0.5,0.25 for a face near
the top of a tall photo. --zoom is the crop size as a fraction of the shorter side
(default 1 = as big as fits; 0.5 = a tight head-and-shoulders crop).
"""
import sys, os, json, re, difflib
from PIL import Image, ImageOps
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
def slug(n): return re.sub(r'^-+|-+$','',re.sub(r'[^a-z0-9]+','-',n.lower()))
skip=set(); [skip.add(i+1) for i,a in enumerate(sys.argv) if a in ('--focus','--zoom')]
args=[a for i,a in enumerate(sys.argv[1:],1) if not a.startswith('--') and i not in skip]
opts={a.split('=')[0][2:]:a.split('=',1)[1] for a in sys.argv[1:] if a.startswith('--') and '=' in a}
if '--focus' in sys.argv: opts['focus']=sys.argv[sys.argv.index('--focus')+1]
if '--zoom' in sys.argv: opts['zoom']=sys.argv[sys.argv.index('--zoom')+1]
if len(args)<2: print(__doc__); sys.exit(1)
name,src=args[0],args[1]
roster=json.load(open(os.path.join(HERE,'roster.json'),encoding='utf-8'))
names=[p['n'] for p in roster['roster']]
if name not in names:
    close=difflib.get_close_matches(name,names,n=5,cutoff=0.4)
    exact=[n for n in names if n.lower()==name.lower()]
    if exact: name=exact[0]
    else:
        print('No player called %r in roster.json.'%name)
        if close: print('Did you mean:',', '.join(close))
        sys.exit(2)
fx,fy=(float(v) for v in opts.get('focus','0.5,0.4').split(','))
im=ImageOps.exif_transpose(Image.open(src)).convert('RGB')
w,h=im.size; s=max(64,int(min(w,h)*min(1.0,max(0.15,float(opts.get('zoom','1'))))))
left=min(max(0,int(fx*w-s/2)),w-s); top=min(max(0,int(fy*h-s/2)),h-s)
im=im.crop((left,top,left+s,top+s)).resize((400,400),Image.LANCZOS)
os.makedirs(os.path.join(ROOT,'photos'),exist_ok=True)
out=os.path.join(ROOT,'photos',slug(name)+'.jpg')
im.save(out,'JPEG',quality=84,optimize=True,progressive=True)
print('wrote %s (%d KB) for %s'%(os.path.relpath(out,ROOT),os.path.getsize(out)//1024,name))
