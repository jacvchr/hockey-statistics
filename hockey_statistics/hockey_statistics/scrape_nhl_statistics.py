import re
import urllib.request
from time import sleep
import json
import pandas as pd
from itertools import chain

#This method finds the urls for each NHL team/roster using regexes
def build_team_urls():
    #Open espn teams webpage and extract names of each roster
    f = urllib.request.urlopen('https://www.espn.com/nhl/teams')
    teams_source = f.read().decode('utf-8')
    teams = dict(re.findall("www\.espn\.com/nhl/team/_/name/(\w+)/(.+?)\",", teams_source))
    #Create urls of each roster
    roster_urls = []
    for key in teams.keys():
        roster_urls.append('https://www.espn.com/nhl/team/roster/_/name/' + key + '/' + teams[key])
        teams[key] = str(teams[key])
    return dict(zip(teams.values(), roster_urls))

#This method creates a dict of player info from a given roster url
def get_player_info(roster_url):
    f = urllib.request.urlopen(roster_url)
    roster_source = f.read().decode('utf-8')
    #sleep(0.5)
    #regex maybe broken?
    player_regex = ('\{\"roster\"\:\"(\w+\s\w+)\",\"href\"\:\"https?\://www\.espn\.com/nhl/teams.*?\",(.*?)\}')
    player_info = re.findall(player_regex, roster_source)
    player_dict = dict()
    for player in player_info:
        player_dict[player[0]] = json.loads("{" + player[1] + "}")
    return(player_dict)

#Scrape player info from rosters
rosters = build_team_urls()
all_players = dict()
for team in rosters.keys():
    print("Gathering player info for team: " + team)
    all_players[team] = get_player_info(rosters[team])

#Loop through each team, create a pandas DataFrame, and append
all_players_df = pd.DataFrame()
for team in all_players.keys():
    team_df = pd.DataFrame.from_dict(all_players[team], orient = "index")
    team_df['team'] = team
    all_players_df = pd.concat([all_players_df, team_df])
all_players_df.to_csv("NHL_roster_info_all_players.csv")

print(all_players["minnesota-wild"].keys())

#Scrape career statistics
print ("Now gathering career stats on all players (may take a while):")
career_stats_df = pd.DataFrame(columns = ["GP","G","A","PTS", "+/-","PIM","SOG","SPCT","PPG","PPA","SHG","SHA","GWG","GTG","TOI/G","PROD"])
for player_index in all_players_df.index:
    url = "https://www.espn.com/nhl/player/stats/_/id/" + str(all_players_df.loc[player_index]['id'])
    f = urllib.request.urlopen(url)
    sleep(0.3)
    player_source = f.read().decode('utf-8')
    #Extract career stats using this regex
    stats_regex = ('\[\"Career\",\"\",(.*?)\]\},\{\"ttl\"\:\"Regular Season Totals\"')
    career_info = re.findall(stats_regex, player_source)
    try:
        #Convert the stats to a list of floats, and add the entry to the DataFrame
        career_info = career_info[0].replace("\"", "").split(",")
        career_info = list(chain.from_iterable([i.split("-") for i in career_info]))
        career_info = list(map(float,career_info))
        career_stats_df = career_stats_df.append(pd.Series(career_info, index = career_stats_df.columns, name=player_index))
    except:
        #If no career stats were returned, the player was a rookie with no games played
        print(player_index + " has no info, ", end = "")
career_stats_df.to_csv("NHL_player_career_stats_all_players.csv")