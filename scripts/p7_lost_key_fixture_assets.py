"""P7 STORY B TEST ART ONLY: new sets, no G-Labs or story-specific runtime code.

Generates workshop/hallway backgrounds and a brass-key RGBA sprite. All
paths are declared in the Story B AssetCatalog, never in the P6 renderer.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


def generate(root: Path) -> None:
    (root / "backgrounds").mkdir(parents=True, exist_ok=True)
    (root / "props").mkdir(parents=True, exist_ok=True)
    workshop=Image.new("RGB",(640,480),"#e5d1a4")
    art=ImageDraw.Draw(workshop)
    art.rectangle((0,341,639,479),fill="#9c8060")
    art.rectangle((0,180,370,210),fill="#705444")
    art.rectangle((0,210,22,358),fill="#5e4638")
    art.rectangle((354,210,374,358),fill="#5e4638")
    art.rounded_rectangle((20,35,235,150),radius=11,fill="#f9e0a0",outline="#705444",width=6)
    art.line((134,35,134,150),fill="#705444",width=5)
    art.rounded_rectangle((400,42,599,184),radius=9,fill="#c19a76",outline="#63493c",width=5)
    for x in (433,486,539):
        art.rectangle((x,74,x+26,135),fill="#546674")
    art.line((190,145,190,175),fill="#8b644b",width=4)
    workshop.save(root/"backgrounds"/"workshop_sunrise.png")
    hallway=Image.new("RGB",(640,480),"#9691a5")
    pen=ImageDraw.Draw(hallway)
    pen.rectangle((0,340,639,479),fill="#6d5b69")
    pen.rectangle((375,35,594,334),fill="#565369",outline="#d0b4a2",width=10)
    pen.ellipse((545,173,560,190),fill="#d9ae69")
    pen.rounded_rectangle((166,95,290,207),radius=7,fill="#bba58f",outline="#514651",width=4)
    pen.line((221,111,221,145),fill="#c9a168",width=5)
    pen.rectangle((246,183,528,198),fill="#8b7168")
    pen.rectangle((269,198,282,354),fill="#776359")
    pen.rectangle((496,198,509,354),fill="#776359")
    hallway.save(root/"backgrounds"/"hallway_twilight.png")
    key=Image.new("RGBA",(58,54),(0,0,0,0))
    art=ImageDraw.Draw(key)
    # Ring on the right: the existing -16px grip socket meets its loop.
    art.ellipse((31,9,54,32),fill="#e8c16d",outline="#775a2e",width=4)
    art.ellipse((38,16,48,26),fill=(0,0,0,0),outline="#775a2e",width=2)
    art.rounded_rectangle((6,19,37,25),radius=2,fill="#dfb65a",outline="#775a2e",width=2)
    art.rectangle((6,23,12,34),fill="#dfb65a",outline="#775a2e",width=2)
    art.rectangle((18,23,23,32),fill="#dfb65a",outline="#775a2e",width=2)
    key.save(root/"props"/"brass_key.png")
    print("P7 new story fixtures: 2 location PNGs and one non-coffee brass key PNG")


if __name__ == "__main__":
    generate(Path("runtime/fixtures"))
