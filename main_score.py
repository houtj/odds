import Downloader
import Page
import Database
import time
import traceback

if __name__ == '__main__':
    try:
        while True:
            print('Downloading score pages ...')
            pages = Downloader.score_pages()
            print('\tdone !!!\nProcessing ' + len(pages) + ' score pages ...')
            for n_page, page in enumerate(pages):
                score_page = Page.ScorePage(page)
                score_page.fetch_scores()
                Database.write_score(score_page.scores, 'odds.db')
                Database.add_score(score_page.scores, 'odds.db')
                print('\tPage '+str(n_page)+' is successfully processed !!!')
            print("Mission finished successfully !!!\nRestart the task in 30 hours ...")
            time.sleep(30*3600)
    except:
        Downloader.send_email('Score page download error!!!', traceback.format_exc())
        raise



