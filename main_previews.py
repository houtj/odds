import Downloader
import Database
from Page import PreviewPage as pp
import sqlite3
import time
from pyvirtualdisplay import Display
import locale
import traceback
from selenium.common.exceptions import TimeoutException


# download previews page, extract the urls for each match preview
# return match_urls [url, league_name]
def fetch_match_url():
    page = Downloader.previews_page('https://www.whoscored.com/Previews')
    match_urls = pp.fetch_preview_url(page)
    return match_urls


if __name__ == '__main__':
    # 每24小时
    # 下载previews页面，提取页面里的url
    # 检查数据库中是否已经含有这些url，如果有则不作为，如果没有则保存该url
    #
    # 每1小时
    # 顺序读取url，下载页面，提取信息，保存信息到数据库
    display = Display(visible=0, size=(1024, 768))
    display.start()
    locale.setlocale(0, 'en_US.UTF-8')

    try:
        while True:
            # get url
            print('Downloading preview page from whoscored.com ...')
            urls = fetch_match_url()
            print('\tdone !!!')
            time.sleep(10)
            db = sqlite3.connect('odds.db')
            c = db.cursor()
            for url in urls:
                # check if the url is in data base
                d = c.execute('SELECT * FROM previews WHERE url=?', (url[0],)).fetchall()
                if d:
                    print('Match preview found in database '+url[0])
                    continue
                # add data to the database
                else:
                    print('Downloading match preview information from ' + url[0])
                    connecting_time = 0
                    while True:
                        try:
                            connecting_time += 1
                            page = Downloader.previews_page('https://www.whoscored.com'+url[0])
                        except TimeoutError:
                            if connecting_time < 10:
                                print('\t' + str(connecting_time) + ' th connection error. Wait for 5 min to retry ...')
                                time.sleep(300)
                                continue
                            if connecting_time == 10:
                                Downloader.send_email('Preview page download error!!!', traceback.format_exc())
                                raise
                        else:
                            print('\tdone !!! Adding preview information to database ...')
                            break
                    match_statistics = pp.fetch_preview_info(url[1], page, url[0])
                    Database.write_preview_info(match_statistics, 'odds.db')
                    print('\tdone !!!')
                    print('Wait for 10 min to download the next match ...')
                    time.sleep(600)
            print('Daily mission finished successfully !!!\nRestart the task tomorrow ...')
            time.sleep(3600*23)
    except:
        Downloader.send_email('Preview page downloading error !!!', traceback.format_exc())
        raise



