"""Explicit opt-in Windows-local G-Labs smoke; generates one image and saves it.

Usage: python scripts/glabs_live_smoke.py --run-live --output outputs/glabs-smoke.png
Requires GLABS_API_KEY and G-Labs MAX webhook started. Never runs from CI.
"""
import argparse
import asyncio
from pathlib import Path
from studio.glabs import GlabsClient, ImageRequest

async def run(dest: Path) -> None:
    async with GlabsClient.from_env() as client:
        print("health:",await client.health())
        task=await client.submit(ImageRequest(
            prompt="One simple flat cartoon coffee cup, front view, centered, clean solid white background, no text",
            model="nano_banana_2",aspect_ratio="1:1"))
        print("task id:",task)
        result=await client.wait(task,max_polls=90,interval=4)
        print("saved:",await client.download(result["results"][0],dest))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--run-live",action="store_true")
    parser.add_argument("--output",type=Path,default=Path("outputs/glabs-smoke.png"))
    args=parser.parse_args()
    if not args.run_live:
        parser.error("Explicit --run-live required; this command consumes image quota.")
    asyncio.run(run(args.output))
