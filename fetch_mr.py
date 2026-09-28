import json, urllib.request

cred = json.load(open('C:/Users/user/.config/fliflightmc/credentials.json', encoding='utf-8'))
token = cred['modrinth']['token']
user_id = cred['modrinth']['user_id']

def get(url):
    req = urllib.request.Request(url, headers={'Authorization': token, 'User-Agent': 'fliflight-stats/1.0'})
    return json.load(urllib.request.urlopen(req, timeout=30))

# list all projects by user
projs = get(f'https://api.modrinth.com/v2/user/{user_id}/projects')
print("TOTAL Modrinth projects:", len(projs))
rows = []
for p in projs:
    rows.append({
        'id': p['id'], 'slug': p['slug'], 'title': p['title'],
        'project_type': p['project_type'],
        'downloads': p.get('downloads'),
        'followers': p.get('followers'),
        'status': p.get('status'),
    })
rows.sort(key=lambda x: -(x['downloads'] or 0))
for r in rows:
    print(json.dumps(r))
