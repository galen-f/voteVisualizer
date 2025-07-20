# Vote Map Visualizer

This is a simple Python CLI tool that colors a map of the US based on how each state's two senators voted on a specific roll-call.
<br>
You need a congress number (119th Congress at time of writing), a session number (1st or 2nd year of that congress), and a roll-call (a three digit "vote number")
<ul>
<li> Retrieves the vote specified from the Senate's public XML feed.
<li> Classifies every state into one of six orientations (both Yea, Both Nay, split, etc.)
<li> Joins the data in the 50-state shape file and the vote data.
<li> Opens a Matplotlib window showing the coloured map.

## Quick Start
Clone the repo
`git clone {url}
cd vote‑map‑visualizer`

Install Dependencies
`pip install -r requirements.txt`

## Demo

## Contributing
Always feel free to pull, if you spot a bug or have an idea, open an issue or reach out to me on my socials.

## License
I don't care, just credit me please.