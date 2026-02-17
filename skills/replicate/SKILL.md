---
name: replicate
description: Generate images or videos via Replicate API (FLUX, Nano Banana Pro, Kling, etc.).
homepage: https://replicate.com
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "bins": ["uv"], "env": ["REPLICATE_API_TOKEN"] },
        "primaryEnv": "REPLICATE_API_TOKEN",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Replicate (Image & Video Generation)

Generate images or videos using Replicate's API. Supports multiple models for images (FLUX, Nano Banana Pro, Seedream) and videos (Kling).

## Image Generation

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png" [--model flux-schnell|nano-banana-pro|flux-2-pro] [--aspect-ratio 1:1|16:9|9:16]
```

## Video Generation (Text-to-Video)

```bash
uv run {baseDir}/scripts/generate_video.py --prompt "a cat walking on the beach at sunset" --filename "output.mp4" [--model kling-v2.1|kling-v2.6] [--aspect-ratio 16:9|9:16|1:1]
```

## Image-to-Video

```bash
uv run {baseDir}/scripts/generate_video.py --prompt "gentle camera zoom" --filename "output.mp4" -i "input.png"
```

## API Key

- `REPLICATE_API_TOKEN` env var (get from [replicate.com/account](https://replicate.com/account))
- Or set `skills.replicate.apiKey` / `skills.replicate.env.REPLICATE_API_TOKEN` in `~/.openclaw/openclaw.json`

## Notes

- Image models: flux-schnell (fast), nano-banana-pro (quality), flux-2-pro, seedream-4
- Video models: kling-v2.1-master (text-to-video), kling-v2.6 (latest, with audio)
- Scripts print `MEDIA:` line for OpenClaw to auto-attach on supported chat providers
- Video generation can take 1–3 minutes
