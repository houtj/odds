import Downloader
import Page
import Database
import time

while True:
    # Download league_id page
    page = Downloader.leagues_page()

    # Fetch league_id from downloaded page
    league_id = Page.LeagueIdPage(page)
    league_id.fetch_league_ids()
    Database.write_league_id(league_id.league_ids, 'League_ids.xlsx')
    print('Wait for 24 hours to update\n')
    time.sleep(3600*24)