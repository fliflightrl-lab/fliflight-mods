import json, requests

CRED = json.load(open(r'C:\Users\user\.config\fliflightmc\credentials.json'))
HDR = {'Authorization': CRED['modrinth']['token']}
API = 'https://api.modrinth.com/v2'

def add_gallery(project, img, title, desc, featured=False, ordering=0):
    with open(img, 'rb') as f:
        data = f.read()
    h = dict(HDR)
    h['Content-Type'] = 'image/png'
    r = requests.post(
        f'{API}/project/{project}/gallery',
        headers=h,
        params={'ext': 'png', 'featured': str(featured).lower(), 'title': title,
                'description': desc, 'ordering': ordering},
        data=data
    )
    print(f'{project} <- {title}: {r.status_code} {r.text[:120]}')

G = r'C:\Users\user\fliflight-mods\dist\mod_gallery'

add_gallery('fliflight-custom-crosshair', G + r'\custom-crosshair-shapes.png',
            'The 5 crosshair shapes', 'Cross, dot, X, circle and T - switch instantly in-game.', featured=True, ordering=0)
add_gallery('fliflight-custom-crosshair', G + r'\custom-crosshair-gui.png',
            'In-game settings screen', 'Press C to open the settings: shape, color, size, thickness, gap, presets.', ordering=1)
add_gallery('fliflight-pvphud', G + r'\pvphud-hud.png',
            'PvP HUD overlay', 'FPS, ping, coordinates and clicks-per-second in the top-left corner.', featured=True, ordering=0)
