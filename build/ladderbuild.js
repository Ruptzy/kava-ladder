/* Builds the public leaderboard as ONE self-contained HTML file.
   Everything is baked in: no server, no fetch, no keys. Upload it and
   the link works. The only companion file is logo.png next to it.

   The page carries the raw games and the nightly ratings; every stat,
   chart, title and fact is worked out in the browser from those. That
   keeps the phone build and the desktop build identical.              */

function ladderData(P,HISTORY,R,divisions,ARCHIVE,seeds,built){
  const lastDate=HISTORY.length?HISTORY[HISTORY.length-1].date:null;
  const dates=HISTORY.map(h=>h.date);
  const names=[], ni={};
  const id=n=>{ if(ni[n]==null){ ni[n]=names.length; names.push(n) } return ni[n] };
  R.forEach(p=>id(p.n));
  const games=[], byes=[];
  HISTORY.forEach((h,i)=>{
    h.games.forEach(([w,b,r])=>games.push([i,id(w),id(b),r]));
    if(h.byes&&h.byes.length) byes.push([i].concat(h.byes.map(id)));
  });
  const di={}; dates.forEach((d,i)=>di[d]=i);
  const divOf={}; R.forEach(p=>divOf[p.n]=p.d);
  const players=Object.keys(P).filter(n=>P[n].n>0).map(n=>{
    const p=P[n];
    return {n, d:divOf[n]||"", r:Math.round(p.r), rd:Math.round(p.rd), seed:Math.round((seeds&&seeds[n])||1000),
      hist:p.hist.map(x=>[di[x.d],Math.round(x.r),Math.round(x.rd)])};
  }).sort((a,b)=>b.r-a.r);
  let next=null;
  if(dates.length>=3){
    const g=[]; for(let i=1;i<dates.length;i++) g.push(Math.round((new Date(dates[i])-new Date(dates[i-1]))/864e5));
    g.sort((a,b)=>a-b); const med=g[Math.floor(g.length/2)];
    const d=new Date(lastDate+"T12:00"); d.setDate(d.getDate()+med); next=d.toISOString().slice(0,10);
    let guard=0; while(built&&next<built&&guard++<12){ d.setDate(d.getDate()+med); next=d.toISOString().slice(0,10) }
  }
  return {club:"KAVA Social Chess Club", built:built||lastDate, date:lastDate, next, divisions, dates, names, games, byes, players, archive:ARCHIVE||null};
}

function buildLadder(){
  const seeds=(typeof SEEDS!=="undefined"&&SEEDS)?Object.assign({},SEEDS):{};
  R.forEach(p=>{ if(seeds[p.n]==null&&p.r!=null) seeds[p.n]=p.r });
  const P=runRatings(HISTORY,seeds);
  if(!Object.keys(P).some(n=>P[n].n>0)) throw new Error("No games on record yet — play a night first.");
  const built=new Date().toISOString().slice(0,10);
  const D=ladderData(P,HISTORY,R,DATA.divisions,(typeof ARCHIVE!=="undefined"?ARCHIVE:null),seeds,built);
  let SITE="https://ruptzy.github.io/kava-ladder/";
  try{ if(typeof pubCfg==="function"){ const c=pubCfg(); if(c.owner&&c.repo) SITE=siteUrl(c) } }catch(e){}
  const DESC="Club ladder · "+D.games.length+" games over "+D.dates.length+" nights · latest night "+D.date;
  return ladderTemplate(D,SITE,DESC);
}

function ladderTemplate(D,SITE,DESC){
  return `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KAVA Ladder</title>
<meta name="description" content="${DESC}">
<meta name="theme-color" content="#0C0D0E">
<meta property="og:type" content="website"><meta property="og:site_name" content="KAVA Social Chess Club">
<meta property="og:title" content="KAVA Ladder"><meta property="og:description" content="${DESC}">
<meta property="og:url" content="${SITE}"><meta property="og:image" content="${SITE}logo.png">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="${SITE}">
<link rel="icon" href="logo.png" type="image/png"><link rel="apple-touch-icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=JetBrains+Mono:wght@400;700&display=swap">
<style>
:root{--void:#0C0D0E;--panel:#161719;--panel-2:#1E2023;--panel-3:#262A2E;--rule:#24282C;--rule-2:#343A40;
--cream:#FFF6E8;--ink-2:#B3ABA0;--ink-3:#8A8276;--scarlet:#FE273A;--scarlet-dim:#B01523;--scarlet-wash:#1F0F12;
--gain:#3BC79A;--gain-wash:#0F211D;--loss:#F0883E;--loss-wash:#231810;
--fd:"Archivo",system-ui,sans-serif;--fb:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--fm:"JetBrains Mono",ui-monospace,Menlo,monospace}
*{box-sizing:border-box}html{background:var(--void);scroll-behavior:smooth}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important;animation:none!important}}
body{margin:0;background:var(--void);color:var(--cream);font-family:var(--fb);font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}
.w{max-width:1080px;margin:0 auto;padding:0 clamp(.8rem,3vw,2rem) 4rem}
h1,h2,h3{margin:0}button{font:inherit;color:inherit}
a{color:var(--scarlet)}
:focus-visible{outline:2px solid var(--scarlet);outline-offset:2px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.skip{position:absolute;left:-999px;top:.5rem;background:var(--scarlet);color:#fff;padding:.5rem .8rem;border-radius:4px;z-index:50;font-weight:700}
.skip:focus{left:.5rem}
.top .w{padding-bottom:0}
.top{border-bottom:1px solid var(--rule);background:radial-gradient(130% 200% at 6% 0%,#241318 0%,var(--void) 60%)}
.tb{display:flex;align-items:center;gap:.9rem;padding:1rem 0 .8rem;flex-wrap:wrap}
.tb img{width:56px;height:56px;border-radius:50%;box-shadow:0 0 34px -6px rgba(254,39,58,.6);flex:none}
.wm{margin-right:auto}.wm b{display:block;font-family:var(--fd);font-variation-settings:"wdth" 122,"wght" 900;font-size:1.5rem;letter-spacing:.03em;line-height:1}
.wm small{font-family:var(--fm);font-size:.55rem;letter-spacing:.3em;color:var(--ink-3);text-transform:uppercase}
.upd{font-family:var(--fm);font-size:.62rem;letter-spacing:.08em;color:var(--ink-3);text-transform:uppercase;line-height:1.7;text-align:right}
.upd b{color:var(--cream);font-weight:700}
.upd.fresh b.d{color:var(--gain)}
.howbtn{background:none;border:1px solid var(--rule-2);border-radius:20px;padding:.35rem .7rem;font-family:var(--fm);font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2);cursor:pointer;white-space:nowrap}
.howbtn:hover{border-color:var(--scarlet);color:var(--scarlet)}
.srch{position:relative;flex:1 1 220px;max-width:340px}
.srch input{width:100%;background:var(--panel);border:1px solid var(--rule-2);border-radius:8px;color:var(--cream);font:inherit;font-size:.95rem;padding:.55rem .8rem .55rem 2.1rem}
.srch input::placeholder{color:var(--ink-3)}
.srch input:focus{border-color:var(--scarlet);outline:none}
.srch svg{position:absolute;left:.7rem;top:50%;transform:translateY(-50%);width:15px;height:15px;stroke:var(--ink-3);fill:none;stroke-width:2}
.sres{position:absolute;left:0;right:0;top:calc(100% + .3rem);background:var(--panel-2);border:1px solid var(--rule-2);border-radius:8px;z-index:40;overflow:hidden;box-shadow:0 14px 30px -10px rgba(0,0,0,.8)}
.sres button{display:flex;width:100%;gap:.6rem;align-items:baseline;background:none;border:none;border-bottom:1px solid var(--rule);padding:.55rem .8rem;text-align:left;cursor:pointer}
.sres button:last-child{border-bottom:none}
.sres button:hover,.sres button.on{background:var(--panel-3)}
.sres b{font-weight:600}.sres span{font-family:var(--fm);font-size:.66rem;color:var(--ink-3);margin-left:auto;white-space:nowrap}
.sres .no{padding:.6rem .8rem;color:var(--ink-3);font-size:.88rem}
.tabs{display:flex;flex-wrap:wrap}
.tabs button{background:none;border:none;border-bottom:2px solid transparent;color:var(--ink-3);font-family:var(--fm);
font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;padding:.7rem .85rem;cursor:pointer;white-space:nowrap}
.tabs button[aria-selected=true]{color:var(--cream);border-bottom-color:var(--scarlet)}
.tabs .n{color:var(--ink-3);margin-left:.4rem}
.tabs .sm{display:none}
/* last night */
.ln{margin:1.2rem 0 0;border:1px solid var(--rule-2);border-radius:6px;background:linear-gradient(160deg,#1B1417,var(--panel) 60%);overflow:hidden}
.ln .lh{display:flex;align-items:baseline;gap:.8rem;padding:.7rem 1rem;border-bottom:1px solid var(--rule);flex-wrap:wrap}
.ln .lh b{font-family:var(--fd);font-variation-settings:"wdth" 116,"wght" 900;font-size:1.05rem;text-transform:uppercase;letter-spacing:.02em}
.ln .lh b span{color:var(--scarlet)}
.ln .lh small{font-family:var(--fm);font-size:.62rem;letter-spacing:.1em;color:var(--ink-3);text-transform:uppercase}
.ln .lh button{margin-left:auto}
.lg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--rule);margin:0}
.lg>div{background:var(--panel);padding:.7rem .9rem;cursor:default}
.lg>div[data-n]{cursor:pointer}.lg>div[data-n]:hover{background:var(--panel-2)}
.lg dt{font-family:var(--fm);font-size:.55rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);margin-bottom:.25rem}
.lg dd{margin:0;font-family:var(--fd);font-variation-settings:"wdth" 110,"wght" 800;font-size:1.15rem;line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lg dd small{display:block;font-family:var(--fm);font-weight:400;font-size:.66rem;color:var(--ink-2);margin-top:.2rem;white-space:normal}
.lg dd .u{color:var(--gain)}
.recap{display:none;border-top:1px solid var(--rule)}
.ln.open .recap{display:grid;grid-template-columns:1fr 1fr}
.recap>div{padding:.8rem 1rem;min-width:0}
.recap>div+div{border-left:1px solid var(--rule)}
.recap h4{margin:0 0 .5rem;font-family:var(--fm);font-size:.55rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);font-weight:500}
.recap table{font-size:.86rem}.recap td{padding:.3rem .3rem;border-bottom:1px solid var(--rule)}
.recap tr[data-n]{cursor:pointer}.recap tr[data-n]:hover td{color:var(--scarlet)}
.recap td.n{font-family:var(--fm);font-size:.76rem;color:var(--ink-3);text-align:right}
.recap td.res{font-family:var(--fm);font-weight:700;text-align:center;color:var(--ink-3);width:2.4rem}
.recap td.win{color:var(--cream);font-weight:600}
/* podium */
.pod{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.8rem;margin:1.2rem 0}
.pc{position:relative;background:linear-gradient(160deg,var(--panel-2),var(--panel) 62%);border:1px solid var(--rule-2);
border-radius:4px;padding:1rem;overflow:hidden;cursor:pointer;text-align:left;min-width:0}
.pc.one{border-color:var(--scarlet);background:linear-gradient(160deg,#2A1319,var(--panel) 68%);box-shadow:0 0 40px -18px var(--scarlet)}
.pc .rk{position:absolute;right:.4rem;top:-.6rem;font-family:var(--fd);font-variation-settings:"wdth" 78,"wght" 900;
font-size:5rem;line-height:1;color:var(--rule-2)}
.pc.one .rk{color:rgba(254,39,58,.3)}
.pc .nm{position:relative;font-family:var(--fd);font-variation-settings:"wdth" 108,"wght" 800;font-size:1.25rem;margin-bottom:.4rem;padding-right:2.4rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pc .rt{position:relative;font-family:var(--fm);font-size:1.9rem;font-weight:700;line-height:1}
.pc .rt sub{font-size:.36em;font-weight:400;color:var(--ink-3);vertical-align:.35em;margin-left:.3rem}
/* section heads */
.sh{display:flex;align-items:baseline;gap:.8rem;margin:2rem 0 .7rem;padding-bottom:.5rem;border-bottom:2px solid var(--rule-2);flex-wrap:wrap}
.sh h2{font-family:var(--fd);font-variation-settings:"wdth" 118,"wght" 900;font-size:clamp(1.15rem,3vw,1.6rem);text-transform:uppercase;white-space:nowrap}
.sh h2 span{color:var(--scarlet)}
.sh p{margin:0 0 0 auto;font-family:var(--fm);font-size:.6rem;letter-spacing:.11em;color:var(--ink-3);text-transform:uppercase}
p.l{max-width:66ch;color:var(--ink-2);margin:0 0 .9rem;font-size:.92rem}
.box{border:1px solid var(--rule-2);border-radius:3px;overflow:hidden;background:var(--panel)}
.sc{overflow-x:auto}
table{border-collapse:collapse;width:100%}
th{font-family:var(--fm);font-size:.55rem;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-3);
text-align:left;padding:.55rem .6rem;background:#101113;border-bottom:1px solid var(--rule-2);white-space:nowrap;font-weight:500}
td{padding:.5rem .6rem;border-bottom:1px solid var(--rule)}
tbody tr[data-n]{cursor:pointer}tbody tr[data-n]:hover,tbody tr[data-n]:focus-visible{background:var(--panel-2);outline:none}
tbody tr[data-n]:focus-visible td.nmc2{box-shadow:inset 3px 0 0 var(--scarlet)}
th.r,td.r{text-align:right}
td.k{font-family:var(--fm);font-size:1rem;font-weight:700;color:var(--ink-2);width:1px;padding-left:1rem;position:relative}
td.k::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:transparent}
tr.one td.k{color:var(--scarlet)}tr.one td.k::before{background:var(--scarlet)}
tr.one td{background:linear-gradient(90deg,var(--scarlet-wash),transparent 55%)}
.nmc{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:14rem;display:inline-block;vertical-align:middle}
tr[data-n]:hover .nmc{color:var(--scarlet)}
td .chev{display:none;color:var(--ink-3);margin-left:.3rem}
.rat{font-family:var(--fm);font-size:1.05rem;font-weight:700}
.rdv{font-family:var(--fm);font-size:.6rem;color:var(--ink-3);display:block}
.dl{font-family:var(--fm);font-weight:700;white-space:nowrap;font-size:1rem}
.dl.u{color:var(--gain)}.dl.d{color:var(--loss)}.dl.f{color:var(--ink-3);font-weight:400;font-size:.8rem}
.wdl{font-family:var(--fm);font-size:.76rem;color:var(--ink-2);white-space:nowrap}
.wdl i{color:var(--ink-3);font-style:normal}
.spk{display:block;width:60px;height:18px}
tr.pv td{background:#131416}
tr.pv td.k{color:var(--rule-2)}
.sortwrap{position:relative;margin:0 0 .8rem}
.sorts{display:flex;gap:.4rem;flex-wrap:wrap}
.sorts button{background:var(--panel);border:1px solid var(--rule-2);border-radius:20px;padding:.4rem .8rem;
font-family:var(--fm);font-size:.62rem;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-2);cursor:pointer;white-space:nowrap;scroll-snap-align:start}
.sorts button[aria-pressed=true]{background:var(--scarlet-wash);border-color:var(--scarlet);color:var(--scarlet);font-weight:700}
.rule-note{font-family:var(--fm);font-size:.6rem;color:var(--ink-3);letter-spacing:.04em;margin:-.3rem 0 .6rem}
.showaway{width:100%;margin-top:.7rem;background:none;border:1px dashed var(--rule-2);border-radius:8px;
padding:.7rem;color:var(--ink-3);font-family:var(--fm);font-size:.63rem;letter-spacing:.1em;
text-transform:uppercase;cursor:pointer}
.showaway:hover{border-color:var(--scarlet);color:var(--scarlet)}
#awayBox{margin-top:.5rem}
.gh{padding:.5rem .7rem .5rem 1rem;background:#101113;border-top:1px solid var(--rule-2);border-bottom:1px solid var(--rule);
font-family:var(--fm);font-size:.57rem;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-3)}
.gh small{text-transform:none;letter-spacing:0;font-size:.62rem;color:var(--ink-3);margin-left:.6rem}
/* crosstable */
.xt{overflow:auto;border:1px solid var(--rule-2);border-radius:4px;background:var(--panel);max-height:80vh}
.xt table{width:auto;border-collapse:separate;border-spacing:0}
.xt th,.xt td{border-right:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.xt thead th{position:sticky;top:0;z-index:3;background:#0F1012;height:132px;vertical-align:bottom;padding:0 0 .5rem}
.xt thead th.c{left:0;z-index:5;min-width:216px;text-align:left;vertical-align:bottom;padding:0 .8rem .6rem;
font-family:var(--fm);font-size:.55rem;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-3);line-height:1.5}
.xt .vt{writing-mode:vertical-rl;transform:rotate(180deg);font-family:var(--fb);font-size:.8rem;font-weight:600;
color:var(--ink-2);white-space:nowrap;padding:.4rem .1rem;max-height:116px;overflow:hidden}
.xt .vt b{color:var(--ink-3);font-family:var(--fm);font-size:.62rem;font-weight:400;margin-bottom:.35rem}
.xt tbody th{position:sticky;left:0;z-index:2;background:var(--panel);text-align:left;padding:.35rem .8rem;
white-space:nowrap;min-width:216px;border-right:2px solid var(--rule-2);cursor:pointer}
.xt tbody th .rn{font-family:var(--fm);font-size:.72rem;color:var(--ink-3);display:inline-block;width:1.6rem}
.xt tbody th .nm2{font-weight:600;font-size:.9rem}
.xt tbody th .r2{font-family:var(--fm);font-size:.68rem;color:var(--ink-3);float:right;margin-left:.9rem}
.xt tbody tr:hover th{background:var(--panel-2)}
.xt tbody tr:hover th .nm2{color:var(--scarlet)}
.xt td{width:54px;min-width:54px;height:42px;text-align:center;font-family:var(--fm);
font-size:.86rem;font-weight:700;color:var(--ink-3);cursor:pointer}
.xt td.self{background:repeating-linear-gradient(45deg,#191B1E,#191B1E 5px,#141619 5px,#141619 10px);cursor:default}
.xt td.none{color:#3A4046}
.w1{background:#132520;color:#4FBE96}
.w2{background:#153328;color:#5CD0A4}
.w3{background:#18452F;color:#72E2B6}
.w4{background:#1B5A3A;color:#93F3CC}
.l1{background:#281B12;color:#D0803F}
.l2{background:#33200F;color:#E0904A}
.l3{background:#43290F;color:#F0A25C}
.l4{background:#573510;color:#FFBA78}
.lev{background:var(--panel-2);color:var(--ink-2)}
.xt tbody tr:hover td{box-shadow:inset 0 0 0 1px rgba(255,246,232,.12)}
.key{display:flex;gap:1rem;flex-wrap:wrap;margin-top:.6rem;font-family:var(--fm);font-size:.62rem;color:var(--ink-3)}
.key i{display:inline-block;width:18px;height:10px;vertical-align:-.05em;margin-right:.3rem;border-radius:2px}
.xlist{display:none}
.xsel{display:flex;gap:.6rem;align-items:center;margin-bottom:.8rem}
.xrow{display:grid;grid-template-columns:1fr auto auto;gap:.8rem;align-items:center;padding:.5rem .8rem;border-bottom:1px solid var(--rule);cursor:pointer}
.xrow:hover{background:var(--panel-2)}
.xrow b{font-weight:600}
.xrow .net{font-family:var(--fm);font-weight:700;padding:.2rem .5rem;border-radius:4px;min-width:3rem;text-align:center}
.xrow .rc{font-family:var(--fm);font-size:.72rem;color:var(--ink-3);min-width:3.6rem;text-align:right}
.xbtn{width:100%;background:var(--panel);border:1px solid var(--rule-2);border-radius:8px;padding:.85rem;color:var(--ink-2);font-family:var(--fm);font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;margin-bottom:.8rem}
.xbtn:hover{border-color:var(--scarlet);color:var(--scarlet)}
/* profile */
.back{background:none;border:none;cursor:pointer;padding:.45rem 0;font-family:var(--fm);font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin-bottom:1.2rem}
.back:hover{color:var(--scarlet)}
.card{background:var(--panel);border:1px solid var(--rule-2);border-radius:3px;padding:1rem;min-width:0}
.card h3{font-family:var(--fm);font-size:.58rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);font-weight:500;margin-bottom:.8rem}
.cap{margin:.6rem 0 0;font-family:var(--fm);font-size:.6rem;color:var(--ink-3);line-height:1.6}
.hid{display:none!important}
.pnick{display:inline-flex;align-items:center;gap:.5rem;background:var(--scarlet-wash);
border:1px solid var(--scarlet-dim);border-radius:100px;padding:.45rem .7rem .45rem .8rem;
font-family:var(--fm);font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;
color:var(--scarlet);margin-bottom:1rem;position:relative;cursor:pointer;outline:none}
.pnick .ni{font-size:1rem;line-height:1}
.pnick .q{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;
border:1px solid var(--scarlet-dim);font-size:.7rem;margin-left:.2rem;opacity:.85;letter-spacing:0}
.pnick .tip{position:absolute;top:calc(100% + .5rem);left:0;z-index:20;width:max-content;max-width:min(300px,86vw);
background:var(--panel-2);border:1px solid var(--scarlet-dim);border-radius:8px;padding:.6rem .75rem;
font-family:var(--fb);font-size:.86rem;letter-spacing:0;text-transform:none;color:var(--cream);
line-height:1.45;box-shadow:0 10px 30px -10px rgba(0,0,0,.8);opacity:0;visibility:hidden;transition:opacity .12s}
.pnick:hover .tip,.pnick:focus-visible .tip,.pnick.open .tip{opacity:1;visibility:visible}
.pnick .tip b{color:var(--scarlet);display:block;font-family:var(--fm);font-size:.58rem;
letter-spacing:.14em;text-transform:uppercase;margin-bottom:.25rem}
.phead2{padding-bottom:1.2rem;border-bottom:2px solid var(--rule-2);margin-bottom:1.3rem}
.phead2 h1{font-family:var(--fd);font-variation-settings:"wdth" 118,"wght" 900;
font-size:clamp(2.1rem,8vw,4rem);letter-spacing:-.035em;line-height:.92;margin-bottom:.5rem;overflow-wrap:anywhere}
.psub{font-family:var(--fm);font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);display:flex;gap:.7rem;flex-wrap:wrap;align-items:center}
.pill{display:inline-block;border:1px solid var(--rule-2);border-radius:20px;padding:.15rem .55rem;font-size:.58rem;color:var(--ink-2);letter-spacing:.1em}
.pill.set{border-color:var(--loss);color:var(--loss)}
.pact{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.9rem;align-items:center}
.cmpbtn{background:var(--scarlet);border:none;border-radius:20px;padding:.5rem .95rem;color:#fff;font-weight:700;font-size:.85rem;cursor:pointer}
.cmpbtn:hover{background:#ff4455}
.chip{background:var(--panel);border:1px solid var(--rule-2);border-radius:20px;padding:.4rem .75rem;font-size:.8rem;color:var(--ink-2);cursor:pointer}
.chip:hover{border-color:var(--scarlet);color:var(--scarlet)}
.chip small{font-family:var(--fm);font-size:.58rem;color:var(--ink-3);letter-spacing:.08em;text-transform:uppercase;margin-right:.35rem}
.kpis{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:1px;background:var(--rule);
border:1px solid var(--rule-2);border-radius:4px;overflow:hidden;margin:0 0 1.1rem}
.kpis>div{background:var(--panel);padding:.8rem .9rem;min-width:0}
.kpis dt{font-family:var(--fm);font-size:.55rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);margin-bottom:.3rem}
.kpis dd{margin:0;font-family:var(--fm);font-size:1.45rem;font-weight:700;line-height:1}
.kpis dd small{display:block;font-size:.44em;font-weight:400;color:var(--ink-3);margin-top:.35rem;letter-spacing:.04em}
.facts{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.6rem;margin-bottom:1.2rem}
.fact{background:linear-gradient(160deg,var(--panel-2),var(--panel) 70%);border:1px solid var(--rule-2);
border-radius:4px;padding:.8rem .85rem;position:relative;overflow:hidden;min-width:0}
.fact .ic{font-size:1.1rem;line-height:1;margin-bottom:.4rem}
.fact b{display:block;font-family:var(--fd);font-variation-settings:"wdth" 110,"wght" 800;
font-size:1.3rem;line-height:1.05;margin-bottom:.2rem;overflow-wrap:anywhere}
.fact span{font-size:.8rem;color:var(--ink-2);line-height:1.4;display:block}
.gwrap{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.9rem;margin-bottom:.9rem;align-items:stretch}
.gwide{grid-column:1/-1}
.strip{display:flex;gap:3px;flex-wrap:wrap}
.strip i{width:20px;height:26px;border-radius:2px;display:grid;place-items:center;font-family:var(--fm);
font-size:.6rem;font-weight:700;color:#0C0D0E}
.strip i.W{background:var(--gain)}.strip i.L{background:var(--loss)}
.strip i.D{background:var(--rule-2);color:var(--ink-2)}
.att{display:flex;gap:3px;flex-wrap:wrap}
.att i{width:13px;height:22px;border-radius:2px;background:var(--rule)}
.att i.on{background:var(--scarlet)}
.bandrow{display:grid;grid-template-columns:6.6rem 1fr 3.4rem;gap:.6rem;align-items:center;margin-bottom:.45rem}
.bandrow .lb{font-family:var(--fm);font-size:.6rem;color:var(--ink-3);text-transform:uppercase;letter-spacing:.06em}
.bar{height:20px;background:var(--panel-3);border-radius:2px;overflow:hidden;display:flex}
.bar i{display:block;height:100%}
.bar i.bw{background:var(--gain)}.bar i.bd{background:var(--rule-2)}.bar i.bl{background:var(--loss)}
.bandrow .vv{font-family:var(--fm);font-size:.74rem;text-align:right;color:var(--ink-2)}
.riv{display:grid;grid-template-columns:7rem 1fr 2.6rem;gap:.6rem;align-items:center;margin-bottom:.4rem;font-size:.84rem}
.riv:hover span:first-child{color:var(--scarlet)}
.riv .rb{height:18px;position:relative;background:var(--panel-3);border-radius:2px}
.riv .rb i{position:absolute;top:0;bottom:0;display:block}
.riv .rb i.p{background:var(--gain);left:50%}
.riv .rb i.m{background:var(--loss);right:50%}
.riv .rb .mid{position:absolute;left:50%;top:0;bottom:0;width:1px;background:var(--rule-2)}
.riv .rv{font-family:var(--fm);font-size:.76rem;text-align:right;font-weight:700}
.rg{width:100%;font-size:.86rem}.rg td{padding:.35rem .3rem;border-bottom:1px solid var(--rule);white-space:nowrap}
.rg td.d{font-family:var(--fm);font-size:.7rem;color:var(--ink-3)}
.rg td.o{font-weight:600;cursor:pointer;max-width:10rem;overflow:hidden;text-overflow:ellipsis}.rg td.o:hover{color:var(--scarlet)}
.card .rg-wrap{overflow-x:auto}
.rg .cc{display:inline-block;width:10px;height:14px;border-radius:2px;vertical-align:-2px;margin-right:.35rem}
.rg .cc.cw{background:var(--cream)}.rg .cc.cb{background:#0C0D0E;border:1px solid var(--rule-2)}
.rg td.rs{font-family:var(--fm);font-weight:700;text-align:center;width:2rem}
.rg td.rs.W{color:var(--gain)}.rg td.rs.L{color:var(--loss)}.rg td.rs.D{color:var(--ink-2)}
.rg td.dl2{font-family:var(--fm);font-size:.74rem;text-align:right}
.tl{list-style:none;margin:0;padding:0 0 0 .2rem;border-left:2px solid var(--rule-2)}
.tl li{position:relative;padding:0 0 .7rem 1rem;font-size:.86rem}
.tl li::before{content:"";position:absolute;left:-7px;top:.35rem;width:10px;height:10px;border-radius:50%;background:var(--scarlet);border:2px solid var(--void)}
.tl li small{display:block;font-family:var(--fm);font-size:.6rem;color:var(--ink-3);letter-spacing:.06em}
.tl li b{font-weight:600}
/* compare */
.cmpsel{display:flex;align-items:center;gap:.7rem;flex-wrap:wrap;margin-bottom:1rem}
.cmpsel label{font-family:var(--fm);font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3)}
.cmpsel select,.xsel select{appearance:none;background:var(--panel-2);color:var(--cream);border:1px solid var(--rule-2);
border-radius:8px;padding:.55rem 2.2rem .55rem .8rem;font-family:var(--fb);font-size:.92rem;cursor:pointer;flex:1;min-width:180px;
background-image:linear-gradient(45deg,transparent 50%,var(--ink-3) 50%),linear-gradient(135deg,var(--ink-3) 50%,transparent 50%);
background-position:calc(100% - 17px) 52%,calc(100% - 12px) 52%;background-size:5px 5px;background-repeat:no-repeat}
.cmpsel select:hover,.xsel select:hover{border-color:var(--scarlet)}
.vsbar{display:grid;grid-template-columns:1fr auto 1fr;gap:1rem;align-items:center;
background:linear-gradient(160deg,var(--panel-2),var(--panel) 70%);border:1px solid var(--rule-2);
border-radius:8px;padding:1rem;margin-bottom:1.1rem}
.vsbar .side{min-width:0;text-align:center}
.vsbar .side b{display:block;font-family:var(--fd);font-variation-settings:"wdth" 112,"wght" 800;
font-size:1.15rem;line-height:1.1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.vsbar .side span{font-family:var(--fm);font-size:.68rem;color:var(--ink-3)}
.vsbar .side em{display:block;font-style:normal;font-family:var(--fm);font-size:.52rem;letter-spacing:.16em;
text-transform:uppercase;color:var(--scarlet);margin-top:.25rem}
.vsbar .mid{text-align:center}
.vsbar .mid .sc2{font-family:var(--fm);font-size:2rem;font-weight:700;line-height:1;white-space:nowrap}
.vsbar .mid em{display:block;font-style:normal;font-family:var(--fm);font-size:.5rem;letter-spacing:.2em;
text-transform:uppercase;color:var(--ink-3);margin-bottom:.35rem}
.cgrp{font-family:var(--fm);font-size:.55rem;letter-spacing:.18em;text-transform:uppercase;color:var(--scarlet);margin:.9rem 0 .5rem;padding-bottom:.25rem;border-bottom:1px solid var(--rule)}
.cmprow{margin-bottom:.75rem}
.cmprow .lab{text-align:center;font-family:var(--fm);font-size:.55rem;letter-spacing:.16em;
text-transform:uppercase;color:var(--ink-3);margin-bottom:.3rem}
.cmprow .line{display:grid;grid-template-columns:3.4rem 1fr 3.4rem;gap:.6rem;align-items:center}
.cmprow .va,.cmprow .vb{font-family:var(--fm);font-size:.88rem;font-weight:700;color:var(--ink-2)}
.cmprow .va{text-align:right}
.cmprow .va.win,.cmprow .vb.win{color:var(--gain)}
.cmpbar{display:flex;height:9px;border-radius:5px;overflow:hidden;background:var(--panel-3)}
.cmpbar i{display:block;height:100%}
.cmpbar i.a{background:var(--rule-2)}.cmpbar i.b{background:var(--rule-2)}
.cmpbar i.a.win{background:var(--gain)}.cmpbar i.b.win{background:var(--gain)}
/* modal */
.modal{position:fixed;inset:0;background:rgba(0,0,0,.72);display:none;align-items:flex-start;justify-content:center;z-index:60;padding:4vh 1rem;overflow:auto}
.modal.open{display:flex}
.mbox{background:var(--panel);border:1px solid var(--rule-2);border-radius:10px;max-width:560px;width:100%;padding:1.2rem 1.3rem 1.4rem;position:relative}
.mbox h2{font-family:var(--fd);font-variation-settings:"wdth" 116,"wght" 900;font-size:1.3rem;text-transform:uppercase;margin-bottom:.8rem}
.mbox h2 span{color:var(--scarlet)}
.mbox .x{position:absolute;right:.7rem;top:.7rem;background:none;border:1px solid var(--rule-2);border-radius:50%;width:32px;height:32px;cursor:pointer;color:var(--ink-2)}
.faq{margin:0}.faq dt{font-weight:700;margin-top:.8rem}.faq dd{margin:.15rem 0 0;color:var(--ink-2);font-size:.92rem}
footer{margin-top:3rem;padding:1.2rem 0 3rem;border-top:1px solid var(--rule);font-family:var(--fm);font-size:.6rem;color:var(--ink-3);line-height:1.9}
/* phones */
@media(max-width:640px){
  .tb{gap:.6rem;padding:.8rem 0 .6rem}
  .tb img{width:44px;height:44px}
  .wm b{font-size:1.2rem}
  .upd{text-align:left;flex:1 1 100%;order:5;line-height:1.5}
  .srch{flex:1 1 100%;max-width:none;order:4}
  .howbtn{order:3}
  .tabs .lg{display:none}.tabs .sm{display:inline}
  .tabs button{padding:.6rem .6rem;font-size:.64rem}
  .pod{gap:.4rem;margin:.9rem 0}
  .pc{padding:.55rem .6rem .5rem}
  .pc .rk{font-size:2.6rem;top:-.3rem;right:.2rem}
  .pc .nm{font-size:.86rem;padding-right:1.3rem;margin-bottom:.2rem}
  .pc .rt{font-size:1.2rem}.pc .rt sub{display:none}
  .sh{margin:1.5rem 0 .6rem}.sh p{margin-left:0;flex:1 1 100%}
  .sortwrap::after{content:"";position:absolute;right:0;top:0;bottom:0;width:36px;background:linear-gradient(90deg,transparent,var(--void));pointer-events:none}
  .sorts{flex-wrap:nowrap;overflow-x:auto;scroll-snap-type:x mandatory;padding-right:2rem;-webkit-overflow-scrolling:touch;scrollbar-width:none}
  .sorts::-webkit-scrollbar{display:none}
  .hm{display:none!important}
  td .chev{display:inline}
  .nmc{max-width:9.5rem}
  td,th{padding:.5rem .45rem}
  td.k{padding-left:.7rem}
  .lg{display:flex;overflow-x:auto;scrollbar-width:none;gap:1px}.lg::-webkit-scrollbar{display:none}
  .lg>div{flex:0 0 46%;min-width:150px}
  .ln .lh{padding:.55rem .8rem}.ln .lh b{font-size:.95rem}
  .sh p{display:none}
  .ln.open .recap{grid-template-columns:1fr}
  .recap>div+div{border-left:none;border-top:1px solid var(--rule)}
  .xt{display:none}.xlist{display:block}.key{display:none}
  .kpis{grid-template-columns:1fr 1fr}
  .facts{grid-template-columns:1fr 1fr}
  .gwrap{grid-template-columns:1fr}
  .riv{grid-template-columns:5.5rem 1fr 2.4rem}
  .bandrow{grid-template-columns:5.6rem 1fr 3.2rem}
}
@media(min-width:641px) and (max-width:900px){
  .gwrap{grid-template-columns:1fr 1fr}
  .facts{grid-template-columns:repeat(3,1fr)}
  .kpis{grid-template-columns:repeat(3,1fr)}
}
@media print{.top,.sorts,.showaway,.xbtn,.back,footer{display:none}body{background:#fff;color:#000}}
</style></head><body>
<a class="skip" href="#ladder">Skip to the ladder</a>
<div class="top"><div class="w">
<div class="tb"><img src="logo.png" alt="KAVA Social Chess Club" width="56" height="56">
<div class="wm"><b>KAVA</b><small>Social Chess Club</small></div>
<div class="srch"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
<input id="q" type="search" placeholder="Find a player" autocomplete="off" aria-label="Find a player"><div class="sres hid" id="sres"></div></div>
<button class="howbtn" id="howBtn">How ratings work</button>
<div class="upd" id="upd"></div></div>
<nav class="tabs" id="tabs" aria-label="Brackets"></nav></div></div>
<div class="sr" id="live" aria-live="polite"></div>
<div class="w">
<main id="board">
<section class="ln" id="ln"></section>
<div class="pod" id="pod"></div>
<div class="sh" id="ladder"><h2 id="bt">Ladder</h2><p>Seasons 8 &amp; 9 &middot; tap a name</p></div>
<p class="l">Beat someone better, gain more. The <b>&plusmn;</b> is wiggle room &mdash; it shrinks as you play.</p>
<div class="sortwrap"><div class="sorts" id="sorts"></div></div>
<p class="rule-note" id="sortNote"></p>
<div class="box"><div class="sc"><table><thead><tr>
<th style="padding-left:1rem">#</th><th>Player</th><th class="r">Rating</th><th class="r" id="thMetric">Last night</th><th class="hm">Trend</th><th class="hm">W&ndash;D&ndash;L</th>
</tr></thead><tbody id="tb"></tbody></table></div></div>
<button class="showaway" id="awayBtn"></button>
<div class="box hid" id="awayBox"><table><tbody id="tbAway"></tbody></table></div>
<section id="arcSec"><div class="sh"><h2>KAVA Social <span>History</span></h2><p id="arcMeta"></p></div>
<p class="l">Seasons 1&ndash;7. Old-system ratings, not comparable with today&rsquo;s ladder &mdash; this is the record of what happened.</p>
<div class="box"><div class="sc"><table><thead><tr>
<th style="padding-left:1rem">#</th><th>Player</th><th class="r">Old-system rating</th><th class="r hm">Games</th><th class="hm">W&ndash;D&ndash;L</th><th>Since then</th>
</tr></thead><tbody id="arc"></tbody></table></div></div></section>
<div class="sh"><h2>The <span>Crosstable</span></h2><p>Every pair who have met</p></div>
<p class="l">Read across a row. <b>+3</b> means three more wins than losses against that player. Tap a square for the head-to-head.</p>
<button class="xbtn" id="xtBtn">Show the crosstable</button>
<div id="xtWrap" class="hid">
<div class="xt" id="xt"></div>
<div class="xlist" id="xl"></div>
<div class="key">
<span><i style="background:#1B5A3A"></i>Well ahead</span>
<span><i style="background:#132520"></i>Just ahead</span>
<span><i style="background:var(--panel-2);border:1px solid var(--rule-2)"></i>All square</span>
<span><i style="background:#281B12"></i>Just behind</span>
<span><i style="background:#573510"></i>Well behind</span>
<span>&middot; = never played</span></div>
</div>
</main>
<main id="pv" class="hid">
<button class="back" id="bk">&larr; Back to the ladder</button>
<div class="phead2"><div class="pnick" id="pnick"></div><h1 id="pname"></h1><div class="psub" id="psub"></div><div class="pact" id="pact"></div></div>
<dl class="kpis" id="kpis"></dl>
<div class="facts" id="facts"></div>
<div class="gwrap" id="graphs"></div>
<div class="gwrap" id="graphs2"></div>
</main>
<footer id="foot"></footer>
</div>
<div class="modal" id="how" role="dialog" aria-modal="true" aria-labelledby="howT"><div class="mbox">
<button class="x" id="howX" aria-label="Close">&times;</button>
<h2 id="howT">How the <span>ratings</span> work</h2>
<dl class="faq">
<dt>Why did I lose points after a good night?</dt><dd>Points depend on who you played. Beating weaker players gains little; losing to one costs more. The number moves towards what your results say.</dd>
<dt>What is the &plusmn;?</dt><dd>How sure the number is. New players swing more. It shrinks as you play.</dd>
<dt>Why am I not on the ranked table?</dt><dd>You are ranked once the &plusmn; is 110 or less. That is usually about eight games.</dd>
<dt>Why did I disappear?</dt><dd>No games in 90 days moves you to &ldquo;away&rdquo;. Play a night and you are back.</dd>
<dt>Do games against other brackets count?</dt><dd>Yes. One rating pool, separate boards.</dd>
<dt>Why is my number different from the old sheet?</dt><dd>New system (Glicko-2), replayed from every game since October 2025. Seasons 1&ndash;7 are kept separately.</dd>
<dt>How is &ldquo;most improved&rdquo; worked out?</dt><dd>Change over the last 90 days, settled ratings only, at least twelve games.</dd>
</dl></div></div>
<script>
const D=${JSON.stringify(D)};
const $=s=>document.querySelector(s), E=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
var esc=E;
const RS=110, IDLE=90, UPSET=150, NAMES=D.names, DATES=D.dates, LASTI=DATES.length-1, P=D.players;
const byN={}, byI={};
P.forEach(p=>{ byN[p.n]=p; p.id=NAMES.indexOf(p.n); byI[p.id]=p; });
const fd=s=>s?new Date(s+"T12:00").toLocaleDateString("en-GB",{day:"numeric",month:"long",year:"numeric"}):"—";
const fshort=s=>s?new Date(s+"T12:00").toLocaleDateString("en-GB",{day:"numeric",month:"short"}):"";
const fdate=fd;
const daysBetween=(a,b)=>Math.round((new Date(b+"T12:00")-new Date(a+"T12:00"))/864e5);
const dtx=v=>v>0?"▲ +"+v:v<0?"▼ −"+Math.abs(v):"— 0";
const res=l=>l.s===1?"W":l.s===.5?"D":"L";
const away=p=>p.idle!=null&&p.idle>IDLE;
let NIGHT=[];

/* ---------- everything derived from the games ---------- */
function derive(){
  P.forEach(p=>{
    p.log=[]; p.opp={}; p.rec=[0,0,0]; p.wh=[0,0,0]; p.bl=[0,0,0]; p.games=0; p.att={}; p.rb={};
    let prev=p.seed; p.hist.forEach(h=>{ p.rb[h[0]]=prev; prev=h[1]; });
  });
  const rb=(p,ni)=>p.rb[ni]!=null?p.rb[ni]:p.seed;
  D.games.forEach(g=>{
    const ni=g[0], w=byI[g[1]], b=byI[g[2]], r=g[3]; if(!w||!b) return;
    const sw=r==="w"?1:r==="b"?0:.5, k=sw===1?0:sw===.5?1:2;
    w.log.push({ni,o:b.n,orat:rb(b,ni),mrat:rb(w,ni),s:sw,c:"w"});
    b.log.push({ni,o:w.n,orat:rb(w,ni),mrat:rb(b,ni),s:1-sw,c:"b"});
    w.games++; b.games++; w.att[ni]=1; b.att[ni]=1;
    w.rec[k]++; b.rec[2-k]++; w.wh[k]++; b.bl[2-k]++;
    (w.opp[b.n]=w.opp[b.n]||[0,0,0])[k]++; (b.opp[w.n]=b.opp[w.n]||[0,0,0])[2-k]++;
  });
  D.byes.forEach(a=>{ for(let i=1;i<a.length;i++){ const p=byI[a[i]]; if(p) p.att[a[0]]=1 } });
  NIGHT=DATES.map(()=>({pts:{},g:{}}));
  P.forEach(p=>p.log.forEach(l=>{ const N=NIGHT[l.ni]; N.pts[p.n]=(N.pts[p.n]||0)+l.s; N.g[p.n]=(N.g[p.n]||0)+1 }));
  NIGHT.forEach(N=>{
    N.table=Object.keys(N.pts).map(n=>[n,N.pts[n],N.g[n]]).sort((a,b)=>b[1]-a[1]||a[2]-b[2]);
    N.place={}; N.table.forEach((row,i)=>{ N.place[row[0]]=(i>0&&N.table[i-1][1]===row[1])?N.place[N.table[i-1][0]]:i+1 });
  });
  const cut=new Date(D.date+"T12:00"); cut.setDate(cut.getDate()-90); const cutS=cut.toISOString().slice(0,10);
  P.forEach(p=>{
    const lg=p.log, hl=p.hist.length;
    const nightsIn=Object.keys(p.att).map(Number).sort((a,b)=>a-b);
    p.cons=nightsIn.length;
    p.lastNi=nightsIn.length?nightsIn[nightsIn.length-1]:null;
    p.last=p.lastNi!=null?DATES[p.lastNi]:null;
    p.idle=p.last?daysBetween(p.last,D.date):null;
    p.played=!!(lg.length&&lg[lg.length-1].ni===LASTI);
    p.delta=p.played?(hl>=2?p.hist[hl-1][1]-p.hist[hl-2][1]:p.r-p.seed):null;
    p.form=lg.slice(-20).map(res).join("");
    const all=lg.map(res); let best=0,cur=0; all.forEach(x=>{ cur=x==="W"?cur+1:0; if(cur>best) best=cur });
    let tail=0; for(let i=all.length-1;i>=0&&all[i]==="W";i--) tail++;
    p.streak=[best,tail];
    const BANDS=[["Much stronger",150,9999],["Stronger",50,150],["Even",-50,50],["Weaker",-150,-50],["Much weaker",-9999,-150]];
    const ni0=lg.length?lg[0].ni:-1; lg.forEach(l=>{ l.first=l.ni===ni0 });
    p.bands=BANDS.map(b=>{ const o=[b[0],0,0,0]; lg.forEach(l=>{ if(l.first&&lg.length>4) return; const gap=l.orat-l.mrat; if(gap>=b[1]&&gap<b[2]) o[l.s===1?1:l.s===.5?2:3]++ }); return o });
    const nn={}; lg.forEach(l=>{ const e=nn[l.ni]=nn[l.ni]||[0,0,0]; e[l.s===1?0:l.s===.5?1:2]++ });
    const hmap={}; p.hist.forEach(h=>hmap[h[0]]=h[1]);
    p.nightly=Object.keys(nn).map(Number).sort((a,b)=>a-b).map(ni=>{
      const N=NIGHT[ni]; return {ni, d:DATES[ni], delta:(hmap[ni]!=null?hmap[ni]:p.r)-rb(p,ni), w:nn[ni][0], dr:nn[ni][1], l:nn[ni][2],
        pts:N.pts[p.n]||0, place:N.place[p.n]||0, of:N.table.length, first:ni===lg[0].ni};
    });
    let pk=null, lo=null; p.hist.forEach(h=>{ if(!pk||h[1]>pk[1]) pk=h; if(!lo||h[1]<lo[1]) lo=h });
    p.peak=pk?[pk[1],DATES[pk[0]]]:null; p.low=lo?[lo[1],DATES[lo[0]]]:null;
    p.avgOpp=lg.length?Math.round(lg.reduce((s,l)=>s+l.orat,0)/lg.length):null;
    p.upsets=lg.filter(l=>l.s===1&&!(l.first&&lg.length>4)&&l.orat-l.mrat>=UPSET).length;
    p.nem=null; p.vic=null;
    Object.keys(p.opp).forEach(o=>{ const a=p.opp[o], g=a[0]+a[1]+a[2]; if(g<3) return; const net=a[0]-a[2];
      if(!p.nem||net<p.nem[4]) p.nem=[o,a[0],a[1],a[2],net]; if(!p.vic||net>p.vic[4]) p.vic=[o,a[0],a[1],a[2],net]; });
    p.first=lg.length?DATES[lg[0].ni]:null;
    const prior=p.hist.filter(h=>DATES[h[0]]<=cutS);
    p.imp=(prior.length>=3&&p.rd<=RS&&p.games>=12)?p.r-prior[prior.length-1][1]:null;
    p.recent=lg.slice(-10).reverse();
    p.bigNight=0; p.nightly.forEach(n=>{ if(!n.first&&n.delta>p.bigNight) p.bigNight=n.delta });
    p.milestones=milestonesOf(p);
  });
}
function milestonesOf(p){
  const out=[], lg=p.log; if(!lg.length) return out;
  const add=(ni,label,detail)=>out.push([DATES[ni],label,detail||""]);
  add(lg[0].ni,"First game","against "+lg[0].o);
  const fw=lg.find(l=>l.s===1); if(fw) add(fw.ni,"First win","against "+fw.o);
  const fu=lg.find(l=>l.s===1&&!(l.first&&lg.length>4)&&l.orat-l.mrat>=UPSET); if(fu) add(fu.ni,"First upset","beat "+fu.o+", rated "+(fu.orat-fu.mrat)+" higher");
  let cur=0, s5=false, s10=false;
  lg.forEach(l=>{ cur=l.s===1?cur+1:0; if(cur===5&&!s5){ s5=true; add(l.ni,"Five wins in a row") } if(cur===10&&!s10){ s10=true; add(l.ni,"Ten wins in a row") } });
  [25,50,100,150].forEach(k=>{ if(lg.length>=k) add(lg[k-1].ni,k+" games played") });
  let bestWin=null; lg.forEach(l=>{ if(l.s===1&&(!bestWin||l.orat>bestWin.orat)) bestWin=l });
  if(bestWin&&p.games>=5) add(bestWin.ni,"Best win so far","beat "+bestWin.o+" when they were rated "+bestWin.orat);
  if(p.peak&&p.games>=8) out.push([p.peak[1],"Career high","rating reached "+p.peak[0]]);
  out.sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0);
  return out;
}
derive();

/* ---------- state + routing ---------- */
let div="all", sortK="r", showAway=false, CUR=null, RIVAL=null, boardHash="", boardScroll=0, xtShown=false;
const shortDiv=d=>{ if(d==="all") return "Club"; const m=/^over ([0-9]+)$/i.exec(d); if(m) return m[1]+"+"; const u=/^under ([0-9]+)$/i.exec(d); if(u) return "U"+u[1]; return d };
const longDiv=d=>d==="all"?"Whole Club":d.charAt(0).toUpperCase()+d.slice(1);
function stateHash(){ const a=[]; if(div!=="all") a.push("b",div); if(sortK!=="r") a.push("sort",sortK); return a.length?"#/"+a.map(encodeURIComponent).join("/"):"" }
function go(h){ if(location.hash===h||(h===""&&!location.hash)){ route(); return } location.hash=h }
function route(){
  const parts=location.hash.replace(/^#[/]?/,"").split("/").map(s=>{ try{return decodeURIComponent(s)}catch(e){return s} }).filter(Boolean);
  if(parts[0]==="p"&&byN[parts[1]]){ showProfile(parts[1], parts[2]==="vs"&&byN[parts[3]]?parts[3]:null); return }
  let i=0, nd="all", ns="r";
  while(i<parts.length){ if(parts[i]==="b"&&(parts[i+1]==="all"||D.divisions.indexOf(parts[i+1])>=0)){ nd=parts[i+1]; i+=2 }
    else if(parts[i]==="sort"&&SORTS.some(s=>s.k===parts[i+1])){ ns=parts[i+1]; i+=2 } else i++; }
  div=nd; sortK=ns;
  showBoard();
}
window.addEventListener("hashchange",route);

/* ---------- header ---------- */
(function(){
  const today=new Date().toISOString().slice(0,10);
  const fresh=D.built&&daysBetween(D.built,today)<=2;
  $("#upd").className="upd"+(fresh?" fresh":"");
  $("#upd").innerHTML='Updated <b class="d">'+fshort(D.built)+'</b> &middot; includes <b>'+fshort(D.date)+'</b>'+(D.next?'<br>Next night <b>'+fshort(D.next)+'</b>':'');
  $("#foot").innerHTML="KAVA Social Chess Club &middot; seasons 8 &amp; 9: "+D.games.length+" games across "+DATES.length+" club nights &middot; seasons 1&ndash;7 archived separately &middot; ratings by Glicko-2 &middot; built "+fd(D.built);
})();
$("#tabs").innerHTML=[{i:"all"}].concat(D.divisions.map(d=>({i:d}))).map(t=>{
  const n=t.i==="all"?P.length:P.filter(p=>p.d===t.i).length;
  return '<button role="tab" data-d="'+E(t.i)+'" aria-selected="false"><span class="lg">'+E(longDiv(t.i))+'</span><span class="sm">'+E(shortDiv(t.i))+'</span><span class="n">'+n+'</span></button>'}).join("");
$("#tabs").onclick=e=>{ const b=e.target.closest("[data-d]"); if(!b) return; div=b.dataset.d; go(stateHash()); $("#live").textContent=longDiv(div)+" ladder"; };
$("#howBtn").onclick=()=>{ $("#how").classList.add("open"); $("#howX").focus() };
$("#howX").onclick=()=>$("#how").classList.remove("open");
$("#how").onclick=e=>{ if(e.target===$("#how")) $("#how").classList.remove("open") };
document.addEventListener("keydown",e=>{ if(e.key==="Escape"){ $("#how").classList.remove("open"); hideSearch() } });

/* ---------- search ---------- */
const ARC=D.archive, ARCBY=Object.fromEntries((ARC?ARC.players:[]).map(p=>[p.n,p]));
const stillPlaying=Object.fromEntries(Object.entries(ARC?ARC.link:{}).map(([c,a])=>[a,c]));
let sIdx=0;
function searchHits(q){
  q=q.trim().toLowerCase(); if(!q) return [];
  const hit=[];
  P.forEach(p=>{ const i=p.n.toLowerCase().indexOf(q); if(i>=0) hit.push({p, w:i===0?0:1}) });
  hit.sort((a,b)=>a.w-b.w||b.p.r-a.p.r);
  const out=hit.slice(0,6).map(h=>({n:h.p.n, sub:(h.p.d||"")+" · "+h.p.r+(away(h.p)?" · away":h.p.rd>RS?" · settling":"")}));
  if(out.length<6&&ARC) ARC.players.forEach(a=>{ if(out.length>=6||stillPlaying[a.n]) return; if(a.n.toLowerCase().indexOf(q)>=0) out.push({n:a.n, sub:"seasons 1–7 only", arc:true}) });
  return out;
}
function drawSearch(){
  const q=$("#q").value, hits=searchHits(q), box=$("#sres");
  if(!q.trim()){ hideSearch(); return }
  box.classList.remove("hid");
  box.innerHTML=hits.length?hits.map((h,i)=>'<button data-n="'+E(h.n)+'"'+(h.arc?' data-arc="1"':'')+' class="'+(i===sIdx?"on":"")+'"><b>'+E(h.n)+'</b><span>'+E(h.sub)+'</span></button>').join(""):'<div class="no">No one by that name.</div>';
}
function hideSearch(){ $("#sres").classList.add("hid"); sIdx=0 }
function pickSearch(b){ if(!b) return; $("#q").value=""; hideSearch(); $("#q").blur();
  if(b.dataset.arc){ go(""); setTimeout(()=>{ const tr=$("#arc").querySelector('tr[data-arc="'+CSS.escape(b.dataset.n)+'"]'); if(tr){ tr.scrollIntoView({block:"center"}); tr.focus() } },60) } else openProfile(b.dataset.n) }
$("#q").oninput=()=>{ sIdx=0; drawSearch() };
$("#q").onfocus=drawSearch;
$("#q").onkeydown=e=>{ const bs=[...$("#sres").querySelectorAll("button")];
  if(e.key==="ArrowDown"){ sIdx=Math.min(bs.length-1,sIdx+1); drawSearch(); e.preventDefault() }
  else if(e.key==="ArrowUp"){ sIdx=Math.max(0,sIdx-1); drawSearch(); e.preventDefault() }
  else if(e.key==="Enter"){ pickSearch(bs[sIdx]||bs[0]); e.preventDefault() } };
$("#sres").onmousedown=e=>{ const b=e.target.closest("button[data-n]"); if(b){ e.preventDefault(); pickSearch(b) } };
document.addEventListener("click",e=>{ if(!e.target.closest(".srch")) hideSearch() });

/* ---------- board ---------- */
const pct=(w,d,g)=>g?Math.round((w+d/2)/g*100):0;
const pool=()=>P.filter(p=>div==="all"||p.d===div);
const rank=()=>pool().filter(p=>!away(p)&&p.rd<=RS);
const prov=()=>pool().filter(p=>!away(p)&&p.rd>RS);
const gone=()=>pool().filter(away);
const SORTS=[
 {k:"r",   t:"Rating",         col:"Last night", val:p=>p.r, show:null, note:"Ranked once the ± is 110 or less. Away after 90 days without a game."},
 {k:"win", t:"Win rate",       col:"Win rate",   val:p=>pct(p.rec[0],p.rec[1],p.games), show:p=>pct(p.rec[0],p.rec[1],p.games)+"%", min:8, note:"Draws count half. Fewer than 8 games drops to the bottom."},
 {k:"g",   t:"Games played",   col:"Games",      val:p=>p.games, show:p=>p.games, note:"Every game in seasons 8 and 9."},
 {k:"imp", t:"Most improved",  col:"3 months",   val:p=>p.imp==null?-9999:p.imp,
   show:p=>p.imp==null?'<span style="font-size:.7rem;color:var(--ink-3)">settling</span>':(p.imp>0?"+"+p.imp:p.imp), sign:true, note:"Change over the last 90 days. Settled ratings only, at least 12 games."},
 {k:"con", t:"Most consistent",col:"Nights",     val:p=>p.cons||0, show:p=>(p.cons||0)+" of "+DATES.length, note:"Club nights turned up to."},
 {k:"blk", t:"Best as Black",  col:"As Black",   val:p=>{const g=p.bl[0]+p.bl[1]+p.bl[2];return g?pct(p.bl[0],p.bl[1],g):-1},
   show:p=>{const g=p.bl[0]+p.bl[1]+p.bl[2];return g?pct(p.bl[0],p.bl[1],g)+"%":"—"}, min:6, note:"Score with the Black pieces. Fewer than 6 games as Black drops to the bottom."}
];
const SORT=()=>SORTS.find(s=>s.k===sortK);
function orderOf(list){
  const s=SORT(); if(s.k==="r") return list;
  const enough=p=>!s.min||p.games>=s.min;
  return [...list].sort((a,b)=>{ const ea=enough(a), eb=enough(b); if(ea!==eb) return ea?-1:1; return s.val(b)-s.val(a)||b.r-a.r });
}
function spark(p){
  const d=(p.nightly.length>1?p.nightly.filter(n=>!n.first):p.nightly).slice(-12); if(!d.length) return "";
  const mx=Math.max(20,...d.map(n=>Math.abs(n.delta))); const W=60,H=18,bw=W/12;
  return '<svg class="spk" viewBox="0 0 '+W+' '+H+'" aria-hidden="true"><line x1="0" y1="9" x2="'+W+'" y2="9" stroke="#343A40"/>'+
    d.map((n,i)=>{ const h=Math.max(1.5,Math.abs(n.delta)/mx*8), x=(12-d.length+i)*bw+1, y=n.delta>=0?9-h:9;
      return '<rect x="'+x+'" y="'+y+'" width="'+(bw-2)+'" height="'+h+'" fill="'+(n.delta>0?"#3BC79A":n.delta<0?"#F0883E":"#4A5058")+'"/>' }).join("")+'</svg>';
}
function metricCell(p){
  const s=SORT();
  if(!s.show) return p.played&&p.delta!=null?'<span class="dl '+(p.delta>0?"u":p.delta<0?"d":"f")+'">'+dtx(p.delta)+'</span>':'<span class="dl f">—</span>';
  const cls=s.sign?(p.imp>0?"u":p.imp<0?"d":"f"):"";
  return '<span class="dl '+cls+'">'+s.show(p)+'</span>';
}
function row(p,i,kind){
  return '<tr data-n="'+E(p.n)+'" tabindex="0" role="button" class="'+(kind==="r"&&i<3?"one":kind==="p"?"pv":"")+'">'+
   '<td class="k">'+(kind==="r"?i+1:"·")+'</td>'+
   '<td class="nmc2"><span class="nmc">'+E(p.n)+'</span><span class="chev">›</span></td>'+
   '<td class="r"><span class="rat">'+p.r+'</span><span class="rdv">±'+p.rd+'</span></td>'+
   '<td class="r">'+metricCell(p)+'</td>'+
   '<td class="hm">'+spark(p)+'</td>'+
   '<td class="wdl hm">'+p.rec[0]+'<i>–</i>'+p.rec[1]+'<i>–</i>'+p.rec[2]+'</td></tr>';
}
function draw(){
  const rk=orderOf(rank()), pv=orderOf(prov()), gn=orderOf(gone());
  [...$("#tabs").children].forEach(x=>x.setAttribute("aria-selected",x.dataset.d===div));
  $("#sorts").innerHTML=SORTS.map(s=>'<button data-s="'+s.k+'" aria-pressed="'+(s.k===sortK)+'">'+s.t+'</button>').join("");
  const on=$("#sorts").querySelector('[aria-pressed="true"]'); if(on&&on.scrollIntoView) try{ on.scrollIntoView({block:"nearest",inline:"nearest"}) }catch(e){}
  $("#thMetric").textContent=SORT().col; $("#sortNote").textContent=SORT().note||"";
  $("#awayBtn").innerHTML=gn.length?(showAway?"Hide the "+gn.length+" away":"Show "+gn.length+" away — no games in "+IDLE+"+ days"):"";
  $("#awayBtn").style.display=gn.length?"":"none";
  $("#awayBox").classList.toggle("hid",!(gn.length&&showAway));
  $("#bt").innerHTML=(div==="all"?"Club":E(longDiv(div)))+' <span style="color:var(--scarlet)">Ladder</span>';
  $("#tb").innerHTML=rk.map((p,i)=>row(p,i,"r")).join("")
   +(pv.length?'<tr><td colspan="6" class="gh">🌱 Still settling in<small>ranked once the ± is '+RS+' or less</small></td></tr>'+pv.map(p=>row(p,0,"p")).join(""):"");
  $("#tbAway").innerHTML=gn.length?'<tr><td colspan="6" class="gh">💤 Away<small>no games in '+IDLE+'+ days — one night brings them back</small></td></tr>'+gn.map(p=>row(p,0,"g")).join(""):"";
  $("#pod").innerHTML=rank().slice(0,3).map((p,i)=>'<button class="pc '+(i===0?"one":"")+'" data-n="'+E(p.n)+'">'+
   '<span class="rk">'+(i+1)+'</span><div class="nm">'+E(p.n)+'</div>'+
   '<div class="rt">'+p.r+'<sub>±'+p.rd+'</sub></div></button>').join("");
  drawLastNight();
  if(xtShown) cross();
}
function showBoard(){
  if(CUR){ CUR=null; RIVAL=null; document.title="KAVA Ladder"; }
  $("#pv").classList.add("hid"); $("#board").classList.remove("hid");
  draw();
  if(boardScroll){ scrollTo({top:boardScroll,behavior:"instant"}); boardScroll=0 }
}

/* ---------- last night ---------- */
function drawLastNight(){
  const ni=LASTI, N=NIGHT[ni]; if(ni<0||!N||!N.table.length){ $("#ln").innerHTML=""; return }
  const played=P.filter(p=>p.played), games=D.games.filter(g=>g[0]===ni);
  let riser=null; played.forEach(p=>{ if(p.delta>0&&(!riser||p.delta>riser.delta)) riser=p });
  let up=null; played.forEach(p=>p.log.forEach(l=>{ if(l.ni===ni&&l.s===1&&l.orat-l.mrat>=100&&(!up||l.orat-l.mrat>up.gap)) up={p, o:l.o, gap:l.orat-l.mrat} }));
  const sweeps=played.filter(p=>{ const n=p.nightly[p.nightly.length-1]; return n&&n.ni===ni&&n.w>=3&&n.l===0&&n.dr===0 });
  const top=N.table.filter(r=>r[2]>=3); const win=top.length?top.filter(r=>r[1]===top[0][1]):[];
  const tiles=[];
  if(win.length) tiles.push('<div data-n="'+E(win[0][0])+'"><dt>'+(win.length>1?"Shared the night":"Won the night")+'</dt><dd>'+E(win.map(r=>r[0]).join(" & "))+'<small>'+win[0][1]+' of '+win[0][2]+' points</small></dd></div>');
  if(riser) tiles.push('<div data-n="'+E(riser.n)+'"><dt>Biggest climb</dt><dd>'+E(riser.n)+'<small><span class="u">+'+riser.delta+'</span> rating points</small></dd></div>');
  if(up) tiles.push('<div data-n="'+E(up.p.n)+'"><dt>Upset of the night</dt><dd>'+E(up.p.n)+'<small>beat '+E(up.o)+', rated '+up.gap+' higher</small></dd></div>');
  if(sweeps.length&&!(win.length===1&&sweeps.length===1&&sweeps[0].n===win[0][0])) tiles.push('<div data-n="'+E(sweeps[0].n)+'"><dt>Clean sweep</dt><dd>'+E(sweeps.map(p=>p.n).join(", "))+'<small>every game won</small></dd></div>');
  tiles.push('<div><dt>Turnout</dt><dd>'+N.table.length+' players<small>'+games.length+' games played</small></dd></div>');
  const results=games.map(g=>{ const w=NAMES[g[1]], b=NAMES[g[2]], r=g[3];
    return '<tr><td class="'+(r==="w"?"win":"")+'">'+E(w)+'</td><td class="res">'+(r==="w"?"1–0":r==="b"?"0–1":"½–½")+'</td><td class="'+(r==="b"?"win":"")+'">'+E(b)+'</td></tr>' }).join("");
  const standings=N.table.map(r=>'<tr data-n="'+E(r[0])+'"><td class="n">'+N.place[r[0]]+'</td><td>'+E(r[0])+'</td><td class="n">'+r[1]+' / '+r[2]+'</td></tr>').join("");
  $("#ln").innerHTML='<div class="lh"><b>Last <span>night</span></b><small>'+fd(DATES[ni])+'</small><button class="howbtn" id="lnBtn" aria-expanded="false">Full results</button></div>'+
    '<dl class="lg">'+tiles.join("")+'</dl>'+
    '<div class="recap"><div><h4>Standings on the night</h4><table>'+standings+'</table></div><div><h4>Results &middot; White first</h4><table>'+results+'</table></div></div>';
  $("#lnBtn").onclick=function(){ const o=$("#ln").classList.toggle("open"); this.setAttribute("aria-expanded",o); this.textContent=o?"Hide results":"Full results" };
  $("#ln").onclick=e=>{ if(e.target.closest("#lnBtn")) return; const t=e.target.closest("[data-n]"); if(t&&byN[t.dataset.n]) openProfile(t.dataset.n) };
}

/* ---------- crosstable ---------- */
let XL_PICK=null;
function crossList(){ return orderOf(rank()).concat(orderOf(prov())).slice(0,div==="all"?18:24) }
function cellCls(a){ const net=a[0]-a[2], mag=Math.min(4,Math.abs(net)); return net>0?"w"+mag:net<0?"l"+mag:"lev" }
function cross(){
  const list=crossList();
  if(list.length<2){ $("#xt").innerHTML='<p style="padding:1rem;color:var(--ink-3)">Not enough players yet.</p>'; $("#xl").innerHTML=""; return }
  const head=list.map((p,i)=>'<th><div class="vt"><b>'+(i+1)+'</b>'+E(p.n)+'</div></th>').join("");
  const rows=list.map((p,i)=>{
    const cells=list.map(o=>{
      if(o.n===p.n) return '<td class="self"></td>';
      const a=p.opp[o.n];
      if(!a) return '<td class="none" data-o="'+E(o.n)+'" title="'+E(p.n)+' and '+E(o.n)+' have never played">·</td>';
      const net=a[0]-a[2], txt=net>0?"+"+net:net<0?String(net):"=";
      return '<td class="'+cellCls(a)+'" data-o="'+E(o.n)+'" title="'+E(p.n)+' v '+E(o.n)+' — '+a[0]+' won, '+a[1]+' drawn, '+a[2]+' lost">'+txt+'</td>';
    }).join("");
    return '<tr data-n="'+E(p.n)+'"><th><span class="rn">'+(i+1)+'</span><span class="nm2">'+E(p.n)+'</span><span class="r2">'+p.r+'</span></th>'+cells+'</tr>';
  }).join("");
  $("#xt").innerHTML='<table><thead><tr><th class="c">Row v column<br>ahead / behind</th>'+head+'</tr></thead><tbody>'+rows+'</tbody></table>';
  const tbl=$("#xt").querySelector("table");
  tbl.onclick=e=>{ const td=e.target.closest("td[data-o]"), tr=e.target.closest("tr[data-n]"); if(!tr) return;
    if(td) openProfile(tr.dataset.n, td.dataset.o); else openProfile(tr.dataset.n) };
  tbl.onmouseover=e=>{ const td=e.target.closest("td"); if(!td) return; tbl.dataset.c=td.cellIndex };
  tbl.onmouseleave=()=>{ delete tbl.dataset.c };
  const sel='<div class="xsel"><select id="xtPick" aria-label="Pick a player"><option value="">Pick a player…</option>'+list.map(p=>'<option value="'+E(p.n)+'"'+(XL_PICK===p.n?" selected":"")+'>'+E(p.n)+' — '+p.r+'</option>').join("")+'</select></div>';
  const me=XL_PICK&&byN[XL_PICK];
  $("#xl").innerHTML=sel+(me?list.filter(o=>o.n!==me.n).map(o=>{ const a=me.opp[o.n];
     if(!a) return '<div class="xrow" data-o="'+E(o.n)+'"><b>'+E(o.n)+'</b><span class="net" style="color:#3A4046">·</span><span class="rc">never played</span></div>';
     const net=a[0]-a[2]; return '<div class="xrow" data-o="'+E(o.n)+'"><b>'+E(o.n)+'</b><span class="net '+cellCls(a)+'">'+(net>0?"+"+net:net<0?net:"=")+'</span><span class="rc">'+a[0]+'–'+a[1]+'–'+a[2]+'</span></div>' }).join("")
    :'<p style="color:var(--ink-3);font-size:.88rem;margin:0">Pick a name to see their record against everyone.</p>');
  $("#xtPick").onchange=function(){ XL_PICK=this.value||null; cross() };
  $("#xl").onclick=e=>{ const r=e.target.closest(".xrow"); if(r&&me) openProfile(me.n, r.dataset.o) };
}
(function(){ /* column crosshair: one attribute on the table, CSS does the rest */
  let css=""; for(let c=1;c<=40;c++){ css+='.xt table[data-c="'+c+'"] td:nth-child('+(c+1)+'){outline:2px solid var(--scarlet);outline-offset:-2px}.xt table[data-c="'+c+'"] thead th:nth-child('+(c+1)+') .vt{color:var(--scarlet)}' }
  const st=document.createElement("style"); st.textContent=css; document.head.appendChild(st);
})();
$("#xtBtn").onclick=function(){ xtShown=!xtShown; $("#xtWrap").classList.toggle("hid",!xtShown); this.textContent=xtShown?"Hide the crosstable":"Show the crosstable"; if(xtShown) cross() };

/* ---------- archive ---------- */
function drawArchive(){
  if(!ARC||!ARC.players||!ARC.players.length){ $("#arcSec").classList.add("hid"); return }
  $("#arcMeta").textContent="Seasons 1–7 · "+ARC.nights+" nights · "+ARC.games+" games";
  $("#arc").innerHTML=ARC.players.map((p,i)=>{
    const now=stillPlaying[p.n];
    return '<tr data-arc="'+E(p.n)+'"'+(now?' data-n="'+E(now)+'" tabindex="0" role="button"':' tabindex="-1"')+' class="'+(i<3?"one":"")+'">'+
     '<td class="k">'+(i+1)+'</td>'+
     '<td class="nmc2"><span class="nmc">'+E(p.n)+'</span></td>'+
     '<td class="r"><span class="rat">'+p.r+'</span></td>'+
     '<td class="r wdl hm">'+p.g+'</td>'+
     '<td class="wdl hm">'+p.rec[0]+'<i>–</i>'+p.rec[1]+'<i>–</i>'+p.rec[2]+'</td>'+
     '<td style="white-space:nowrap">'+(now?'<span style="font-family:var(--fm);font-size:.62rem;color:var(--gain)"><span class="hm">still playing — </span>'+E(now)+'</span>'
             :p.st==="dormant"?'<span style="font-family:var(--fm);font-size:.62rem;color:var(--loss)">away</span>'
                :'<span style="font-family:var(--fm);font-size:.62rem;color:var(--ink-3)">—</span>')+'</td></tr>'}).join("");
}
function legacyFor(p){
  const key=ARC&&ARC.link?ARC.link[p.n]:null, a=key?ARCBY[key]:null;
  if(!a) return "";
  const tot=[p.rec[0]+a.rec[0], p.rec[1]+a.rec[1], p.rec[2]+a.rec[2]], g=p.games+a.g;
  const td=(t,extra)=>'<td style="padding:.35rem .2rem;'+(extra||"")+'">'+t+'</td>';
  return '<p style="margin:0 0 .8rem;color:var(--ink-2);font-size:.86rem">Played as <b>'+E(a.n)+'</b> in seasons 1&ndash;7.</p>'+
   '<table style="font-size:.86rem"><tbody>'+
   '<tr>'+td("Seasons 1&ndash;7","color:var(--ink-3)")+td(a.g+" games","text-align:right;font-family:var(--fm)")+td(a.rec.join("–"),"text-align:right;font-family:var(--fm);font-weight:700")+'</tr>'+
   '<tr>'+td("Seasons 8 &amp; 9","color:var(--ink-3)")+td(p.games+" games","text-align:right;font-family:var(--fm)")+td(p.rec.join("–"),"text-align:right;font-family:var(--fm);font-weight:700")+'</tr>'+
   '<tr>'+td("All time","font-weight:700;padding:.5rem .2rem")+td(g+" games","text-align:right;font-family:var(--fm);font-weight:700")+td(tot.join("–"),"text-align:right;font-family:var(--fm);font-weight:700;color:var(--gain)")+'</tr>'+
   '</tbody></table><p class="cap">Old-system rating back then: '+a.r+'. Not comparable with today&rsquo;s number.</p>';
}

/* ---------- titles ----------
   Forty traits read off the player's own record, five names each. Highest weight
   wins; the variant is a hash of the name so a title is stable for life.
   Nothing here is unkind. No gendered wording anywhere.                     */
function sc(p){return p.rec[0]+p.rec[1]/2}
function wr(p){return p.games?Math.round(sc(p)/p.games*100):0}
function cpct(a){var g=a[0]+a[1]+a[2];return g?Math.round((a[0]+a[1]/2)/g*100):0}
function hashName(s){var h=2166136261>>>0;for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0}return h>>>0}
function T(w,ic,test,names,why){return {w:w,ic:ic,test:test,names:names,why:why}}
var TITLES=[
 T(100,"👑",function(p,c){return c.rank1&&c.win>=85&&p.games>=10},["The Untouchable","Final Boss","Flawless","The Ceiling","Apex Predator"],function(p,c){return "Top of the ladder, scoring "+c.win+"% across "+p.games+" games."}),
 T(96,"👑",function(p,c){return c.rank1},["Top of the Mountain","The Benchmark","King of the Hill","The One to Beat","Head of the Table"],function(p,c){return "Number one on the ladder at "+p.r+"."}),
 T(94,"🗡️",function(p,c){return c.beatTop},["Regicide","Toppled the Top","Slayer of Giants","Took the Crown","Big Game Hunter"],function(p,c){return "Has beaten "+c.topName+", the top of the ladder."}),
 T(90,"⚡",function(p){return p.upsets>=5},["Giant Killer","Bracket Buster","The Upset Machine","Dragon Slayer","Seed Wrecker"],function(p,c){return p.upsets+" wins over opponents rated 150 or more above them."}),
 T(86,"💣",function(p){return p.upsets>=3},["Trouble","The Spoiler","Dark Horse","Ambush Specialist","The Banana Skin"],function(p,c){return p.upsets+" wins over opponents rated 150 or more above them."}),
 T(84,"🔥",function(p){return p.streak[0]>=10},["The Streak","Avalanche","Ten Straight","Unstoppable Once Started","Chain Reaction"],function(p,c){return "Longest winning run at the club: "+p.streak[0]+" straight."}),
 T(80,"🔥",function(p){return p.streak[0]>=6},["Hot Hand","On a Tear","Runs Deep","The Surge","Snowball"],function(p,c){return "Put together "+p.streak[0]+" wins in a row."}),
 T(78,"🚀",function(p,c){return c.mostImproved},["Story of the Season","Biggest Riser","The Jump","Most Improved","Season's Climber"],function(p,c){return "The biggest three-month rise in the club, up "+p.imp+"."}),
 T(76,"📈",function(p){return p.imp!=null&&p.imp>=100},["The Climber","Rocket","Rising Fast","Up and Up","The Ascent"],function(p,c){return "Up "+p.imp+" points over the last three months."}),
 T(74,"🥇",function(p,c){return c.atPeak&&p.games>=15},["Career Best","Peak Form","Highest Ever","Top of Their Game","New Heights"],function(p,c){return "Sitting at their highest rating ever, "+p.r+"."}),
 T(72,"♚",function(p,c){return c.bpc>=c.wpc+15&&c.blk>=8},["Nightfall","Second Mover","The Dark Side","Better in Black","Shadow Play"],function(p,c){return c.bpc+"% with Black against "+c.wpc+"% with White, over "+c.blk+" games as Black."}),
 T(72,"♔",function(p,c){return c.wpc>=c.bpc+15&&c.wht>=8},["First Strike","Opening Bell","The Initiative","Better in White","Sets the Pace"],function(p,c){return c.wpc+"% with White against "+c.bpc+"% with Black, over "+c.wht+" games as White."}),
 T(70,"🎯",function(p,c){return c.dominates},["Has Their Number","The Bogey","Nightmare Matchup","Owns the Fixture","Personal Curse"],function(p,c){return "Holds "+p.vic[1]+"-"+p.vic[2]+"-"+p.vic[3]+" over "+p.vic[0]+"."}),
 T(68,"🪑",function(p,c){return c.att>=0.9&&p.games>=15},["Ever-Present","The Fixture","Never Misses","The Constant","Part of the Furniture"],function(p,c){return "At the board on "+p.cons+" of "+DATES.length+" club nights."}),
 T(66,"⛏️",function(p){return p.games>=80},["The Grinder","Iron Board","Volume Dealer","Never Says No","High Mileage"],function(p,c){return p.games+" games played, more than almost anyone."}),
 T(64,"🧊",function(p,c){return p.rd<=55&&p.games>=40},["The Metronome","Known Quantity","Rock Solid","The Baseline","Steady State"],function(p,c){return "Rating settled to within "+p.rd+" after "+p.games+" games."}),
 T(62,"🥊",function(p){return p.games>=15&&p.avgOpp&&p.avgOpp>=p.r+80},["Punching Up","Swims Upstream","Takes All Comers","No Easy Nights","Books the Hard Ones"],function(p,c){return "Average opponent rated "+p.avgOpp+", about "+(p.avgOpp-p.r)+" above them."}),
 T(60,"🎲",function(p,c){return c.wildcard},["The Wildcard","Coin Flip","Chaos Agent","Never the Same Twice","Hard to Predict"],function(p,c){return "Beats players above them and drops games below — never the same twice."}),
 T(58,"🤝",function(p,c){return c.drawRate>=0.12&&p.games>=15},["The Diplomat","Peace Broker","Splits the Point","Hard to Beat","The Handshake"],function(p,c){return p.rec[1]+" draws in "+p.games+" games."}),
 T(57,"⚔️",function(p,c){return p.rec[1]===0&&p.games>=20},["No Quarter","All or Nothing","Decisive","No Middle Ground","Wins or Loses"],function(p,c){return "Not a single draw in "+p.games+" games."}),
 T(56,"✅",function(p,c){return c.noSlips&&p.games>=20},["No Slip-Ups","Clinical","Does the Job","Takes Care of Business","Nothing Dropped"],function(p,c){return "Unbeaten against players well below them."}),
 T(54,"🌟",function(p,c){return c.last5win},["Five From Five","Untouched Lately","Clean Sweep Mode","Perfect Fortnight","Nothing Given Away"],function(p,c){return "Won the last five games on record."}),
 T(52,"📊",function(p,c){return Math.abs(c.wpc-c.bpc)<=3&&p.games>=20},["Ambidextrous","Either Side","No Preference","Same Either Way","Colour Agnostic"],function(p,c){return c.wpc+"% with White, "+c.bpc+"% with Black - no preference at all."}),
 T(50,"🌍",function(p,c){return c.opps>=20},["Plays Anyone","Knows Everyone","Full Circuit","No Ducking","The Socialite"],function(p,c){return "Has faced "+c.opps+" different opponents."}),
 T(48,"🏃",function(p,c){return p.streak[1]>=4},["Red Hot","Rolling","In Form","Riding the Wave","Can't Miss"],function(p,c){return "On "+p.streak[1]+" straight wins right now."}),
 T(46,"💥",function(p,c){return p.bigNight>=60},["Big Night Merchant","The Spike","Peaks Hard","One Great Evening","Boom and Bust"],function(p,c){return "Once gained "+p.bigNight+" rating points in a single night."}),
 T(44,"🛡️",function(p,c){return p.games>=15&&p.avgOpp&&p.avgOpp<=p.r-80},["Front Runner","Protects the Lead","Handles the Field","Business as Usual","Holds Station"],function(p,c){return "Average opponent rated "+p.avgOpp+", around "+(p.r-p.avgOpp)+" below them."}),
 T(42,"🔁",function(p,c){return c.returner},["The Returner","Back in the Room","Long Time No See","Comeback Trail","Rejoined the Fray"],function(p,c){return "Back at the board after a spell away."}),
 T(40,"👻",function(p,c){return away(p)},["Missing in Action","On Sabbatical","Whereabouts Unknown","The Ghost","Seat Still Warm"],function(p,c){return "No games in "+p.idle+" days."}),
 T(38,"🧩",function(p){return p.rd>=110&&p.games>=15},["The Enigma","Hard to Read","Still a Mystery","Unresolved","Work in Progress"],function(p,c){return "Still swinging by "+p.rd+" after "+p.games+" games - hard to pin down."}),
 T(36,"🧱",function(p,c){return c.hasNemesis},["Unfinished Business","Owes Someone","One Name Haunts Them","The Rematch Wanted","A Score to Settle"],function(p,c){return p.nem[0]+" leads it "+p.nem[3]+"-"+p.nem[1]+"."}),
 T(34,"🔨",function(p){return p.games>=50},["The Workhorse","Plenty of Reps","In the Chair","Puts the Hours In","Always Playing"],function(p,c){return p.games+" games and counting."}),
 T(65,"🌱",function(p){return p.games<8},["The Newcomer","Fresh Blood","Just Arrived","Ink Still Wet","Unwritten"],function(p,c){return "Only "+p.games+" games on the board so far."}),
 T(30,"🏗️",function(p,c){return p.imp!=null&&p.imp>=40},["Trending Up","Finding Form","Sharpening","On the Rise","Building Something"],function(p,c){return "Up "+p.imp+" points over the last three months."}),
 T(28,"🌊",function(p,c){return p.imp!=null&&p.imp<=-80},["Due a Bounce","Between Gears","Rebuilding","Storm to Ride Out","Better Days Coming"],function(p,c){return "Down "+Math.abs(p.imp)+" over three months - it comes back."}),
 T(26,"🕳️",function(p,c){return c.slips>=3},["Off-Days Specialist","Trap Door","The Occasional Wobble","Loses the Winnable","Keeps It Interesting"],function(p,c){return "Has dropped "+c.slips+" games to players well below them."}),
 T(24,"👥",function(p,c){return c.opps<=5&&p.games>=15},["Small Circle","Same Faces","Closed Shop","Familiar Foes","The Usual Suspects"],function(p,c){return "Plays the same "+c.opps+" opponents over and over."}),
 T(22,"🌧️",function(p,c){return c.last5loss},["Rough Patch","Heads Down","Grinding Through","Turning a Corner","Fortunes Will Turn"],function(p,c){return "Last five games did not go their way."}),
 T(20,"⏳",function(p,c){return p.games>=15&&p.peak&&p.r<p.peak[0]-120},["Chasing the Peak","Was Higher Once","Road Back","Remembers Better Days","The Long Climb"],function(p,c){return "Career high was "+p.peak[0]+", currently "+p.r+"."}),
 T(10,"♟️",function(){return true},["The Regular","Club Stalwart","Board Warrior","One of the Crew","Always Game"],function(p,c){return p.games+" games across "+p.cons+" nights."})
];
function titleCtx(p){
  var board=P.filter(function(x){return !away(x)&&x.rd<=RS}), top=board[0], rank1=!!(top&&top.n===p.n);
  var wht=p.wh[0]+p.wh[1]+p.wh[2], blk=p.bl[0]+p.bl[1]+p.bl[2];
  var mostImp=null; P.forEach(function(x){ if(x.imp!=null&&(mostImp===null||x.imp>mostImp.imp)) mostImp=x; });
  var strong=p.bands[0], weak=p.bands[4], f=p.form||"", last5=f.slice(-5);
  var gapBefore=0; if(p.nightly.length>=2){ var a=p.nightly[p.nightly.length-2].ni, b=p.nightly[p.nightly.length-1].ni; gapBefore=b-a-1 }
  return {rank1:rank1, topName:top?top.n:"", beatTop:!!(top&&top.n!==p.n&&p.opp[top.n]&&p.opp[top.n][0]>0),
    win:wr(p), wpc:cpct(p.wh), bpc:cpct(p.bl), wht:wht, blk:blk, att:DATES.length?p.cons/DATES.length:0,
    drawRate:p.games?p.rec[1]/p.games:0, opps:Object.keys(p.opp).length, atPeak:!!(p.peak&&Math.abs(p.r-p.peak[0])<=2),
    mostImproved:!!(mostImp&&mostImp.n===p.n&&mostImp.imp>=40), dominates:!!(p.vic&&p.vic[1]-p.vic[3]>=5),
    hasNemesis:!!(p.nem&&p.nem[3]-p.nem[1]>=3), wildcard:strong[1]>=2&&weak[3]>=3, noSlips:weak[3]===0&&weak[1]>=8, slips:weak[3],
    returner:p.played&&gapBefore>=3,
    last5win:last5.length===5&&last5.indexOf("L")<0&&last5.indexOf("D")<0, last5loss:last5.length===5&&last5.indexOf("W")<0};
}
function titleFor(p){
  var c=titleCtx(p), best=null;
  for(var i=0;i<TITLES.length;i++){ var t=TITLES[i]; try{ if(t.test(p,c)&&(!best||t.w>best.w)) best=t }catch(e){} }
  if(!best) best=TITLES[TITLES.length-1];
  var idx=hashName(p.n)%best.names.length, why=""; try{ why=best.why(p,c) }catch(e){ why="" }
  return {name:best.names[idx], ic:best.ic, why:why};
}

/* ---------- fun facts: five, most unusual first ---------- */
function pctile(arr,v){ var n=arr.length; if(!n) return .5; var below=0, eq=0; arr.forEach(function(x){ if(x<v) below++; else if(x===v) eq++ }); return (below+eq/2)/n }
function facts(p){
  var pool=P.filter(function(x){return x.games>=5}), wpc=cpct(p.wh), bpc=cpct(p.bl);
  var surprise=function(f,v){ return Math.abs(pctile(pool.map(f),v)-.5) };
  var bestNight=null; p.nightly.forEach(function(n){ if(!n.first&&(!bestNight||n.delta>bestNight.delta)) bestNight=n });
  var c=[];
  if(p.peak&&p.games>=8) c.push([surprise(function(x){return x.peak?x.peak[0]:0},p.peak[0]),"🏔️",p.peak[0],"Career-high rating, reached "+fd(p.peak[1])+"."]);
  if(p.streak[0]>=3) c.push([surprise(function(x){return x.streak[0]},p.streak[0])+.05,"🔥",p.streak[0]+" in a row","Their longest winning run to date."]);
  if(p.upsets>=1) c.push([surprise(function(x){return x.upsets},p.upsets)+.1,"⚡",p.upsets+(p.upsets===1?" upset":" upsets"),"Wins over players rated 150 or more above them."]);
  if(p.vic&&p.vic[1]-p.vic[3]>=2) c.push([surprise(function(x){return x.vic?x.vic[1]-x.vic[3]:0},p.vic[1]-p.vic[3]),"🎯",p.vic[1]+"–"+p.vic[2]+"–"+p.vic[3],"Their best record against anyone — "+esc(p.vic[0])+"."]);
  if(p.nem&&p.nem[3]-p.nem[1]>=2) c.push([surprise(function(x){return x.nem?x.nem[3]-x.nem[1]:0},p.nem[3]-p.nem[1]),"🧱",p.nem[1]+"–"+p.nem[2]+"–"+p.nem[3],esc(p.nem[0])+" has their number."]);
  if(bestNight&&bestNight.delta>=15) c.push([surprise(function(x){return x.bigNight},bestNight.delta),"🚀","+"+bestNight.delta,"Biggest single night, on "+fd(bestNight.d)+"."]);
  if(p.cons>=2) c.push([surprise(function(x){return x.cons},p.cons),"🪑",p.cons+" of "+DATES.length,"Club nights turned up to."]);
  if(Math.abs(wpc-bpc)>=10&&p.games>=10) c.push([surprise(function(x){return Math.abs(cpct(x.wh)-cpct(x.bl))},Math.abs(wpc-bpc)),"♟️",(bpc>wpc?bpc:wpc)+"%","Better with "+(bpc>wpc?"Black":"White")+" — "+wpc+"% as White, "+bpc+"% as Black."]);
  if(p.avgOpp) c.push([surprise(function(x){return x.avgOpp||0},p.avgOpp)-.05,"📏",p.avgOpp,"Average rating of everyone they have faced."]);
  var oppsN=Object.keys(p.opp).length; if(oppsN>=2) c.push([surprise(function(x){return Object.keys(x.opp).length},oppsN)-.05,"🌍",oppsN,"Different opponents faced."]);
  if(p.first) c.push([surprise(function(x){return x.first},p.first)-.1,"🌱",fshort(p.first),"First night on the board."]);
  if(p.games>=2) c.push([surprise(function(x){return x.games},p.games)-.1,"♜",p.games,"Games played in seasons 8 and 9."]);
  if(p.low&&p.peak&&p.peak[0]-p.low[0]>=150&&p.games>=10) c.push([surprise(function(x){return x.peak&&x.low?x.peak[0]-x.low[0]:0},p.peak[0]-p.low[0]),"🎢",(p.peak[0]-p.low[0])+" pts","Between their lowest and highest rating."]);
  c.sort(function(a,b){return b[0]-a[0]});
  return c.slice(0,5).map(function(f){return [f[1],f[2],f[3]]});
}

/* ---------- charts ---------- */
function svgWrap(inner,w,h,label){ return '<svg viewBox="0 0 '+w+' '+h+'" width="100%" style="display:block" role="img" aria-label="'+esc(label)+'">'+inner+'</svg>' }
function journey(p,rival){
  var h=p.hist; if(!h||h.length<2) return '<p style="color:var(--ink-3)">Not enough nights yet.</p>';
  var W=620,H=250,L=48,R=16,T=18,B=30, lo=1e9,hi=-1e9;
  h.forEach(function(x){lo=Math.min(lo,x[1]-x[2]);hi=Math.max(hi,x[1]+x[2])});
  if(rival&&rival.hist) rival.hist.forEach(function(x){lo=Math.min(lo,x[1]);hi=Math.max(hi,x[1])});
  var pad=(hi-lo)*.08||40; lo-=pad; hi+=pad;
  var st=[25,50,100,200,250,500].find(function(s){return (hi-lo)/s<=5})||1000;
  lo=Math.floor(lo/st)*st; hi=Math.ceil(hi/st)*st;
  var N=h.length, X=function(i){return L+i*(W-L-R)/(N-1)}, Y=function(v){return T+(hi-v)*(H-T-B)/(hi-lo)};
  var tv=[]; for(var v=lo;v<=hi+.5;v+=st) tv.push(v);
  var band=h.map(function(x,i){return X(i)+","+Y(x[1]+x[2])}).join(" ")+" "+h.map(function(x,i){return X(i)+","+Y(x[1]-x[2])}).reverse().join(" ");
  var path=h.map(function(x,i){return (i?"L":"M")+X(i)+","+Y(x[1])}).join(" ");
  var rv=""; if(rival&&rival.hist&&rival.hist.length>1){
    var rmap={}; rival.hist.forEach(function(x){rmap[x[0]]=x[1]});
    var pts=[]; h.forEach(function(x,i){ if(rmap[x[0]]!=null) pts.push((pts.length?"L":"M")+X(i)+","+Y(rmap[x[0]])) });
    if(pts.length>1) rv='<path d="'+pts.join(" ")+'" fill="none" stroke="#8A8276" stroke-width="2" stroke-dasharray="5 4"/>';
  }
  var pk=""; if(p.peak){ var pi=h.findIndex(function(x){return DATES[x[0]]===p.peak[1]});
    if(pi>=0) pk='<circle cx="'+X(pi)+'" cy="'+Y(p.peak[0])+'" r="3.5" fill="none" stroke="#FFF6E8" stroke-width="1.5"/>'+
      '<text x="'+X(pi)+'" y="'+(Y(p.peak[0])-10)+'" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="9" fill="#FFF6E8">peak</text>'; }
  var idx=[0,Math.floor((N-1)/3),Math.floor(2*(N-1)/3),N-1].filter(function(v,i,a){return a.indexOf(v)===i});
  return svgWrap(
    tv.map(function(v){return '<line x1="'+L+'" y1="'+Y(v)+'" x2="'+(W-R)+'" y2="'+Y(v)+'" stroke="#24282C"/><text x="'+(L-8)+'" y="'+(Y(v)+3.5)+'" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="9.5" fill="#8A8276">'+v+'</text>'}).join("")+
    '<polygon points="'+band+'" fill="rgba(254,39,58,.13)"/>'+rv+
    '<path d="'+path+'" fill="none" stroke="#FE273A" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>'+pk+
    '<circle cx="'+X(N-1)+'" cy="'+Y(h[N-1][1])+'" r="4" fill="#FE273A" stroke="#0C0D0E" stroke-width="2"/>'+
    idx.map(function(i){return '<text x="'+X(i)+'" y="'+(H-9)+'" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="9" fill="#8A8276">'+fshort(DATES[h[i][0]])+'</text>'}).join(""),
    W,H,p.n+" rating across "+N+" club nights, now "+p.r)+
    '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:.5rem;font-family:var(--fm);font-size:.62rem;color:var(--ink-3)">'+
    '<span><i style="display:inline-block;width:14px;border-top:2.6px solid #FE273A;vertical-align:.25em;margin-right:.3rem"></i>Rating</span>'+
    '<span><i style="display:inline-block;width:14px;height:9px;background:rgba(254,39,58,.13);vertical-align:-.1em;margin-right:.3rem"></i>Wiggle room</span>'+
    (rival?'<span><i style="display:inline-block;width:14px;border-top:2px dashed #8A8276;vertical-align:.25em;margin-right:.3rem"></i>'+esc(rival.n)+'</span>':'')+'</div>'+
    '<p class="cap">Rating after each of the last '+N+' club nights. The band is how sure the number is'+(p.peak?'; peak '+p.peak[0]+' on '+fshort(p.peak[1]):'')+'.</p>';
}
function nightly(p){
  var d=(p.nightly.length>1?p.nightly.filter(function(n){return !n.first}):p.nightly).slice(-16); if(!d.length) return '<p style="color:var(--ink-3)">No nights recorded.</p>';
  var W=620,H=190,L=40,R=12,T=14,B=34, mx=Math.max(20,Math.max.apply(null,d.map(function(x){return Math.abs(x.delta)})));
  var bw=(W-L-R)/d.length, Y0=T+(H-T-B)/2, k=(H-T-B)/2/mx;
  var ord=function(n){return n===1?"1st":n===2?"2nd":n===3?"3rd":n+"th"};
  return svgWrap(
    '<line x1="'+L+'" y1="'+Y0+'" x2="'+(W-R)+'" y2="'+Y0+'" stroke="#343A40"/>'+
    '<text x="'+(L-6)+'" y="'+(Y0+3)+'" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="9" fill="#8A8276">0</text>'+
    '<text x="'+(L-6)+'" y="'+(T+8)+'" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="9" fill="#8A8276">+'+Math.round(mx)+'</text>'+
    '<text x="'+(L-6)+'" y="'+(H-B+2)+'" text-anchor="end" font-family="JetBrains Mono,monospace" font-size="9" fill="#8A8276">-'+Math.round(mx)+'</text>'+
    d.map(function(x,i){
      var v=x.delta, hgt=Math.max(2,Math.abs(v)*k), y=v>=0?Y0-hgt:Y0;
      return '<rect x="'+(L+i*bw+bw*0.18)+'" y="'+y+'" width="'+(bw*0.64)+'" height="'+hgt+'" rx="1.5" fill="'+(v>0?"#3BC79A":v<0?"#F0883E":"#343A40")+'"><title>'+fshort(x.d)+": "+(v>0?"+":"")+v+" · "+x.w+"W "+x.dr+"D "+x.l+"L · "+x.pts+" pts, "+ord(x.place)+" of "+x.of+"</title></rect>";
    }).join("")+
    d.map(function(x,i){ return (i%Math.ceil(d.length/5)===0)?'<text x="'+(L+i*bw+bw/2)+'" y="'+(H-8)+'" text-anchor="middle" font-family="JetBrains Mono,monospace" font-size="8.5" fill="#8A8276">'+fshort(x.d)+'</text>':""}).join(""),
    W,H,"Rating points won or lost each night")+
    '<p class="cap">Points gained or lost on each of the last '+d.length+' nights played'+(p.nightly.length>1?', not counting the first night while the rating was still a guess':'')+'. Hover a bar for the record and where they finished that night.</p>';
}
function formStrip(p){
  var f=p.form||""; if(!f) return '<p style="color:var(--ink-3)">No games yet.</p>';
  return '<div class="strip">'+f.split("").map(function(c){return '<i class="'+c+'">'+c+'</i>'}).join("")+'</div>'+
   '<p class="cap">Last '+f.length+' games, oldest first. Longest run <b style="color:var(--gain)">'+p.streak[0]+'</b>'+(p.streak[1]>0?' &middot; on <b style="color:var(--gain)">'+p.streak[1]+'</b> right now':' &middot; not on a run')+'.</p>';
}
function bandsChart(p){
  var rows=p.bands.filter(function(b){return b[1]+b[2]+b[3]>0});
  if(!rows.length) return '<p style="color:var(--ink-3)">No games yet.</p>';
  var mx=Math.max.apply(null,rows.map(function(b){return b[1]+b[2]+b[3]}));
  return rows.map(function(b){ var g=b[1]+b[2]+b[3];
    return '<div class="bandrow"><span class="lb">'+b[0]+'</span><span class="bar" style="width:'+(g/mx*100)+'%">'+
      '<i class="bw" style="width:'+(b[1]/g*100)+'%"></i><i class="bd" style="width:'+(b[2]/g*100)+'%"></i><i class="bl" style="width:'+(b[3]/g*100)+'%"></i></span>'+
      '<span class="vv">'+b[1]+'-'+b[2]+'-'+b[3]+'</span></div>' }).join("")+
    '<p class="cap">Opponent strength at the time, first night not counted. Bar length is how often, colour is how it went.</p>';
}
function colourChart(p){
  var tw=p.wh[0]+p.wh[1]+p.wh[2], tb=p.bl[0]+p.bl[1]+p.bl[2], wp=cpct(p.wh), bp=cpct(p.bl);
  function block(lab,a,pc,tot){
    return '<div style="margin-bottom:.8rem"><div style="display:flex;justify-content:space-between;font-family:var(--fm);font-size:.62rem;color:var(--ink-3);margin-bottom:.3rem">'+
      '<span>'+lab+' &middot; '+tot+' games</span><span style="color:'+(pc>=50?"var(--gain)":"var(--loss)")+';font-weight:700">'+pc+'%</span></div>'+
      '<div class="bar"><i class="bw" style="width:'+(tot?a[0]/tot*100:0)+'%"></i><i class="bd" style="width:'+(tot?a[1]/tot*100:0)+'%"></i><i class="bl" style="width:'+(tot?a[2]/tot*100:0)+'%"></i></div>'+
      '<div style="font-family:var(--fm);font-size:.66rem;color:var(--ink-2);margin-top:.25rem">'+a[0]+' won &middot; '+a[1]+' drawn &middot; '+a[2]+' lost</div></div>';
  }
  return block("As White",p.wh,wp,tw)+block("As Black",p.bl,bp,tb)+'<p class="cap">'+(Math.abs(wp-bp)>=10?("Clearly stronger with "+(bp>wp?"Black":"White")+"."):"About the same either way.")+'</p>';
}
function rivalsChart(p){
  var rows=Object.keys(p.opp).map(function(o){var a=p.opp[o];return [o,a[0],a[1],a[2],a[0]+a[1]+a[2],a[0]-a[2]]}).sort(function(a,b){return b[4]-a[4]}).slice(0,8);
  if(!rows.length) return '<p style="color:var(--ink-3)">No opponents yet.</p>';
  var mx=Math.max.apply(null,rows.map(function(r){return Math.abs(r[5])}))||1;
  return rows.map(function(r){ var w=Math.abs(r[5])/mx*50;
    return '<div class="riv" data-o="'+esc(r[0])+'" style="cursor:pointer"><span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(r[0])+'</span>'+
      '<span class="rb"><span class="mid"></span>'+(r[5]>0?'<i class="p" style="width:'+w+'%"></i>':r[5]<0?'<i class="m" style="width:'+w+'%"></i>':'')+'</span>'+
      '<span class="rv" style="color:'+(r[5]>0?"var(--gain)":r[5]<0?"var(--loss)":"var(--ink-3)")+'">'+(r[5]>0?"+"+r[5]:r[5]===0?"=":r[5])+'</span></div>' }).join("")+
    '<p class="cap">Most-played opponents. Bar shows how far ahead or behind. Tap one to compare.</p>';
}
function attendance(p){
  return '<div class="att">'+DATES.map(function(d,i){return '<i class="'+(p.att[i]?"on":"")+'" title="'+fshort(d)+(p.att[i]?" — there":" — missed")+'"></i>'}).join("")+'</div>'+
   '<p class="cap">One block per club night, oldest first. There for <b style="color:var(--scarlet)">'+p.cons+'</b> of '+DATES.length+'.</p>';
}
function recentGames(p){
  if(!p.recent.length) return '<p style="color:var(--ink-3)">No games yet.</p>';
  var nd={}; p.nightly.forEach(function(n){nd[n.ni]=n});
  return '<div class="rg-wrap"><table class="rg"><tbody>'+p.recent.map(function(l){ var n=nd[l.ni], r=res(l);
    return '<tr><td class="d">'+fshort(DATES[l.ni])+'</td><td class="o" data-o="'+esc(l.o)+'"><i class="cc c'+l.c+'"></i>'+esc(l.o)+'<span style="font-family:var(--fm);font-size:.66rem;color:var(--ink-3)"> '+l.orat+'</span></td>'+
      '<td class="rs '+r+'">'+r+'</td><td class="dl2" style="color:'+(n&&n.delta>0?"var(--gain)":n&&n.delta<0?"var(--loss)":"var(--ink-3)")+'">'+(n?(n.delta>0?"+":"")+n.delta:"")+'</td></tr>' }).join("")+'</tbody></table></div>'+
    '<p class="cap">Newest first. The block is the side they had; the last column is the rating change for that whole night.</p>';
}
function milestones(p){
  if(!p.milestones.length) return '<p style="color:var(--ink-3)">Nothing yet — first game coming.</p>';
  return '<ul class="tl">'+p.milestones.map(function(m){return '<li><small>'+fshort(m[0])+'</small><b>'+esc(m[1])+'</b>'+(m[2]?' <span style="color:var(--ink-2)">— '+esc(m[2])+'</span>':'')+'</li>'}).join("")+'</ul>';
}
function vsTable(p){
  var opps=Object.keys(p.opp).sort(function(a,b){var A=p.opp[a],B=p.opp[b];return (B[0]+B[1]+B[2])-(A[0]+A[1]+A[2])});
  return opps.length?'<table style="font-size:.85rem"><tbody>'+opps.map(function(o){ var a=p.opp[o], k=a[0]>a[2]?"var(--gain)":a[0]<a[2]?"var(--loss)":"var(--ink-2)";
    return '<tr data-o="'+esc(o)+'" style="cursor:pointer"><td style="padding:.35rem .2rem">'+esc(o)+'</td><td style="text-align:right;padding:.35rem .2rem;font-family:var(--fm);color:'+k+';font-weight:700">'+a[0]+'–'+a[1]+'–'+a[2]+'</td></tr>'}).join("")+'</tbody></table>'
    :'<p style="color:var(--ink-3);font-size:.86rem;margin:0">No games on record yet.</p>';
}
function suggestRivals(p){
  var out=[], seen={};
  var add=function(n,lab){ if(n&&n!==p.n&&byN[n]&&!seen[n]){ seen[n]=1; out.push([n,lab]) } };
  var most=null; Object.keys(p.opp).forEach(function(o){ var g=p.opp[o][0]+p.opp[o][1]+p.opp[o][2]; if(!most||g>most[1]) most=[o,g] });
  if(most) add(most[0],"most played");
  if(p.nem&&p.nem[4]<0) add(p.nem[0],"nemesis");
  var close=null; P.forEach(function(x){ if(x.n===p.n||away(x)) return; var d=Math.abs(x.r-p.r); if(!close||d<close[1]) close=[x.n,d] });
  if(close) add(close[0],"closest rating");
  return out.slice(0,3);
}
function comparePanel(p){
  var opts=P.filter(function(x){return x.n!==p.n}).sort(function(a,b){return b.r-a.r});
  var sel='<div class="cmpsel"><label for="rivalSel">Compare with</label><select id="rivalSel"><option value="">Pick a player…</option>'+
    opts.map(function(o){return '<option value="'+esc(o.n)+'"'+(RIVAL&&RIVAL.n===o.n?" selected":"")+'>'+esc(o.n)+' — '+o.r+'</option>'}).join("")+'</select></div>';
  if(!RIVAL) return sel+'<p style="margin:.2rem 0 0;color:var(--ink-3);font-size:.88rem;line-height:1.5">Their rating line drops onto the journey chart, with the head-to-head and every stat side by side.</p>';
  var a=p.opp[RIVAL.n]||null, net=a?a[0]-a[2]:0;
  var lastMeet=null; for(var i=p.log.length-1;i>=0;i--){ if(p.log[i].o===RIVAL.n){ lastMeet=p.log[i]; break } }
  var groups=[["Strength",[["Rating",p.r,RIVAL.r],["Win rate",wr(p),wr(RIVAL),"%"],["Upsets",p.upsets,RIVAL.upsets],["Best run",p.streak[0],RIVAL.streak[0]]],true],
              ["Activity",[["Games",p.games,RIVAL.games],["Nights",p.cons,RIVAL.cons]],false],
              ["Style",[["As White",cpct(p.wh),cpct(RIVAL.wh),"%"],["As Black",cpct(p.bl),cpct(RIVAL.bl),"%"]],true]];
  var body=groups.map(function(g){ return '<div class="cgrp">'+g[0]+'</div>'+g[1].map(function(r){
    var A=r[1], B=r[2], suf=r[3]||"", tot=(A+B)||1, pa=Math.round(A/tot*100), pb=100-pa, aw=g[2]&&A>B, bw=g[2]&&B>A;
    return '<div class="cmprow"><div class="lab">'+r[0]+'</div><div class="line"><span class="va'+(aw?" win":"")+'">'+A+suf+'</span>'+
      '<span class="cmpbar"><i class="a'+(aw?" win":"")+'" style="width:'+pa+'%"></i><i class="b'+(bw?" win":"")+'" style="width:'+pb+'%"></i></span>'+
      '<span class="vb'+(bw?" win":"")+'">'+B+suf+'</span></div></div>' }).join("") }).join("");
  return sel+'<div class="vsbar"><div class="side"><b>'+esc(p.n)+'</b><span>'+p.r+'</span><em>this page</em></div>'+
   '<div class="mid"><em>Head to head</em><div class="sc2">'+(a?('<span style="color:'+(net>0?"var(--gain)":"var(--ink-2)")+'">'+a[0]+'</span><span style="color:var(--ink-3)">–</span><span style="color:'+(net<0?"var(--gain)":"var(--ink-2)")+'">'+a[2]+'</span>'):'<span style="color:var(--ink-3);font-size:.9rem">never met</span>')+'</div></div>'+
   '<div class="side"><b>'+esc(RIVAL.n)+'</b><span>'+RIVAL.r+'</span></div></div>'+
   (a?'<p style="text-align:center;font-family:var(--fm);font-size:.62rem;color:var(--ink-3);margin:-.6rem 0 1rem">'+(a[1]?a[1]+' drawn &middot; ':'')+'last met '+fshort(DATES[lastMeet.ni])+', '+esc(p.n)+' '+(lastMeet.s===1?"won":lastMeet.s===.5?"drew":"lost")+'</p>':'')+body;
}

/* ---------- profile ---------- */
function openProfile(n,rival){ if(!byN[n]) return; if(!CUR){ boardHash=stateHash(); boardScroll=scrollY } location.hash="#/p/"+encodeURIComponent(n)+(rival&&byN[rival]&&rival!==n?"/vs/"+encodeURIComponent(rival):"") }
function showProfile(n,rival){
  var p=byN[n]; if(!p) return;
  var same=CUR&&CUR.n===n; CUR=p; RIVAL=rival&&rival!==n?byN[rival]:null;
  document.title=p.n+" · KAVA Ladder";
  var tt=titleFor(p), el=$("#pnick");
  el.setAttribute("tabindex","0");
  el.innerHTML='<span class="ni">'+tt.ic+'</span>'+tt.name+'<span class="q" aria-hidden="true">?</span><span class="tip"><b>Why this title</b>'+esc(tt.why||"Earned from their record.")+'</span>';
  el.onclick=function(){ this.classList.toggle("open") };
  var hinted=false; try{ hinted=sessionStorage.getItem("kv-hint")==="1" }catch(e){}
  if(!hinted){ el.classList.add("open"); setTimeout(function(){ el.classList.remove("open") },2600); try{ sessionStorage.setItem("kv-hint","1") }catch(e){} }
  $("#pname").textContent=p.n;
  $("#psub").innerHTML='<span>'+esc(p.d)+'</span><span>'+p.games+' games</span>'+(p.rd>RS?'<span class="pill set">still settling · ±'+p.rd+'</span>':'')+(away(p)?'<span class="pill">away · no games in '+p.idle+' days</span>':'');
  $("#pact").innerHTML='<button class="cmpbtn" id="cmpGo">Compare with a rival</button>'+suggestRivals(p).map(function(r){return '<button class="chip" data-r="'+esc(r[0])+'"><small>'+r[1]+'</small>'+esc(r[0])+'</button>'}).join("");
  $("#cmpGo").onclick=function(){ var c=$("#cmpCard"); if(c){ c.scrollIntoView({behavior:"smooth",block:"start"}); var s=$("#rivalSel"); if(s&&!RIVAL) setTimeout(function(){ s.focus() },400) } };
  $("#kpis").innerHTML=
    '<div><dt>Rating</dt><dd>'+p.r+'<small>probably '+(p.r-Math.round(1.96*p.rd))+'–'+(p.r+Math.round(1.96*p.rd))+'</small></dd></div>'+
    '<div><dt>Record</dt><dd>'+p.rec.join("–")+'<small>W–D–L</small></dd></div>'+
    '<div><dt>Win rate</dt><dd style="color:'+(wr(p)>=50?"var(--gain)":"var(--loss)")+'">'+wr(p)+'%<small>across '+p.games+' games</small></dd></div>'+
    '<div><dt>Nights</dt><dd>'+p.cons+'<small>of '+DATES.length+'</small></dd></div>'+
    '<div class="hm"><dt>Peak</dt><dd>'+(p.peak?p.peak[0]+'<small>'+fshort(p.peak[1])+'</small>':'—')+'</dd></div>';
  $("#facts").innerHTML=facts(p).map(function(f){return '<div class="fact"><div class="ic">'+f[0]+'</div><b>'+f[1]+'</b><span>'+f[2]+'</span></div>'}).join("");
  drawGraphs();
  $("#board").classList.add("hid"); $("#pv").classList.remove("hid");
  if(!same) scrollTo({top:0,behavior:"instant"});
  $("#live").textContent=p.n+", "+tt.name;
}
function card(title,body,cls,id){ return '<div class="card'+(cls?" "+cls:"")+'"'+(id?' id="'+id+'"':'')+'><h3>'+title+'</h3>'+body+'</div>' }
function drawGraphs(){
  var p=CUR; if(!p) return;
  $("#graphs").innerHTML=
    card("Rating journey"+(RIVAL?" vs "+esc(RIVAL.n):""), journey(p,RIVAL), "gwide")+
    card("Points won and lost each night", nightly(p), "gwide")+
    card("Recent form", formStrip(p))+
    card("Against each level", bandsChart(p))+
    card("White and Black", colourChart(p))+
    card("Recent games", recentGames(p))+
    card("Rivals", rivalsChart(p))+
    card("Turnout", attendance(p));
  var leg=legacyFor(p);
  $("#graphs2").innerHTML=
    card("Compare with a rival", comparePanel(p), "gwide", "cmpCard")+
    card("Milestones", milestones(p))+
    card("Record against everyone", vsTable(p))+
    (leg?card("Legacy", leg):"");
  var s=$("#rivalSel"); if(s) s.onchange=function(){ location.hash="#/p/"+encodeURIComponent(p.n)+(this.value?"/vs/"+encodeURIComponent(this.value):"") };
}
$("#pv").onclick=function(e){
  var chip=e.target.closest("[data-r]"); if(chip&&CUR){ openProfile(CUR.n, chip.dataset.r); return }
  var o=e.target.closest("[data-o]"); if(o&&CUR){ if(e.target.closest(".riv,.rg")) openProfile(CUR.n, o.dataset.o); else openProfile(o.dataset.o) }
};
$("#bk").onclick=function(){ go(boardHash||"") };

/* ---------- wiring ---------- */
function rowKeys(e){ if((e.key==="Enter"||e.key===" ")&&e.target.matches("tr[data-n]")){ e.preventDefault(); openProfile(e.target.dataset.n) } }
["#tb","#tbAway","#arc"].forEach(function(s){ $(s).onclick=function(e){ var t=e.target.closest("[data-n]"); if(t) openProfile(t.dataset.n) }; $(s).addEventListener("keydown",rowKeys) });
$("#sorts").onclick=e=>{ const b=e.target.closest("[data-s]"); if(!b) return; sortK=b.dataset.s; go(stateHash()); $("#live").textContent="Sorted by "+SORT().t };
$("#awayBtn").onclick=()=>{ showAway=!showAway; draw() };
$("#pod").onclick=e=>{ const t=e.target.closest("[data-n]"); if(t) openProfile(t.dataset.n) };
window.matchMedia("(max-width:640px)").addEventListener("change",()=>{ if(xtShown) cross() });
drawArchive(); route();
<\/script></body></html>`;
}
