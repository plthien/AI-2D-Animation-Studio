"""Manual AI FilmPlan + compiled P4 spine poses -> exact film and narration timing."""
import argparse
from pathlib import Path
from studio.film import compile_film_file

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("asset", type=Path, help="Previously compiled 48-frame P4 world motion JSON")
    parser.add_argument("out", type=Path)
    args=parser.parse_args()
    print(compile_film_file(args.plan, {"baseline":args.asset}, args.out))
