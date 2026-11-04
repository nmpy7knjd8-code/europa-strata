import json,sys,urllib.request,urllib.parse,importlib
UA={'User-Agent':'EuropaStrata-check/1.0 (garrett)'}
def api(params):
    params.update(format='json')
    r=urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params),headers=UA),timeout=30)
    return json.load(r)
def exists(names):
    ok={}
    for i in range(0,len(names),40):
        ch=names[i:i+40]
        d=api({'action':'query','titles':'|'.join('File:'+n for n in ch),'redirects':1})
        miss={p['title'] for p in d['query']['pages'].values() if 'missing' in p}
        norm={n['from']:n['to'] for n in d['query'].get('normalized',[])}
        for n in ch:
            t=norm.get('File:'+n,'File:'+n); ok[n]=t not in miss
    return ok
def search(q,n=6):
    d=api({'action':'query','list':'search','srsearch':q,'srnamespace':6,'srlimit':n})
    return [x['title'][5:] for x in d['query']['search']]
if __name__=='__main__':
    mod=importlib.import_module(sys.argv[1])
    names=[im[0] for p in mod.P for im in p['images']]
    ok=exists(names)
    for p in mod.P:
        for im in p['images']:
            if not ok[im[0]]: print('MISSING',p['id'],'|',im[0],'->',search(im[1][:60]))

def resolve(q):
    """exact file name if it exists, else first bitmap search hit"""
    if exists([q]).get(q): return q
    r=search(q+' filetype:bitmap',5)
    return r[0] if r else None
