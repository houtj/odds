import Downloader
import Database
from Page import PreviewPage as pp
import sqlite3
import time
from pyvirtualdisplay import Display
import locale


# download previews page, extract the urls for each match preview
# return match_urls [url, league_name]
def fetch_match_url():
    page = Downloader.previews_page('https://www.whoscored.com/Previews')
    match_urls = pp.fetch_preview_url(page)
    return match_urls


# 每24小时
# 下载previews页面，提取页面里的url
# 检查数据库中是否已经含有这些url，如果有则不作为，如果没有则保存该url
#
# 每1小时
# 顺序读取url，下载页面，提取信息，保存信息到数据库
Database.create_db('odds.db')
display = Display(visible=0, size=(1024, 768))
display.start()
locale.setlocale(0, 'en_US.UTF-8')

while True:
    # get url
    urls = fetch_match_url()
    time.sleep(10)
    # check if the url is in data base, return the urls that are not in data base
    db = sqlite3.connect('odds.db')
    for url in urls:
        c = db.cursor()
        d = c.execute('SELECT * FROM previews WHERE url=?', (url[0],)).fetchall()
        if d:
            print('already in the database ' + url[0])
            continue
        else:
            page = Downloader.previews_page('https://www.whoscored.com'+url[0])
            match_statistics = pp.fetch_preview_info(url[1], page, url[0])
            Database.write_preview_info(match_statistics, 'odds.db')
            print('database added ' + url[0])
            time.sleep(600)
    time.sleep(3600*23)


