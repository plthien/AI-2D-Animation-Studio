"""Kokoro-local PCM WAVs (or CI signal fixtures) -> exact 24 FPS audio track."""
import argparse
from pathlib import Path
from studio.voice import assemble_file

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("timeline",type=Path)
    parser.add_argument("voices",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("manifest",type=Path)
    args=parser.parse_args()
    print(assemble_file(args.timeline,args.voices,args.output,args.manifest))
