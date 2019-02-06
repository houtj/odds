import locale
import time
import Downloader
import Database
import Page
import urllib

locale.setlocale(0, 'en_US.UTF-8')
n = 0
while True:
    if n % 5 == 0:
        league_id = Database.read_league_id('League_ids.xlsx')
    for league in league_id:
        if league.split('|')[0] in ['Europe', 'England', 'Spain', 'Germany', 'Italy', 'France']:
            continue
        if league.split('|')[0] in ['World', 'North America', 'Portugal', 'Scotland', 'Brazil', 'Denmark',
                                    'Finland', 'Ireland', 'Netherlands', 'Poland', 'Russia', 'Turkey', 'Argentina']:
            continue
        print('Begin processing matches in '+league)
        try:
            page = Downloader.odds_page(league_id[league])
        except urllib.error.HTTPError as err:
            print('Connection error ' + str(err.code) + '. Wait for 20s to reload')
            time.sleep(20)
            continue
        odds_page = Page.OddsPage(page, league)
        odds_page.fetch_odds()
        Database.write_odds(odds_page.odds, 'odds.db')
        time.sleep(10)
    print('Wait 10 hour for update database')
    n += 1
    time.sleep(3600*10)
