# CellVQ Model Weight Download — SharePoint Technique

## Model Info
- **Model**: CellVQ (A4Bio/CellVQ, Nature Communications)
- **File**: `models.ckpt` — 1,366 MB (~1.37 GB)
- **Source**: SharePoint public folder (not GitHub/HuggingFace)
- **Repository**: https://github.com/A4Bio/CellVQ

## Download URL
```
SharePoint folder: https://hopebio2020.sharepoint.com/:f:/s/PublicSharedfiles/EmUQnvZMETlDvoCaBduCNeIBQArcOrd8T8iEpiGofFZ9CQ
File inside: models.ckpt
```

## Download Technique: curl with FedAuth cookies

SharePoint requires authentication even for "public" files. The approach:

### Step 1: Get FedAuth cookie by visiting the public share
```bash
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy  # bypass GFW proxy for M365
curl -s -c /tmp/sp_cookies.txt -L \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://hopebio2020.sharepoint.com/:f:/s/PublicSharedfiles/EmUQnvZMETlDvoCaBduCNeIBQArcOrd8T8iEpiGofFZ9CQ?e=3SpPZU" \
  -o /dev/null
```

### Step 2: Download with cookies + resume support
```bash
curl -L -C - -b /tmp/sp_cookies.txt \
  -H "User-Agent: Mozilla/5.0 ..." \
  "https://hopebio2020.sharepoint.com/sites/PublicSharedfiles/_layouts/15/download.aspx?SourceUrl=%2Fsites%2FPublicSharedfiles%2FShared%20Documents%2FPublic%20Shared%20files%2Fmodels%2Eckpt" \
  -o /Users/aj/.hermes/data/models/models.ckpt \
  --connect-timeout 30 --max-time 7200 \
  --retry 3 --retry-delay 10
```

### Key Points
- `unset HTTP_PROXY` — SharePoint (M365) is accessible without proxy in China
- `-C -` — resume interrupted downloads
- `FedAuth` cookie in cookie jar is the auth token
- Direct `download.aspx` URL works after cookie is obtained
- Run in background with long timeout (1.37GB takes 10-30 min)

## Pitfalls
- Browser-based download (Browserbase/Playwright) saves to remote machine, not local
- `requests` library through GFW proxy times out
- Rclone `:http:` remote gets 403 without auth cookies
- SharePoint REST API (`_api/web/GetFileByServerRelativePath`) returns 403

## Destination
```
/Users/aj/.hermes/data/models/models.ckpt
```

Corresponds to CellVQ README default: `pretrained_model/checkpoint.pt`
