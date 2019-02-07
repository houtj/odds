import locale
import time
import Downloader
import Database
import Page
import urllib
import traceback

if __name__ == '__main__':
    locale.setlocale(0, 'en_US.UTF-8')
    n = 0
    try:
        while True:
            if n % 15 == 0:
                print('Read the League_ids ...')
                league_id = Database.read_league_id('League_ids.xlsx')
                print('\tdone !!!')
            for league in league_id:
                if league.split('|')[0] not in ['World', 'North America', 'Portugal', 'Scotland', 'Brazil', 'Denmark',
                                        'Finland', 'Ireland', 'Netherlands', 'Poland', 'Russia', 'Turkey', 'Argentina']:
                    continue
                print('Begin processing matches in ' + league + ' ...')
                connecting_time = 0
                while True:
                    try:
                        connecting_time += 1
                        page = Downloader.odds_page(league_id[league])
                    except urllib.error.HTTPError as err:
                        if connecting_time < 10:
                            print(str('\t' + connecting_time) + 'th connection error ' + str(err.code) +
                                  '. Wait for 20s to retry ...')
                            time.sleep(20)
                        if connecting_time == 10:
                            Downloader.send_email('Odd_2 page download error!!!', traceback.format_exc())
                            raise
                    else:
                        connecting_time = 0
                        break
                odds_page = Page.OddsPage(page, league)
                odds_page.fetch_odds()
                Database.write_odds(odds_page.odds, 'odds.db')
                print('\tdone !!! Wait for 10 seconds to download the next league')
                time.sleep(10)
            print('Mission finished successfully !!!\nRestart the task in 4 hours ...')
            n += 1
            time.sleep(3600*4)
    except:
        Downloader.send_email('Odd_2 page download error!!!', traceback.format_exc())
        raise
