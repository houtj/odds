from bs4 import BeautifulSoup
import re
from datetime import datetime


class OddsPage:

    def __init__(self, webpage, league_name):
        self.soup = BeautifulSoup(webpage, 'html5lib')
        self.league_name = league_name
        self.odds = []

    def parser_3ways_odds(self):
        odds_div = self.soup.find_all(name='div', class_='marketboard-event-group__item--sub-group')
        threeway_div = None
        for div in odds_div:
            if div.find(name='span', text=re.compile('.*(3Way).*')) is not None:
                threeway_div = div
                break
        if not threeway_div:
            return []
        threeway_div_matches = threeway_div.find(name='div',
                                                 attrs={'class': 'marketboard-event-group__item-container '
                                                                 'marketboard-event-group__item-container--level-2'})
        by_date_div = threeway_div_matches.find_all(name='div',
                                                    attrs={'class': 'marketboard-event-group__item--sub-group'})
        if not by_date_div:
            return []
        matches = []
        for div in by_date_div:
            date = div.find(name='h2').text.strip().split(' - ')[1]
            date = datetime.strptime(date, '%m/%d/%Y').strftime('%m/%d/%Y')
            matches_div = div.find_all(name='div', class_='marketboard-event-group__item--event')
            for m in matches_div:
                time = m.find(name='div', class_='marketboard-event-without-header__market-time').text.strip()
                info = m.find(name='table', class_='marketboard-event-without-header__markets-list')
                match_info = re.sub('\s\s+', '|', info.text.strip())
                m_split = match_info.split('|')
                match = {
                    'date':   date,
                    'time':   time,
                    'league':   self.league_name,
                    'home':   m_split[0],
                    'away':   m_split[4],
                    'home_odds':   m_split[1],
                    'draw_odds':   m_split[3],
                    'away_odds':   m_split[5]}
                matches.append(match)
        return matches

    def parser_2ways_odds(self):
        odds_div = self.soup.find_all(name='div', class_='marketboard-event-group__item--sub-group')
        twoway_div = None
        for div in odds_div:
            if div.find(name='span', text=re.compile('.*(2Way).*')) is not None:
                twoway_div = div
                break
        if not twoway_div:
            return []
        twoway_div_matches = twoway_div.find(name='div',
                                             attrs={'class':    'marketboard-event-group__item-container '
                                                                'marketboard-event-group__item-container--level-2'})
        by_date_div = twoway_div_matches.find_all(name='div',
                                                  attrs={'class':   'marketboard-event-group__item--sub-group'})
        if len(by_date_div) == 0:
            return []
        matches = []
        for div in by_date_div:
            date = div.find(name='h2').text.strip().split(' - ')[1]
            date = datetime.strptime(date, '%m/%d/%Y').strftime('%m/%d/%Y')
            matches_div = div.find_all(name='div', class_='marketboard-event-with-header')
            for m in matches_div:
                match_info = re.sub('\s\s+', '|', m.text.strip())
                m_split = match_info.split('|')
                match = {
                    'date':   date,
                    'home':   m_split[4],
                    'away':   m_split[6],
                    'time':   m_split[2],
                    'home_draw_odds':   m_split[5],
                    'away_draw_odds':   m_split[7]}
                matches.append(match)
        return matches

    def fetch_odds(self):
        matches_3way = self.parser_3ways_odds()
        matches_2way = self.parser_2ways_odds()
        for m_3way in matches_3way:
            for m_2way in matches_2way:
                if m_3way['home'] == m_2way['home'] and m_3way['away'] == m_2way['away'] and \
                        m_3way['time'] == m_2way['time'] and m_3way['date'] == m_2way['date']:
                    m_3way['home_draw_odds'] = m_2way['home_draw_odds']
                    m_3way['away_draw_odds'] = m_2way['away_draw_odds']
            if 'home_draw_odds' not in m_3way:
                m_3way['home_draw_odds'] = '0'
            if 'away_draw_odds' not in m_3way:
                m_3way['away_draw_odds'] = '0'
        self.odds = matches_3way


class ScorePage:

    def __init__(self, webpage):
        self.soup = BeautifulSoup(webpage, 'html5lib')
        self.scores = []

    def fetch_scores(self):
        match_scores = []
        dates = self.soup.find_all(name='div', class_='result-group date')
        for date in dates:
            date_title_h3 = date.find(name='h3', class_='section__title')
            if date_title_h3 is None:
                return
            date_title = date_title_h3.text.strip()
            leagues = date.find_all(name='table', class_='transaction-table league')
            for league in leagues:
                league_name = league.find(name='thead').text.strip().replace('Result', '')
                matches = league.find(name='tbody').find_all(name='tr')
                for match in matches:
                    match_strings = list(match.stripped_strings)
                    if len(match_strings) < 3:
                        continue
                    if re.match('^\d+\:\d+ \(\d+\:\d+\)$', match_strings[2]) is None or \
                            re.match('^.+ - .+$', match_strings[1]) is None:
                        continue
                    league_name_format = league_name.split(', ')
                    if len(league_name_format) == 2:
                        league_name = league_name_format[1] + '|' + league_name_format[0]
                    d = datetime.strptime(date_title, '%A, %B %d, %Y').strftime('%m/%d/%Y')
                    match = {
                        'date': d,
                        'league':   league_name,
                        'time': match_strings[0],
                        'home': match_strings[1].split(' - ')[0],
                        'away': match_strings[1].split(' - ')[1],
                        'home_score':   match_strings[2].split(' ')[0].split(':')[0],
                        'away_score':   match_strings[2].split(' ')[0].split(':')[1],
                        'home_score_half':  match_strings[2].split(' ')[1].split(':')[0].replace('(', ''),
                        'away_score_half':  match_strings[2].split(' ')[1].split(':')[1].replace(')', '')}
                    match_scores.append(match)
        self.scores = match_scores


class LeagueIdPage:

    def __init__(self, webpage):
        self.soup = BeautifulSoup(webpage, 'html5lib')
        self.league_ids = []

    def fetch_league_ids(self):
        league_ids = {}
        countries = self.soup.find_all(name='li', class_='nav-toggle sports-links__item')
        for country in countries:
            country_name = country.find(name='span', attrs={'class': 'nav-region-name sports-links__text'}).text
            leagues = country.find_all(name='span', class_='sports-links__text')
            for league in leagues:
                if len(league['class']) > 1:
                    continue
                league_name = league.text
                league_id = str(league.parent.parent['id']).replace('nav-league-', '')
                league_ids[country_name + '|' + league_name] = league_id
        self.league_ids = league_ids


class PreviewPage:

    # 从preview页面提取所有比赛的网页地址
    # 输入：preview网页
    # 输入：二维数组 [网址，联赛名]
    @staticmethod
    def fetch_preview_url(page):
        soup = BeautifulSoup(page, 'html5lib')
        divs = soup.find_all(name='div', class_='region previews')
        if len(divs) != 0:
            div = divs[0]
        else:
            return []
        locations = div.find_all(name='td', attrs={'colspan': '99'})
        matches_url = []
        for l in locations:
            if l.a:
                if 'class' in l.a:
                    continue
                matches_url.append([l.a['href'], l.a.text.strip()])
        matches_league = []
        for m in matches_url:
            if 'Region' in m[0]:
                league = m[1]
            else:
                matches_league.append([m[0], league])
        return matches_league

    @staticmethod
    def chunks(arr, n):
        return [arr[i:i + n] for i in range(0, len(arr), n)]

    @staticmethod
    # 从比赛的预测网页提取预测信息
    # 输入：联赛名，网页，网页地址
    # 输出：17维字典，包含所有预测信息
    def fetch_preview_info(league, page, url):
        soup = BeautifulSoup(page, 'html5lib')
        # definition items
        date = time = 'NA'
        team_home = []
        team_away = []
        goals_home_1 = goals_away_1 = goals_home_2 = goals_away_2 = 'NA'
        assists_home_1 = assists_home_2 = assists_away_1 = assists_away_2 = 'NA'
        rating_home_1 = rating_home_2 = rating_away_1 = rating_away_2 = 'NA'
        shots_home_1 = shots_home_2 = shots_away_1 = shots_away_2 = 'NA'
        aerial_home_1 = aerial_home_2 = aerial_away_1 = aerial_away_2 = 'NA'
        dribbles_home_1 = dribbles_home_2 = dribbles_away_1 = dribbles_away_2 = 'NA'
        tackles_home_1 = tackles_home_2 = tackles_away_1 = tackles_away_2 = 'NA'
        age_home = age_away = 'NA'
        height_home = height_away = 'NA'
        formation_home = formation_away = 'NA'
        players_home = []
        players_away = []
        mis_players_home = []
        mis_players_away = []
        news_home = []
        news_away = []
        predictions = []
        predictions_score_home = predictions_score_away = 'NA'
        ## time and date
        headers_str = list(soup.find(name='div', attrs={'id': 'match-header', 'class': 'match-header'})
                           .stripped_strings)
        if headers_str:
            time = headers_str[headers_str.index('Kick off:') + 1]
            date = headers_str[headers_str.index('Date:') + 1]
        # team
        teams_a = soup.find_all(name='a', class_=re.compile('team-link.*'))
        if len(teams_a) >= 2:
            team_home = (teams_a[0].string.strip(), teams_a[0]['href'])
            team_away = (teams_a[1].string.strip(), teams_a[1]['href'])
        # team stats
        team_stats_div = soup.find_all(name='div', class_='stat-group')
        for stats in team_stats_div:
            for stat_item_div in stats.find_all(name='div', class_='stat'):
                stat_item = list(stat_item_div.stripped_strings)
                if len(stat_item) == 5:
                    if 'Goals' in stat_item:
                        goals_home_1 = stat_item[1]
                        goals_home_2 = stat_item[0].lstrip('(').rstrip(')')
                        goals_away_1 = stat_item[3]
                        goals_away_2 = stat_item[4].lstrip('(').rstrip(')')
                    if 'Assists' in stat_item:
                        assists_home_1 = stat_item[1]
                        assists_home_2 = stat_item[0].lstrip('(').rstrip(')')
                        assists_away_1 = stat_item[3]
                        assists_away_2 = stat_item[4].lstrip('(').rstrip(')')
                    if 'Average Ratings' in stat_item:
                        rating_home_1 = stat_item[1]
                        rating_home_2 = stat_item[0].lstrip('(').rstrip(')')
                        rating_away_1 = stat_item[3]
                        rating_away_2 = stat_item[4].lstrip('(').rstrip(')')
                    if 'Shots pg' in stat_item:
                        shots_home_1 = stat_item[1]
                        shots_home_2 = stat_item[0].lstrip('(').rstrip(')')
                        shots_away_1 = stat_item[3]
                        shots_away_2 = stat_item[4].lstrip('(').rstrip(')')
                    if 'Aerial Duel Success' in stat_item:
                        aerial_home_1 = stat_item[1].rstrip('%')
                        aerial_home_2 = stat_item[0].lstrip('(').rstrip(')').rstrip('%')
                        aerial_away_1 = stat_item[3].rstrip('%')
                        aerial_away_2 = stat_item[4].lstrip('(').rstrip(')').rstrip('%')
                    if 'Dribbles pg' in stat_item:
                        dribbles_home_1 = stat_item[1]
                        dribbles_home_2 = stat_item[0].lstrip('(').rstrip(')')
                        dribbles_away_1 = stat_item[3]
                        dribbles_away_2 = stat_item[4].lstrip('(').rstrip(')')
                    if 'Tackles pg' in stat_item:
                        tackles_home_1 = stat_item[1]
                        tackles_home_2 = stat_item[0].lstrip('(').rstrip(')')
                        tackles_away_1 = stat_item[3]
                        tackles_away_2 = stat_item[4].lstrip('(').rstrip(')')
                if len(stat_item) == 3:
                    if 'Average Age' in stat_item:
                        age_home = stat_item[0]
                        age_away = stat_item[2]
                    if 'Average Height (cm)' in stat_item:
                        height_home = stat_item[0]
                        height_away = stat_item[2]
        # formation
        formation_divs = soup.find_all(name='span', class_='formation-label')
        if len(formation_divs) == 2:
            formation_home = formation_divs[0].text
            formation_away = formation_divs[1].text
        # player stats
        player_div = soup.find(name='div', class_='pitch')
        players_home_div = player_div.find(name='div', class_='home')
        players_away_div = player_div.find(name='div', class_='away')
        players_home_wrapper = players_home_div.find_all(name='ul', class_='player')
        players_home = []
        for player_wrapper in players_home_wrapper:
            players_home.append(player_wrapper.find(name='a').string.strip())
            player_rating_wrapper = player_wrapper.find(name='li', class_=re.compile('player-rating rc.*'))
            if not player_rating_wrapper:
                players_home.append('NA')
            else:
                players_home.append(list(player_rating_wrapper.stripped_strings)[0])
            players_home_list = PreviewPage.chunks(players_home, 2)
        player_url_list = []
        for player_a in players_home_div.find_all(name='a'):
            player_url_list.append(player_a['href'])
        n_defender = int(formation_home.split('-')[0])
        n_attacker = int(formation_home.split('-')[-1])
        players_home = []
        for n, player in enumerate(players_home_list):
            player_dic = {'name': player[0], 'rating': player[1], 'url': player_url_list[n]}
            if n == 0:
                player_dic['position'] = 'goalkeeper'
            elif n_defender >= n >= 1:
                player_dic['position'] = 'defender'
            elif n >= 11 - n_attacker:
                player_dic['position'] = 'attacker'
            else:
                player_dic['position'] = 'midfielder'
            players_home.append(player_dic)
        players_away_wrapper = players_away_div.find_all(name='ul', class_='player')
        players_away = []
        for player_wrapper in players_away_wrapper:
            players_away.append(player_wrapper.find(name='a').string.strip())
            player_rating_wrapper = player_wrapper.find(name='li', class_=re.compile('player-rating rc.*'))
            if not player_rating_wrapper:
                players_away.append('NA')
            else:
                players_away.append(list(player_rating_wrapper.stripped_strings)[0])
            players_away_list = PreviewPage.chunks(players_away, 2)
        player_url_list = []
        for player_a in players_away_div.find_all(name='a'):
            player_url_list.append(player_a['href'])
        n_defender = int(formation_away.split('-')[0])
        n_attacker = int(formation_away.split('-')[-1])
        players_away = []
        for n, player in enumerate(players_away_list):
            player_dic = {'name': player[0], 'rating': player[1], 'url': player_url_list[n]}
            if n == 0:
                player_dic['position'] = 'goalkeeper'
            elif n_defender >= n >= 1:
                player_dic['position'] = 'defender'
            elif n >= 11 - n_attacker:
                player_dic['position'] = 'attacker'
            else:
                player_dic['position'] = 'midfielder'
            players_away.append(player_dic)
        # missing players
        mis_players_wrapper = soup.find(name='div', attrs={'id': 'missing-players', 'class': 'two-cols'})
        if mis_players_wrapper:
            mis_players_div = mis_players_wrapper.find_all(name='tbody')
            if len(mis_players_div) >= 2:
                players_url = []
                for player_a in mis_players_div[0].find_all(name='a'):
                    players_url.append(player_a['href'])
                for n, player_tr in enumerate(mis_players_div[0].find_all(name='tr')):
                    player_list = list(player_tr.stripped_strings)
                    if len(player_list) == 3:
                        player_dic = {'name': player_list[0], 'rating': player_list[2], 'url': players_url[n],
                                      'position': 'missing'}
                        mis_players_home.append(player_dic)
                players_url = []
                for player_a in mis_players_div[1].find_all(name='a'):
                    players_url.append(player_a['href'])
                for n, player_tr in enumerate(mis_players_div[1].find_all(name='tr')):
                    player_list = list(player_tr.stripped_strings)
                    if len(player_list) == 3:
                        player_dic = {'name': player_list[0], 'rating': player_list[2], 'url': players_url[n],
                                      'position': 'missing'}
                        mis_players_away.append(player_dic)
        else:
            mis_players_home = []
            mis_players_away = []
        # news
        news_div = soup.find(name='div', attrs={'id': 'preview-team-news', 'class': 'two-cols'})
        news_ul = news_div.find_all(name='ul', class_='items')
        if len(news_ul) == 2:
            news_home = list(news_ul[0].stripped_strings)
            news_away = list(news_ul[1].stripped_strings)
        # preview
        predictions = list(soup.find(name='div', class_='intensity').stripped_strings)
        predicted_score_span = soup.find_all(name='span', class_='predicted-score')
        if len(predicted_score_span) >= 2:
            predictions_score_home = predicted_score_span[0].text.strip()
            predictions_score_away = predicted_score_span[1].text.strip()
        # summary information
        info = {
            'url': url,
            'date': date,
            'time': time,
            'league': league,
            'team_home': team_home,
            'team_away': team_away,
            'stat_home': {'goals_1': goals_home_1,
                          'goals_2': goals_home_2,
                          'assists_1': assists_home_1,
                          'assists_2': assists_home_2,
                          'rating_1': rating_home_1,
                          'rating_2': rating_home_2,
                          'age': age_home,
                          'height': height_home,
                          'shots_1': shots_home_1,
                          'shots_2': shots_home_2,
                          'aerial_1': aerial_home_1,
                          'aerial_2': aerial_home_2,
                          'dribbles_1': dribbles_home_1,
                          'dribbles_2': dribbles_home_2,
                          'tackles_1': tackles_home_1,
                          'tackles_2': tackles_home_2},
            'stat_away': {'goals_1': goals_away_1,
                          'goals_2': goals_away_2,
                          'assists_1': assists_away_1,
                          'assists_2': assists_away_2,
                          'rating_1': rating_away_1,
                          'rating_2': rating_away_2,
                          'age': age_away,
                          'height': height_away,
                          'shots_1': shots_away_1,
                          'shots_2': shots_away_2,
                          'aerial_1': aerial_away_1,
                          'aerial_2': aerial_away_2,
                          'dribbles_1': dribbles_away_1,
                          'dribbles_2': dribbles_away_2,
                          'tackles_1': tackles_away_1,
                          'tackles_2': tackles_away_2},
            'players_home': list(players_home),
            'players_away': list(players_away),
            'missing_players_home': list(mis_players_home),
            'missing_players_away': list(mis_players_away),
            'news_home': list(news_home),
            'news_away': list(news_away),
            'predictions': list(predictions),
            'predicted_score_home': predictions_score_home,
            'predicted_score_away': predictions_score_away
        }
        return info


if __name__ == '__main__':
    with open('previews.html', 'r') as f:
        a = f.read()
    matches = PreviewPage.fetch_preview_url(a)
    print(len(matches))



