"""One authored action JSON + an independently generated rig -> Spine motion poses."""
import argparse
from pathlib import Path
from studio.retarget import compile_retargeted_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("profile", type=Path)
    parser.add_argument("skeleton", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print("Retargeted:", compile_retargeted_file(args.source, args.profile, args.skeleton, args.output))
