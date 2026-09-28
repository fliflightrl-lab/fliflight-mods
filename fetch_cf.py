import json, urllib.request

cred = json.load(open('C:/Users/user/.config/fliflightmc/credentials.json', encoding='utf-8'))
key = cred['curseforge']['api_key']
author_id = cred['curseforge']['author_id']

def get(url):
    req = urllib.request.Request(url, headers={'x-api-key': key, 'User-Agent': 'fliflight-stats/1.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

url = 'https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter=Fliflightmc&pageSize=50'
r = get(url)
print("TOTAL search hits:", r['pagination']['totalCount'])
mods = []
for m in r['data']:
    authors = m.get('authors', [])
    if any(a.get('id') == author_id for a in authors):
        mods.append(m)

print("Mods by author:", len(mods))
for m in mods:
    print(json.dumps({
        'id': m['id'], 'name': m['name'], 'slug': m['slug'],
        'classId': m.get('classId'),
        'downloadCount': m.get('downloadCount'),
        'status': m.get('status'),
    }))
