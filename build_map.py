"""
Senate Vote Visualizer
Fetches US Senate vote data and displays results on a US map
"""

import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import numpy as np
from collections import defaultdict

# State positions for the map (approximate coordinates)
STATE_POSITIONS = {
    'AL': (86.79, 32.77), 'AK': (152.40, 64.20), 'AZ': (111.09, 34.27),
    'AR': (92.37, 34.91), 'CA': (119.41, 36.77), 'CO': (105.31, 39.05),
    'CT': (72.74, 41.76), 'DE': (75.50, 39.00), 'FL': (81.69, 27.77),
    'GA': (83.44, 33.76), 'HI': (157.50, 21.31), 'ID': (114.74, 44.07),
    'IL': (88.99, 40.63), 'IN': (86.15, 39.79), 'IA': (93.62, 42.03),
    'KS': (98.48, 38.50), 'KY': (84.67, 37.84), 'LA': (91.98, 30.99),
    'ME': (69.32, 44.32), 'MD': (76.50, 39.05), 'MA': (71.38, 42.41),
    'MI': (84.72, 43.33), 'MN': (95.01, 45.39), 'MS': (89.40, 32.35),
    'MO': (92.60, 38.57), 'MT': (110.36, 47.05), 'NE': (99.68, 41.49),
    'NV': (117.05, 39.16), 'NH': (71.55, 43.95), 'NJ': (74.76, 40.22),
    'NM': (106.25, 34.31), 'NY': (74.22, 42.16), 'NC': (78.64, 35.77),
    'ND': (99.78, 47.41), 'OH': (82.76, 40.27), 'OK': (97.53, 35.01),
    'OR': (123.03, 44.93), 'PA': (77.19, 40.27), 'RI': (71.42, 41.70),
    'SC': (80.95, 33.84), 'SD': (99.90, 44.30), 'TN': (86.58, 35.86),
    'TX': (97.56, 31.05), 'UT': (111.89, 39.32), 'VT': (72.71, 44.56),
    'VA': (78.17, 37.77), 'WA': (121.49, 47.75), 'WV': (80.95, 38.84),
    'WI': (89.62, 44.27), 'WY': (107.30, 42.75)
}

# Color mapping
COLORS = {
    'Yea': 'green',
    'Nay': 'red',
    'Split': 'yellow',
    'Not Voting': 'lightgray',
    'Absent': 'lightgray'
}

class SenateVoteVisualizer:
    def __init__(self):
        self.vote_data = {}
        self.vote_info = {}
        
    def fetch_vote_data(self, congress, session, roll_call):
        """
        Fetch vote data from Senate.gov XML API
        
        Args:
            congress (int): Congress number (e.g., 119)
            session (int): Session number (1 or 2)
            roll_call (int): Roll call number
        """
        # Format the URL according to the API specification
        url = f"https://www.senate.gov/legislative/LIS/roll_call_votes/vote{congress}{session}/vote_{congress:03d}_{session}_{roll_call:05d}.xml"
        
        try:
            print(f"Fetching data from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Extract vote information
            self.vote_info = {
                'congress': root.find('congress').text if root.find('congress') is not None else str(congress),
                'session': root.find('session').text if root.find('session') is not None else str(session),
                'vote_number': root.find('vote_number').text if root.find('vote_number') is not None else str(roll_call),
                'vote_date': root.find('vote_date').text if root.find('vote_date') is not None else 'Unknown',
                'question': root.find('question').text if root.find('question') is not None else 'Unknown',
                'vote_title': root.find('vote_title').text if root.find('vote_title') is not None else 'Unknown'
            }
            
            # Extract member votes
            self.vote_data = defaultdict(list)
            
            members = root.find('members')
            if members is not None:
                for member in members.findall('member'):
                    state = member.find('state').text if member.find('state') is not None else None
                    vote_cast = member.find('vote_cast').text if member.find('vote_cast') is not None else 'Not Voting'
                    
                    if state:
                        self.vote_data[state].append(vote_cast)
            
            print(f"Successfully fetched vote data for {len(self.vote_data)} states")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return False
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def determine_state_vote(self, votes):
        """
        Determine the overall state vote based on individual senator votes
        
        Args:
            votes (list): List of votes from the state's senators
            
        Returns:
            str: Overall state vote ('Yea', 'Nay', 'Split', etc.)
        """
        if not votes:
            return 'Not Voting'
        
        # Count different vote types
        vote_counts = defaultdict(int)
        for vote in votes:
            vote_counts[vote] += 1
        
        # Determine state result
        yea_count = vote_counts.get('Yea', 0)
        nay_count = vote_counts.get('Nay', 0)
        
        if yea_count > 0 and nay_count > 0:
            return 'Split'
        elif yea_count > nay_count:
            return 'Yea'
        elif nay_count > yea_count:
            return 'Nay'
        else:
            # Handle cases where neither Yea nor Nay (e.g., all abstentions)
            most_common_vote = max(vote_counts, key=vote_counts.get)
            return most_common_vote if most_common_vote in ['Yea', 'Nay'] else 'Not Voting'
    
    def create_map(self):
        """Create and display the vote visualization map"""
        if not self.vote_data:
            print("No vote data available. Please fetch vote data first.")
            return
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        
        # Set map bounds (approximate US boundaries)
        ax.set_xlim(-180, -60)
        ax.set_ylim(15, 75)
        
        # Plot states
        for state, position in STATE_POSITIONS.items():
            lon, lat = position
            
            # Determine state vote
            state_votes = self.vote_data.get(state, [])
            state_result = self.determine_state_vote(state_votes)
            
            # Get color
            color = COLORS.get(state_result, 'lightgray')
            
            # Create state marker
            circle = plt.Circle((-lon, lat), 2, color=color, alpha=0.8, zorder=2)
            ax.add_patch(circle)
            
            # Add state label
            ax.text(-lon, lat, state, ha='center', va='center', 
                   fontsize=8, fontweight='bold', zorder=3)
        
        # Add title and legend
        title = f"Senate Vote {self.vote_info.get('vote_number', 'Unknown')}"
        if self.vote_info.get('vote_title', '') != 'Unknown':
            title += f": {self.vote_info.get('vote_title', '')}"
        title += f"\nCongress {self.vote_info.get('congress', '')}, Session {self.vote_info.get('session', '')}"
        title += f" | Date: {self.vote_info.get('vote_date', 'Unknown')}"
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Create legend
        legend_elements = []
        for vote_type, color in COLORS.items():
            if vote_type in ['Yea', 'Nay', 'Split']:
                legend_elements.append(plt.Circle((0,0), 1, color=color, label=vote_type))
        
        ax.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0, 0))
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    
    def print_vote_summary(self):
        """Print a summary of the vote results"""
        if not self.vote_data:
            print("No vote data available.")
            return
        
        print("\n" + "="*60)
        print("VOTE SUMMARY")
        print("="*60)
        print(f"Congress: {self.vote_info.get('congress', 'Unknown')}")
        print(f"Session: {self.vote_info.get('session', 'Unknown')}")
        print(f"Vote Number: {self.vote_info.get('vote_number', 'Unknown')}")
        print(f"Date: {self.vote_info.get('vote_date', 'Unknown')}")
        print(f"Question: {self.vote_info.get('question', 'Unknown')}")
        print(f"Title: {self.vote_info.get('vote_title', 'Unknown')}")
        print("-"*60)
        
        # Count state results
        state_results = defaultdict(int)
        for state, votes in self.vote_data.items():
            result = self.determine_state_vote(votes)
            state_results[result] += 1
        
        print("State Results:")
        for result, count in sorted(state_results.items()):
            print(f"  {result}: {count} states")
        
        print("\nDetailed State Breakdown:")
        for state in sorted(self.vote_data.keys()):
            votes = self.vote_data[state]
            result = self.determine_state_vote(votes)
            vote_detail = ", ".join(votes) if len(votes) <= 2 else f"{len(votes)} votes"
            print(f"  {state}: {result} ({vote_detail})")

def main():
    """Main function to run the Senate Vote Visualizer"""
    visualizer = SenateVoteVisualizer()
    
    print("Senate Vote Visualizer")
    print("="*40)
    
    while True:
        try:
            print("\nEnter vote details:")
            congress = int(input("Congress number (e.g., 119): "))
            session = int(input("Session (1 or 2): "))
            roll_call = int(input("Roll call number (e.g., 160): "))
            
            print("\nFetching vote data...")
            if visualizer.fetch_vote_data(congress, session, roll_call):
                visualizer.print_vote_summary()
                
                show_map = input("\nShow map visualization? (y/n): ").lower().strip()
                if show_map.startswith('y'):
                    visualizer.create_map()
                
                another = input("\nAnalyze another vote? (y/n): ").lower().strip()
                if not another.startswith('y'):
                    break
            else:
                print("Failed to fetch vote data. Please check your inputs and try again.")
                retry = input("Try again? (y/n): ").lower().strip()
                if not retry.startswith('y'):
                    break
        
        except ValueError:
            print("Please enter valid numbers.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            retry = input("Try again? (y/n): ").lower().strip()
            if not retry.startswith('y'):
                break
    
    print("Thank you for using Senate Vote Visualizer!")

if __name__ == "__main__":
    main()