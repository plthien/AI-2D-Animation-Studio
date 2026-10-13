"""P7 story B CI art. Two LIGHTING STATES of the SAME workshop preserve landmarks.

Only fixture creation; all rigging, asset resolution and animation remain the
unchanged shared P5/P6 runtime. No G-Labs or model API is contacted.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


def _workshop(path: Path, *, wall: str, floor: str, window: str,
              wood: str, detail: str) -> None:
    image=Image.new("RGB",(640,480),wall)
    art=ImageDraw.Draw(image)
    art.rectangle((0,341,639,479),fill=floor)
    # Same workbench, same window, same pegboard and same key hook in both states.
    art.rectangle((0,180,370,210),fill=wood)
    art.rectangle((0,210,22,358),fill=detail)
    art.rectangle((354,210,374,358),fill=detail)
    art.rounded_rectangle((20,35,235,150),radius=11,
                           fill=window,outline=detail,width=6)
    art.line((134,35,134,150),fill=detail,width=5)
    art.rounded_rectangle((400,42,599,184),radius=9,
                           fill=wood,outline=detail,width=5)
    for x in (433,486,539):
        art.rectangle((x,74,x+26,135),fill=detail)
    # The key is placed at (221,130): its RIGHT-HAND ring hangs at x≈234.
    art.line((234,102,234,130),fill=detail,width=5)
    art.ellipse((228,119,240,131),outline=detail,width=3)
    image.save(path)


def generate(root: Path) -> None:
    (root/"backgrounds").mkdir(parents=True,exist_ok=True)
    (root/"props").mkdir(parents=True,exist_ok=True)
    _workshop(root/"backgrounds"/"workshop_sunrise.png",
              wall="#e5d1a4",floor="#9c8060",window="#f9e0a0",
              wood="#705444",detail="#554235")
    _workshop(root/"backgrounds"/"workshop_twilight.png",
              wall="#9790a4",floor="#62586b",window="#dd9b79",
              wood="#6a5260",detail="#403c51")
    key=Image.new("RGBA",(58,54),(0,0,0,0))
    art=ImageDraw.Draw(key)
    art.ellipse((31,9,54,32),fill="#e8c16d",outline="#775a2e",width=4)
    art.ellipse((38,16,48,26),fill=(0,0,0,0),outline="#775a2e",width=2)
    art.rounded_rectangle((6,19,37,25),radius=2,fill="#dfb65a",
                          outline="#775a2e",width=2)
    art.rectangle((6,23,12,34),fill="#dfb65a",outline="#775a2e",width=2)
    art.rectangle((18,23,23,32),fill="#dfb65a",outline="#775a2e",width=2)
    key.save(root/"props"/"brass_key.png")
    print("P7 fixtures: SAME workshop geometry by day/dusk + new brass-key asset")


if __name__=="__main__":
    generate(Path("runtime/fixtures"))
