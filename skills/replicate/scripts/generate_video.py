#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "replicate>=1.0.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Generate videos via Replicate API (text-to-video or image-to-video).

Usage:
    uv run generate_video.py --prompt "a cat walking on the beach" --filename "output.mp4"
    uv run generate_video.py --prompt "gentle zoom" --filename "out.mp4" -i "first_frame.png"
"""

import argparse
import os
import sys
from pathlib import Path

VIDEO_MODELS = {
    "kling-v2.1": {
        "replicate_id": "kwaivgi/kling-v2.1-master",
        "aspect_ratios": ["16:9", "9:16", "1:1"],
        "default_ratio": "16:9",
        "modes": ["standard", "pro"],
        "duration": 5,
    },
    "kling-v2.6": {
        "replicate_id": "kwaivgi/kling-v2.6",
        "aspect_ratios": ["16:9", "9:16", "1:1"],
        "default_ratio": "16:9",
        "modes": ["standard", "pro"],
        "duration": 5,
    },
}


def get_api_token(provided: str | None) -> str | None:
    if provided:
        return provided
    return os.environ.get("REPLICATE_API_TOKEN")


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos via Replicate API"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Video description/prompt")
    parser.add_argument("--filename", "-f", required=True, help="Output filename (e.g., output.mp4)")
    parser.add_argument(
        "--input-image", "-i",
        dest="input_image",
        help="First frame for image-to-video (path or URL)",
    )
    parser.add_argument(
        "--model", "-m",
        choices=list(VIDEO_MODELS),
        default="kling-v2.1",
        help="Model to use (default: kling-v2.1)",
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        help="Aspect ratio (16:9, 9:16, 1:1)",
    )
    parser.add_argument(
        "--mode",
        choices=["standard", "pro"],
        default="standard",
        help="standard=720p, pro=1080p",
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=5,
        help="Duration in seconds (default: 5)",
    )
    parser.add_argument(
        "--api-token", "-k",
        help="Replicate API token (overrides REPLICATE_API_TOKEN env)",
    )

    args = parser.parse_args()

    token = get_api_token(args.api_token)
    if not token:
        print("Error: No API token provided.", file=sys.stderr)
        print("Set REPLICATE_API_TOKEN or use --api-token", file=sys.stderr)
        sys.exit(1)

    model_info = VIDEO_MODELS[args.model]
    aspect_ratio = args.aspect_ratio or model_info["default_ratio"]
    if aspect_ratio not in model_info["aspect_ratios"]:
        aspect_ratio = model_info["default_ratio"]

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    import replicate

    client = replicate.Client(api_token=token)
    replicate_id = model_info["replicate_id"]

    input_params = {
        "prompt": args.prompt,
        "aspect_ratio": aspect_ratio,
        "mode": args.mode,
        "duration": args.duration,
    }

    if args.input_image:
        path = Path(args.input_image)
        if path.exists():
            input_params["start_image"] = open(path, "rb")
        else:
            input_params["start_image"] = args.input_image

    print(f"Generating video with {replicate_id}...", file=sys.stderr)

    try:
        output = client.run(replicate_id, input=input_params)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle output: FileOutput, string URL, or list
    content = None
    url = None
    if isinstance(output, list) and len(output) > 0:
        first = output[0]
        if hasattr(first, "read") and callable(first.read):
            content = first.read()
        elif hasattr(first, "url") and callable(first.url):
            url = first.url()
        elif isinstance(first, str):
            url = first
    elif output and hasattr(output, "read") and callable(output.read):
        content = output.read()
    elif output and hasattr(output, "url") and callable(output.url):
        url = output.url()
    elif isinstance(output, str):
        url = output

    if content is not None:
        output_path.write_bytes(content)
    elif url:
        import httpx
        print(f"Downloading to {output_path}...", file=sys.stderr)
        resp = httpx.get(url, follow_redirects=True)
        resp.raise_for_status()
        output_path.write_bytes(resp.content)
    else:
        print("Error: No video in response", file=sys.stderr)
        sys.exit(1)

    full_path = output_path.resolve()
    print(f"\nVideo saved: {full_path}")
    print(f"MEDIA: {full_path}")


if __name__ == "__main__":
    main()
