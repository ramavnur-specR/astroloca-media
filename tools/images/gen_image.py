"""Generate a scene image with Cloudflare Workers AI (free tier).
Env: CF_ACCOUNT, CF_TOKEN (never commit them).
Usage: python3 gen_image.py "<prompt>" out.jpg
Model: flux-1-schnell (chosen 7 Nov 2026 over lucid-origin: closer to the prompt, fewer glitches). Output 1024x1024 JPEG.
"""
import os, sys, json, base64, urllib.request
MODEL = "@cf/black-forest-labs/flux-1-schnell"
acc, tok = os.environ["CF_ACCOUNT"], os.environ["CF_TOKEN"]
prompt, out = sys.argv[1], sys.argv[2]
req = urllib.request.Request(
    f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{MODEL}",
    data=json.dumps({"prompt": prompt, "steps": 8}).encode(),
    headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
j = json.loads(urllib.request.urlopen(req, timeout=180).read())
open(out, "wb").write(base64.b64decode(j["result"]["image"]))
print("ok", out)
