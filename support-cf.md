# Réponse au support CurseForge — capture brute de la requête (2e échange)

> Réponse du support : « could you please provide a sample of the raw HTTP request you're sending (including headers, but with the actual token redacted) and the full response body? »
>
> Réponse ci-dessous, avec token masqué. Les captures sont **réelles** (rejouées le 15/08/2026 via `scripts/capture_cf_evidence.py`).

---

## 🇬🇧 Message de suivi à envoyer

**Subject: Re: Upload API rejects every API key as "malformed" — raw request + response**

Hi, thanks for the quick reply. Here are the raw request and the full response body. The token is redacted.

**1. The upload request (exactly what my tooling sends):**

```
POST /api/projects/123880127/upload-file HTTP/1.1
Host: minecraft.curseforge.com
X-Api-Token: REDACTED
User-Agent: fliflight-mods/1.0
Accept: */*
Content-Type: multipart/form-data; boundary=----fliflight-test-boundary
Content-Length: 537

------fliflight-test-boundary
Content-Disposition: form-data; name="metadata"

{"changelog": "test", "changelogType": "text", "displayName": "test", "gameVersions": [12656], "releaseType": "release"}
------fliflight-test-boundary
Content-Disposition: form-data; name="file"; filename="test.zip"
Content-Type: application/zip

PK... [zip bytes, sent in full]
------fliflight-test-boundary--
```

**Full response body (HTTP 400):**

```json
{"errorCode":3,"errorMessage":"API token is malformed. Token provided: REDACTED"}
```

**2. Key observation:** the error message **echoes the token back** ("Token provided: ..."). This proves the token IS received and parsed by the server — the failure is in the server-side validation of the token's *format*, not in how it's transmitted. The same token works fine on the read API (`api.curseforge.com/v1`, HTTP 200), so the token is valid; the legacy upload endpoint appears to reject the current token format (`$2a$10$...`) at the server side.

**3. Additional data point:** a `GET` on the same path returns `HTTP 302` redirected to `/error?aspxerrorpath=/api/projects/123880127/upload-file` (ASP.NET MVC 5.2, behind Cloudflare — headers `x-aspnetmvc-version: 5.2`, `x-aspnet-version: 4.0.30319`).

**What I need:** either the legacy upload endpoint fixed to accept current API keys, or the officially supported upload endpoint + auth method going forward. Happy to provide more captures or test anything your team suggests.

Thanks,
Fliflightmc

---

## Notes techniques (pour toi)

- **Point décisif** : le serveur echo le token dans l'erreur → transmission OK, c'est la validation du format côté serveur qui échoue (les tokens `$2a$10$…` ne passent plus depuis le changement du 2026-07-15).
- **GET** sur ce chemin → 302 vers `/error` : la route legacy n'existe qu'en POST, c'est un vieux ASP.NET MVC derrière Cloudflare.
- Rejouable à tout moment : `python3 scripts/capture_cf_evidence.py` (token lu depuis credentials.json, masqué à l'affichage).
- ⚠️ L'erreur serveur renvoie le token en clair dans `errorMessage` — ne jamais poster la capture sans le masquer (le script le fait automatiquement).

---

## ✂️ Version courte — 2e échange (485 caractères — pour formulaires limités)

Hi, here's the raw request+response. POST /api/projects/123880127/upload-file on minecraft.curseforge.com, header X-Api-Token: <REDACTED>, multipart body (metadata+zip). Response 400 {"errorCode":3,"errorMessage":"API token is malformed. Token provided: <REDACTED>"}. The server echoes the token back, so it IS received - failure is server-side format validation, not transmission. Same token works on api.curseforge.com/v1 (200). Please fix the endpoint or confirm the current method.
