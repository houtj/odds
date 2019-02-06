from datetime import datetime
import sqlite3
import xlsxwriter
import xlrd


def create_db(db_path):
    db = sqlite3.connect(db_path)
    c = db.cursor()
    # odds
    try:
        c.execute('CREATE TABLE matches (date, time, league, home, away, '
                  'odds_time, home_odds, draw_odds, away_odds, home_draw_odds, away_draw_odds, flag, '
                  'home_score, away_score, home_score_half, away_score_half)')
        print('Table "matches" created')
    except:
        print('Table "matches" already exists.')
    # scores
    try:
        c.execute('CREATE TABLE scores (date, time, league, home, away, '
                  'home_score, away_score, home_score_half, away_score_half)')
        print('Table "scores" created')
    except:
        print('Table "scores" already exists')
    # previews
    # independent tables: players, previews
    try:
        c.execute('CREATE TABLE players (name, url_whoscored)')
        print('Table "players" created')
    except:
        print('Table "players" already exists')
    try:
        c.execute('CREATE TABLE previews (url, date, time, league, home, away, home_url, away_url, '
                  'home_goals_1, away_goals_1, home_goals_2, away_goals_2, '
                  'home_assists_1, away_assists_1, home_assists_2, away_assists_2, '
                  'home_rating_1, away_rating_1, home_rating_2, away_rating_2, '
                  'home_shots_1, away_shots_1, home_shots_2, away_shots_2, '
                  'home_aerial_1, away_aerial_1, home_aerial_2, away_aerial_2, '
                  'home_dribbles_1, away_dribbles_1, home_dribbles_2, away_dribbles_2, '
                  'home_tackles_1, away_tackles_1, home_tackles_2, away_tackles_2, '
                  'home_age, away_age, home_height, away_height, '
                  'home_predicted_scores, away_predicted_scores)')
        print('Table "previews" created')
    except:
        print('Table "previews" already exists')
    # dependent tables:  players_predicted, predictions
    try:
        c.execute('CREATE TABLE players_predicted (match, team, player, rating, position)')
        print('Table "players_predicted" created')
    except:
        print('Table "players_predicted" already exists')
    try:
        c.execute('CREATE TABLE predictions (match, team, news)')
        print('Table "predictions" created')
    except:
        print('Table "predictions" already exists')
    db.commit()
    db.close()


def write_odds(matches, db_path):
    time_now = str(datetime.now().strftime('%m/%d/%Y %H:%M'))
    db = sqlite3.connect(db_path)
    c = db.cursor()
    print(str(len(matches))+' matches odds are downloaded')
    n_added = 0
    n_updated = 0
    for match in matches:
        d = c.execute('SELECT rowid FROM matches WHERE date=? AND home=? AND away=?',
                      (match['date'], match['home'], match['away'])).fetchall()
        if len(d) == 0:
            c.execute('INSERT INTO matches '
                      '(date, time, league, home, away, odds_time, home_odds, draw_odds, away_odds, '
                      'home_draw_odds, away_draw_odds, flag) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                      (match['date'], match['time'], match['league'], match['home'],
                       match['away'], time_now, match['home_odds'], match['draw_odds'], match['away_odds'],
                       match['home_draw_odds'], match['away_draw_odds'], '1'))
            n_added += 1
        if len(d) > 0:
            m = c.execute('SELECT home_odds, draw_odds, away_odds, home_draw_odds, away_draw_odds FROM matches '
                          'WHERE date=? AND home=? AND away=? AND flag="1"',
                          (match['date'], match['home'], match['away'])).fetchall()
            if match['home_odds'] == m[0][0] and match['draw_odds'] == m[0][1] and match['away_odds'] == m[0][2] and \
                    match['home_draw_odds'] == m[0][3] and match['away_draw_odds'] == m[0][4]:
                pass
            else:
                c.execute('UPDATE matches SET flag="0" WHERE date=? AND home=? AND away=? AND flag="1"',
                          (match['date'], match['home'], match['away']))
                c.execute('INSERT INTO matches '
                          '(date, time, league, home, away, odds_time, home_odds, draw_odds, away_odds, '
                          'home_draw_odds, away_draw_odds, flag) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                          (match['date'], match['time'], match['league'], match['home'], match['away'], time_now,
                           match['home_odds'], match['draw_odds'], match['away_odds'],
                           match['home_draw_odds'], match['away_draw_odds'], '1'))
                n_updated += 1
    print(str(n_added)+' piece of information are added')
    print(str(n_updated)+' piece of information are updated\n')
    db.commit()
    db.close()


def add_score(scores, db_path):
    db = sqlite3.connect(db_path)
    c = db.cursor()
    n_added = 0
    for score in scores:
        d = c.execute('SELECT rowid FROM matches WHERE date=? AND time=? AND league=? AND '
                      'home=? AND away=? AND flag="1"',
                      (score['date'], score['time'], score['league'], score['home'], score['away'])).fetchall()
        if d:
            c.execute('UPDATE matches SET home_score=?, away_score=?, home_score_half=?, away_score_half=? '
                      'WHERE date=? AND time=? AND league=? AND home=? AND away=? AND flag="1"',
                      (score['home_score'], score['away_score'], score['home_score_half'], score['away_score_half'],
                       score['date'], score['time'], score['league'], score['home'], score['away']))
            n_added += 1
    if n_added != 0:
        print(str(n_added)+' piece of score information are added')
    db.commit()
    db.close()


def write_score(scores, db_path):
    db = sqlite3.connect(db_path)
    c = db.cursor()
    for score in scores:
        d = c.execute('SELECT rowid FROM scores WHERE date=? AND time=? AND league=? AND '
                      'home=? AND away=?',
                      (score['date'], score['time'], score['league'], score['home'], score['away'])).fetchall()
        if not d:
            c.execute('INSERT INTO scores '
                      '(date, time, league, home, away, home_score, away_score, home_score_half, away_score_half) ' 
                      'VALUES (?,?,?,?,?,?,?,?,?)',
                      (score['date'], score['time'], score['league'], score['home'], score['away'],
                       score['home_score'], score['away_score'], score['home_score_half'], score['away_score_half']))
    db.commit()
    db.close()


def write_league_id(league_id, excel_path):
    w = xlsxwriter.Workbook(excel_path)
    ws = w.add_worksheet('Leagues')
    row = 0
    for league in league_id:
        ws.write(row, 0, league)
        ws.write(row, 1, league_id[league])
        row += 1


def read_league_id(excel_path):
    data = xlrd.open_workbook(excel_path)
    league_id = {}
    table = data.sheet_by_name('Leagues')
    for i in range(table.nrows):
        league_id[table.row_values(i)[0]] = table.row_values(i)[1]
    return league_id


def write_players(players, c):
    for p in players:
        d = c.execute('SELECT rowid FROM players WHERE url_whoscored=?', (p['url'],)).fetchone()
        if not d:
            c.execute('INSERT INTO players (name, url_whoscored) VALUES (?,?)', (p['name'], p['url']))


def write_players_predicted(players, team, info, c):
    for p in players:
        d_players = c.execute('SELECT rowid FROM players WHERE url_whoscored=?', (p['url'],)).fetchone()[0]
        d_previews = c.execute('SELECT rowid FROM previews WHERE date=? AND time=? AND home=? AND away=?',
                               (info['date'], info['time'], info['team_home'][0], info['team_away'][0])).fetchone()[0]
        c.execute('INSERT INTO players_predicted (match, team, player, rating, position) VALUES (?,?,?,?,?)',
                  (d_previews, team, d_players, p['rating'], p['position']))


def write_predictions(news, team, info, c):
    for n in news:
        d_previews = c.execute('SELECT rowid FROM previews WHERE date=? AND time=? AND home=? AND away=?',
                               (info['date'], info['time'], info['team_home'][0], info['team_away'][0])).fetchone()[0]
        c.execute('INSERT INTO predictions (match, team, news) VALUES (?,?,?)',
                  (d_previews, team, n))


def write_preview_info(info, db_path):
    db = sqlite3.connect(db_path)
    c = db.cursor()
    print(info)
    d = c.execute('SELECT rowid FROM previews WHERE date=? AND time=? AND home=? AND away=?',
                  (info['date'], info['time'], info['team_home'][0], info['team_away'][0])).fetchall()

    if not d:
        # write preview information
        c.execute('INSERT INTO previews (url, date, time, league, home, away, home_url, away_url, '
                  'home_goals_1, away_goals_1, home_goals_2, away_goals_2, '
                  'home_assists_1, away_assists_1, home_assists_2, away_assists_2, '
                  'home_rating_1, away_rating_1, home_rating_2, away_rating_2, '
                  'home_shots_1, away_shots_1, home_shots_2, away_shots_2, '
                  'home_aerial_1, away_aerial_1, home_aerial_2, away_aerial_2, '
                  'home_dribbles_1, away_dribbles_1, home_dribbles_2, away_dribbles_2, '
                  'home_tackles_1, away_tackles_1, home_tackles_2, away_tackles_2, '
                  'home_age, away_age, home_height, away_height, '
                  'home_predicted_scores, away_predicted_scores) '
                  'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (info['url'], info['date'], info['time'], info['league'], info['team_home'][0], info['team_away'][0],
                      info['team_home'][1], info['team_away'][1],
                      info['stat_home']['goals_1'], info['stat_away']['goals_1'],
                      info['stat_home']['goals_2'], info['stat_away']['goals_2'],
                      info['stat_home']['assists_1'], info['stat_away']['assists_1'],
                      info['stat_home']['assists_2'], info['stat_away']['assists_2'],
                      info['stat_home']['rating_1'], info['stat_away']['rating_1'],
                      info['stat_home']['rating_2'], info['stat_away']['rating_2'],
                      info['stat_home']['shots_1'], info['stat_away']['shots_1'],
                      info['stat_home']['shots_2'], info['stat_away']['shots_2'],
                      info['stat_home']['aerial_1'], info['stat_away']['aerial_1'],
                      info['stat_home']['aerial_2'], info['stat_away']['aerial_2'],
                      info['stat_home']['dribbles_1'], info['stat_away']['dribbles_1'],
                      info['stat_home']['dribbles_2'], info['stat_away']['dribbles_2'],
                      info['stat_home']['tackles_1'], info['stat_away']['tackles_1'],
                      info['stat_home']['tackles_2'], info['stat_away']['tackles_2'],
                      info['stat_home']['age'], info['stat_away']['age'],
                      info['stat_home']['height'], info['stat_away']['height'],
                      info['predicted_score_home'], info['predicted_score_away']))
        # write players
        write_players(info['players_home'], c)
        write_players(info['players_away'], c)
        write_players(info['missing_players_home'], c)
        write_players(info['missing_players_away'], c)
        # write match_players
        write_players_predicted(info['players_home'], 'home', info, c)
        write_players_predicted(info['players_away'], 'away', info, c)
        write_players_predicted(info['missing_players_home'], 'home', info, c)
        write_players_predicted(info['missing_players_away'], 'away', info, c)
        # write predictions
        write_predictions(info['news_home'], 'home', info, c)
        write_predictions(info['news_away'], 'away', info, c)
        write_predictions(info['predictions'], 'predictions', info, c)
    db.commit()
    db.close()
