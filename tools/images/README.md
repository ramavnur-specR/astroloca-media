# Scene images for image + caption posts
Cloudflare Workers AI, model flux-1-schnell, free. 1024x1024 JPEG (square, fine for IG/FB/TikTok feed).
Needs CF_ACCOUNT and CF_TOKEN in the environment (key lives in Ram's Drive, Publishing folder, "CLOUDFLARE KEY"). api.cloudflare.com must be in Claude's allowed websites.
Run: `python3 tools/images/gen_image.py "<prompt>" out.jpg` — then LOOK at the image before using it; rerun if hands, faces or the scene are off.
