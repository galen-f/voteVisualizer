import argparse
from .maps.plot_house import render_map_house
from .maps.plot_senate import render_map_senate
from .senate import SenateSource
from .house import HouseSource
from .geo.load_geo import load_states, load_districts
from .geo.join_geo import join_votes
import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chamber", choices=["senate","house"], required=True)
    p.add_argument("--congress", type=int, required=True)
    p.add_argument("--session", type=int, required=True)
    p.add_argument("--roll", type=int, required=True)
    p.add_argument("--background", choices=["white", "transparent"], default="white", help="Background color")
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

    if args.chamber == "senate":
        print("Rendering Visualization...")
        fig = render_map_senate(merged, title=f"{args.chamber.title()} {args.congress}-{args.session}-{args.roll}", background=args.background)
    else:
        print("Rendering Visualization...")
        fig = render_map_house(merged, title=f"{args.chamber.title()} {args.congress}-{args.session}-{args.roll}", background=args.background)

    outfile = f"out/vote_{args.chamber}_{args.congress}_{args.session}_{args.roll}.png"
    plt.savefig(outfile, dpi=200, bbox_inches="tight")
    print(f"Saved {outfile}")
    plt.close("all")

if __name__ == "__main__":
    main()
