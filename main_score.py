import Downloader
import Page
import Database
import time

Database.create_db('odds.db')
while True:
    pages = Downloader.score_pages()
    for n_page, page in enumerate(pages):
        score_page = Page.ScorePage(page)
        score_page.fetch_scores()
        Database.write_score(score_page.scores, 'odds.db')
        Database.add_score(score_page.scores, 'odds.db')
        print('Page '+str(n_page)+' is successfully processed')
    print("Today's match scores are added to the database")
    time.sleep(30*3600)



