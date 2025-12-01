# Vote Map Visualizer

This is a simple Python CLI tool that colors a map of the US based on how each state's two senators voted on a specific roll-call.
<br>
You need a congress number (119th Congress at time of writing), a session number (1st or 2nd year of that congress), and a roll-call (a three digit "vote number")
<ul>
<li> Retrieves the vote specified from the Senate's public XML feed.
<li> Classifies each Senate seat into Yea, Nay, Present, or Not Voting.
<li> Visualizes the data in a grid.
<li> Downloads a .png file of the visualization in out/..

## Quick Start
Clone the repo
`git clone {url}
cd vote‑map‑visualizer`

Install Dependencies
`WIP`

To generate a map, from the root use a command such as: ```python -m src.cli --chamber senate --congress 117 --session 2 --roll 325``` for vote 117-2-325 (the inflation reduction act).

## Notes
Works on 101st congress - 119th (current) and (hopefully) future congresses

## Demo
<img width="1440" height="792" alt="seateVoteMap" src="https://github.com/user-attachments/assets/4b62107b-e00a-4b1a-aa2b-e9056ffa56c4" />
Vote map of the vote 119-1-416 of the US Senate.

## Contributing
Always feel free to pull, if you spot a bug or have an idea, open an issue or reach out to me on my socials.

## License
I don't care, just credit me please.
