import argparse
from .plot import render_map
from .senate import present_senate_data
from .house import present_house_data
from .geo.load_geo import load_states, load_districts
from .geo.join_geo import join_votes
import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chamber", choices=["senate","house"], required=True)
    p.add_argument("--congress", type=int, required=True)
    p.add_argument("--session", type=int, required=True)
    p.add_argument("--roll", type=int, required=True)
    p.add_argument("--no-show", action="store_true", help="Do not open a window (CI-safe)")
    args = p.parse_args()

    source = present_senate_data() if args.chamber == "senate" else present_house_data()

    votes = source.fetch(args.congress, args.session, args.roll)
    shapes = load_states() if args.chamber == "senate" else load_districts()
    merged = join_votes(args.chamber, votes, shapes)

    fig = render_map(merged, title=f"{args.chamber.title()} {args.congress}-{args.session}-{args.roll}")
    if not args.no_show:
        plt.show()

if __name__ == "__main__":
    main()
