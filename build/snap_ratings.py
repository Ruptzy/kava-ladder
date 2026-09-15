"""Record every player's rating as the replay computes it today.

check_site.py replays the same nights and refuses to publish if any rating
differs, so a change to the rating code, the seeds or the hidden list cannot
slip out unnoticed. Run this only when a difference is intended:
    python build/snap_ratings.py
and commit the new build/ratings.snapshot.json with the change that caused it.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import buildsite as B

HISTORY=B.load_history(); SEEDS=json.load(open(B.here('seeds.json')))
for n,r in B.night_seeds().items(): SEEDS.setdefault(n,r)
try: HIDDEN=json.load(open(B.here('hidden.json')))
except Exception: HIDDEN=[]
HISTORY,SEEDS=B.anonymise(HISTORY,SEEDS,HIDDEN)
P=B.run(HISTORY,SEEDS)
snap={"through":HISTORY[-1]["date"], "ratings":{n:round(p["r"]) for n,p in P.items() if p["n"]>0}}
json.dump(snap,open(B.here('ratings.snapshot.json'),'w',encoding='utf-8'),indent=0,sort_keys=True)
print('snapshot: %d players through %s' % (len(snap["ratings"]), snap["through"]))
