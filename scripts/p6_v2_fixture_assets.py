"""Deterministic artwork ONLY for CI end-to-end integration.

Production accepts external PNG images with identical catalog paths; no
G-Labs request is made here.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


def generate(root: Path) -> None:
    (root/"backgrounds").mkdir(parents=True, exist_ok=True)
    (root/"props").mkdir(parents=True, exist_ok=True)
    for name, wall, floor, window in (
        ("cafe_morning","#e9e1d2","#caa783","#9ac7d4"),
        ("cafe_evening","#9f9db6","#675d73","#f0b77c"),
    ):
        img=Image.new("RGB",(640,480),wall)
        art=ImageDraw.Draw(img)
        art.rectangle((0,332,639,479),fill=floor)
        art.rounded_rectangle((20,42,220,210),radius=9,fill=window,
                              outline="#554b50",width=7)
        art.line((120,42,120,210),fill="#554b50",width=5)
        art.rectangle((265,207,588,227),fill="#876449")
        art.rectangle((292,227,312,410),fill="#795741")
        art.rectangle((540,227,560,410),fill="#795741")
        art.rounded_rectangle((410,90,580,168),radius=14,
                              fill="#d7b89b",outline="#775d5a",width=5)
        img.save(root/"backgrounds"/(name+".png"))
    mug=Image.new("RGBA",(58,54),(0,0,0,0))
    pen=ImageDraw.Draw(mug)
    pen.rounded_rectangle((2,7,40,51),radius=5,fill="#c95848",
                          outline="#6d3538",width=4)
    pen.ellipse((34,17,55,39),outline="#6d3538",width=5)
    mug.save(root/"props"/"red_mug.png")
    print("Wrote 2 independent background PNGs and 1 prop texture")


if __name__=="__main__":
    generate(Path("runtime/fixtures"))
