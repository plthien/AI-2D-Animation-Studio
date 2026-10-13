"""Compile a manual-AI motion JSON to deterministic per-frame data."""
from __future__ import annotations
import argparse
from pathlib import Path
from studio.motion import compile_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print("Compiled:", compile_file(args.source, args.destination))
