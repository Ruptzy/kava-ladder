"""Local server for the photo crop tool. Organiser's PC only, never published.

    python build/photoserver.py            # serves the repo root on http://localhost:8765
    open http://localhost:8765/build/photos.html

POST /save    {name, data}  -> writes photos/<slug>.jpg from a 400x400 JPEG data URL
POST /remove  {name}        -> deletes photos/<slug>.jpg
POST /publish               -> git add photos && git commit && git push, returns the output
GET  /list                  -> {slug: bytes} for every photo on disk
"""
import os, sys, json, re, base64, subprocess, http.server
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
PORT=int(sys.argv[1]) if len(sys.argv)>1 else 8765
def slug(n): return re.sub(r'^-+|-+$','',re.sub(r'[^a-z0-9]+','-',n.lower()))
def git(*a):
    r=subprocess.run(['git']+list(a),cwd=ROOT,capture_output=True,text=True)
    return (r.stdout+r.stderr).strip(), r.returncode

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def log_message(self,*a): pass
    def send_json(self,obj,code=200):
        b=json.dumps(obj).encode(); self.send_response(code)
        self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(b)))
        self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(b)
    def end_headers(self):
        if self.path.startswith('/photos/') or self.path.endswith('.html'): self.send_header('Cache-Control','no-store')
        super().end_headers()
    def do_GET(self):
        if self.path.split('?')[0]=='/list':
            d=os.path.join(ROOT,'photos'); out={}
            if os.path.isdir(d):
                for f in os.listdir(d):
                    if f.endswith('.jpg'): out[f[:-4]]=os.path.getsize(os.path.join(d,f))
            return self.send_json(out)
        return super().do_GET()
    def do_POST(self):
        n=int(self.headers.get('Content-Length') or 0); body=json.loads(self.rfile.read(n) or b'{}')
        if self.client_address[0] not in ('127.0.0.1','::1'): return self.send_json({'error':'local only'},403)
        if self.path=='/save':
            name=body.get('name',''); data=body.get('data','')
            if not name or not data.startswith('data:image/jpeg;base64,'): return self.send_json({'error':'bad request'},400)
            os.makedirs(os.path.join(ROOT,'photos'),exist_ok=True)
            out=os.path.join(ROOT,'photos',slug(name)+'.jpg')
            open(out,'wb').write(base64.b64decode(data.split(',',1)[1]))
            return self.send_json({'ok':True,'file':'photos/'+slug(name)+'.jpg','bytes':os.path.getsize(out)})
        if self.path=='/remove':
            out=os.path.join(ROOT,'photos',slug(body.get('name',''))+'.jpg')
            if os.path.exists(out): os.remove(out)
            return self.send_json({'ok':True})
        if self.path=='/publish':
            log=[]
            for cmd in (['add','photos'],['-c','user.name=Ruptzy','-c','user.email=haroldemanuel002@gmail.com','commit','-m','Photos: '+body.get('msg','update')],['push','origin','main']):
                o,c=git(*cmd); log.append('$ git '+' '.join(cmd)+'\n'+o)
                if c and 'nothing to commit' not in o: return self.send_json({'ok':False,'log':'\n'.join(log)})
            return self.send_json({'ok':True,'log':'\n'.join(log)})
        return self.send_json({'error':'not found'},404)

if __name__=='__main__':
    print('KAVA photo tool: http://localhost:%d/build/photos.html  (serving %s)'%(PORT,ROOT))
    http.server.ThreadingHTTPServer(('127.0.0.1',PORT),H).serve_forever()
