import argparse
from .plot import render_map
from .senate import present_senate_data, SenateSource
from .house import present_house_data, HouseSource
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

    print(f"Fetching Vote Data for {args.chamber}, {args.session}, {args.roll}...")

    if args.chamber == "senate":
        votes = SenateSource().fetch(args.congress, args.session, args.roll)
    else:
        votes = HouseSource().fetch(args.congress, args.roll)

    print("Loading Geometry...")
    shapes = load_states() if args.chamber == "senate" else load_districts()

    print("Joining Data...")
    merged = join_votes(args.chamber, votes, shapes)

    print("Rendering Visualization...")
    fig = render_map(merged, title=f"{args.chamber.title()} {args.congress}-{args.session}-{args.roll}")
    if not args.no_show:
        plt.show()

if __name__ == "__main__":
    main()
