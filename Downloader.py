import urllib.parse
import urllib.request
import time
from selenium import webdriver


# Save bwin page as string
def odds_page(league_id):
    # Request header
    values = {
        'sportId':      '4',
        'leagueIds':    league_id,
        'page':         '0',
        'categoryIds':  '25,359'}
    headers = {
        'user-agent':   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'referer':      'https://sports.bwin.com/en/sports',
        'x-requested-with': 'XMLHttpRequest',
        'origin':       'https://sports.bwin.com',
        'connection':   'close'}
    # Constructing request
    data = urllib.parse.urlencode(values).encode('utf8')
    req = urllib.request.Request(r'https://sports.bwin.com/en/sports/indexmultileague', data, headers)
    response = urllib.request.urlopen(req)
    return response.read().decode('utf8')


# Save fixture page as string
def score_pages():
    # Request header
    headers = {
        'user-agent':   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    values = {
        'sport':    '4',
        'region':   '',
        'period':   'ThreeDays',
        'sort':     'Date'}
    # Constructing request
    req = urllib.request.Request(r'https://sports.bwin.com/en/sports/results?'
                                 'sport=4&region=&period=ThreeDays&sort=Date', headers=headers)
    response = urllib.request.urlopen(req)
    page = response.read().decode('utf8')
    if 'No results were found for the selected period.' in page:
        return []
    pages = [page]
    n = 1
    while True:
        url = r'https://sports.bwin.com/en/sports/results?sport=4&region=&period=ThreeDays&sort=Date&page=' + str(n)
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        page = response.read().decode('utf8')
        if 'No results were found for the selected period.' not in page:
            pages.append(page)
        else:
            break
        n += 1
        time.sleep(10)
    return pages


# Save leagues page as string
def leagues_page():
    headers = {'user-agent':    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    req = urllib.request.Request(r'https://sports.bwin.com/en/sports/navigation/index/4', headers=headers)
    response = urllib.request.urlopen(req)
    return response.read().decode('utf8')


# Save web page as string using selenium
def previews_page(url):
    driver = webdriver.Chrome()
    driver.get(url)
    page = driver.page_source
    driver.close()
    return page


if __name__ == '__main__':
    page = previews_page()
    with open('previews.html', 'w', encoding='utf8') as f:
        f.write(page)


