# hockey-statistics

This web application is build using Django and allows the user to display hockey team and player statistics data scraped from ESPN.

`scrape_nhl_statistics.py` contains the methods that are used to scrape the team and player data from ESPN. The data is scraped and stored in nested dictionaries (Team>Player>Stat>Value).

Currently, only the data scraper is built and that data is being exported to cvs files using a `pandas` DataFrame. The frontend is being build, slowly but surely :D
