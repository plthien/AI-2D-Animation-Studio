"""Deterministic synthetic character to test the real Genielabs pipeline without AI image calls."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

def make_body():
    im=Image.new("RGBA",(145,170),(0,0,0,0))
    draw=ImageDraw.Draw(im)
    draw.rounded_rectangle((8,5,137,161),radius=21,fill="#ce8850",outline="#222c40",width=5)
    for i in range(20,130,22):
        draw.line((i,35,i,130),fill="#9b563e",width=3)
    draw.rectangle((29,122,116,133),fill="#713629")
    return im

def make_head():
    im=Image.new("RGBA",(110,105),(0,0,0,0))
    draw=ImageDraw.Draw(im)
    draw.ellipse((6,4,104,102),fill="#32485a",outline="#131a21",width=5)
    draw.ellipse((29,37,43,54),fill="white")
    draw.ellipse((66,37,80,54),fill="white")
    draw.ellipse((35,41,39,50),fill="#101b25")
    draw.ellipse((72,41,76,50),fill="#101b25")
    draw.arc((36,51,78,83),0,170,fill="#f0f0ed",width=3)
    return im

def paste_white(bg, image, pos):
    bg.paste(image,pos,image)

def main():
    base=Path("outputs/p2_fixture")
    base.mkdir(parents=True,exist_ok=True)
    atlas=Image.new("RGB",(510,420),"white")
    reference=Image.new("RGB",(340,440),"white")
    head,body=make_head(),make_body()
    paste_white(atlas,head,(42,20))
    paste_white(atlas,body,(270,180))
    paste_white(reference,head,(115,55))
    paste_white(reference,body,(96,177))
    atlas.save(base/"parts_atlas.png")
    reference.save(base/"reference.png")
    (base/"semantic.json").write_text(json.dumps({"part_00":"head","part_01":"torso"},indent=2))
    (base/"anchors.json").write_text(json.dumps({"head":{"x":170,"y":100},"torso":{"x":170,"y":220}},indent=2))
    print("Synthetic P2 fixture at",base)

if __name__=="__main__":
    main()
