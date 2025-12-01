# 🔴 🔵 Vote Map Visualizer 🔴 🔵
👋 Hey! This is the vote visualizer. An easy to use python tool meant to help create graphics of votes in the US Senate and House of Represenatives (WIP).

## Features
The tool is CLI based. It captures vote information from clerk.house.gov (for the House) and senate.gov (for the Senate). It then displays these in a visually appealing graphic.

In the most recent stable build you can reliably display any Senate vote from the 101st congress to the current 119th. All you need is the roll call number (go to CLI usage to learn more).

The vizualization has serveral configuration settings which you can edit in the src/config file like the colors used, and font weights. Additionally, you can set the background to be transparent through a CLI tag (discussed later).

Roll call vote tallies are generally posted within an hour of a vote.


## Demo
As an example, lets take the August 7, 2022 vote on the Inflation Reduction Act. This was the 117th congress, 2nd session, and 325th roll call. We can call the command:

```python -m src.cli --chamber senate --congress 117 --session 2 --roll 325 --background transparent```

from the root directory. In this case, we use the --background tag, which is optional, to specify we want it to be transparent. This can make it easier to add the vizualization to your own graphics. The following .png file is then placed in the /out directory.

<img width="2140" height="1580" alt="Inflation reduction Act - Senate 117 - 2 - 325"  src="https://github.com/user-attachments/assets/9a231339-35fb-4634-bbf8-a327a69aefed" />


## Installation
To install the tool locally

1. Clone the repository
   `git clone https://github.com/yourusername/VoteMapMaker.git
    cd VoteMapMaker`
2. Create a virtual environment
   `.venv\Scripts\activate`
3. Install Dependencies
   `pip install -r requirements.txt`


## CLI Usage
The CLI tool has several flags:
- `--chamber`
    - This is set to either `senate` or `house`
- `--congress`
    - Set to a congress number, `101` - `119`+
- `--session`
    - Session number, either `1` or `2`
- `--roll`
    - Vote Number
- `--background`
    Optional, either `white` or `transparent`

Roll call numbers are made up of three different numbers, the congress, the session, and the roll call. For instance, the current congress is the 119th, so we start with 119. A congress is 2 years long, the session is that year, 1 or 2. The roll call is the vote number, so for the first vote of a session, it is 1.

An example usage would be 

```python -m src.cli --chamber senate --congress 119 --session 1 --roll 35 --background transparent``` 

which is the vote 119-1-35 found [here](https://www.senate.gov/legislative/LIS/roll_call_votes/vote1191/vote_119_1_00035.htm). It was a relatively boring confirmation of Eric Turner to the Secretary of Housing and Human Development.


## Senate Data Pipeline
1. Senate.py parses the CLI command to a Senate roll call XML URL
2. Takes the free to use XML off senate.gov
3. XML is parsed into a structures dataframe with state codes and vote values
4. Renders a semi-circle shape for each vote (two per state)


## House Data Pipeline
House data is a work in progress and does not currently work. It is partially implemented but has serious known issues with district matching, missing data, and geometry alignment. Expect changes as development continues.


## Testing
The testing suite is built with pytest. To run the test use `python -m pytest`.

*note* Tests cover the house section too, but many of these tests are stubs, incorrect, or do not work.


## Future Work
The House of Represenatives presents two challenges. One is in redistricting, which causes the maps to change at irregular intervals and makes it incredibly difficult to align votes with the actual districts which they represent. Additionally, with over 400 unique districts, vizualization becomes difficult. 

Currently, the Senate data only goes back to the 101st congress (1989). In the long term I would be interested in expanding this to historical data, however finding and storing this data is a massive task.


## License
MIT open source


## Acknowledgments / Resources
**U.S. Senate Roll Call Vote XML Feeds** — Publicly available vote data provided by senate.gov.

**U.S. House Clerk Vote Data** — Public vote data API from clerk.house.gov.

**US Census Data** — Publicly availible shape files for districts and states.
