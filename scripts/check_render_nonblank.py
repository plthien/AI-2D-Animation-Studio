"""Cheap integration QC: reject a blank WebGL screenshot (not a quality assessment)."""
from __future__ import annotations
import sys
from PIL import Image

def check(path: str) -> None:
    im=Image.open(path).convert("RGB")
    width,height=im.size
    if width<200 or height<150:
        raise ValueError(f"Screenshot too small: {im.size}")
    # Player status label is beneath canvas. Inspect the top canvas region only.
    image=im.crop((0,0,min(width,640),min(height,480)))
    pixel=image.load()
    background=pixel[2,2]
    changed=0
    total=image.width*image.height
    for y in range(0,image.height,3):
        for x in range(0,image.width,3):
            rgb=pixel[x,y]
            if sum(abs(rgb[i]-background[i]) for i in range(3))>70:
                changed+=1
    fraction=changed/(len(range(0,image.height,3))*len(range(0,image.width,3)))
    if fraction<0.004:
        raise ValueError(f"Blank / near-blank render: {fraction:.4%} non-background pixels; bg={background}")
    print(f"Render is non-blank: {fraction:.2%} foreground pixels in screenshot")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python scripts/check_render_nonblank.py <screenshot.png>")
    check(sys.argv[1])
