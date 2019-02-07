import Downloader
import Page
import Database
import time
import traceback

if __name__ == '__main__':
    try:
        while True:
            # Download league_id page
            print('Downloading league pages ...')
            page = Downloader.leagues_page()
            print('\tdone !!!')

            # Fetch league_id from downloaded page
            print('Processing league pages ...')
            league_id = Page.LeagueIdPage(page)
            league_id.fetch_league_ids()
            Database.write_league_id(league_id.league_ids, 'League_ids.xlsx')
            print('\tdone !!!')
            print("Mission finished successfully !!!\nRestart the task in 24 hours ...")
            time.sleep(3600*24)
    except:
        Downloader.send_email('League page download error!!!', traceback.format_exc())
        raise
