"""List every era-tab map feature that would show the "No Europa Strata profile yet" fallback. Exit 1 if any."""
import json,collections,sys,os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
prof=json.load(open('data/kingdom-eras/basemap-profiles.json'))['profiles']
def find(n,t,y):
  for e in prof:
    if n in e['names'] and (not e.get('when') or f"{t}:{y}" in e['when']): return e
used=set();fb=[];per=collections.Counter();unn=collections.Counter()
for t in ['high-medieval','renaissance','early-modern','modern']:
  topo=json.load(open(f'data/kingdom-eras/geo/{t}.topo.json'))
  ids={p['id'] for p in json.load(open(f'data/kingdom-eras/{t}.json'))['polities']}
  for k,o in topo['objects'].items():
    seen=set()
    for g in o['geometries']:
      pr=g.get('properties') or {}
      if pr.get('polityId') in ids: continue
      n=(pr.get('name') or '').strip()
      if not n: unn[f"{t}:{k[1:]}"]+=1; continue
      e=find(n,t,k[1:])
      if not e: fb.append((t,k,n))
      else:
        used.add(e['id'])
        if e['id'] not in seen: seen.add(e['id']); per[t]+=1
print('FALLBACKS',len(fb),fb)
print('profile-stops per tab',dict(per))
print('unused',[e['id'] for e in prof if e['id'] not in used])
print('unnamed features total',sum(unn.values()))
sys.exit(1 if fb else 0)
