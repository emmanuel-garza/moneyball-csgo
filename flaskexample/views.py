from flask import render_template, request, redirect
from flaskexample import app

import numpy as np
import pandas as pd
import json

import pickle
import csgo 
from sklearn.linear_model import LogisticRegression

# from bokeh.plotting import figure, show, output_file

# For the selection of the Team
@app.route('/') 
@app.route('/index')
def index():

    # Open the team dictionary
    filename = 'webapp_dict_team.sav'
    df_team  = pickle.load(open(filename, 'rb'))

    team_names = df_team['team_name'].values[:]
    team_ids    = df_team.index.values
    n           = len(team_names)

    return render_template("index.html", title = 'CSGO Moneyball', team_names=team_names,team_ids=team_ids,n=n)


# For the selection of the player
@app.route('/choose_player', methods=['GET','POST'])
def choose_player():

    if request.method == 'GET':
        team_id = request.args.get('team', '')
        #team = get_team(team_id)
        #players = get_players(team_id)

    # Open the team df
    filename = 'webapp_dict_team.sav'
    df_team  = pickle.load(open(filename, 'rb'))

    tmp = df_team.loc[int(team_id)]
    team_name = tmp.team_name
 
    player_name_vec = [ 
        tmp.player_name_1, tmp.player_name_2, tmp.player_name_3, tmp.player_name_4, tmp.player_name_5
    ]

    player_id_vec = [ 
        tmp.player_id_1, tmp.player_id_2, tmp.player_id_3, tmp.player_id_4, tmp.player_id_5
    ]

    # Replacement options
    filename = 'webapp_dict_player.sav'
    df_player  = pickle.load(open(filename, 'rb'))

    player_rep_id_vec   = df_player.index.values
    player_rep_name_vec = df_player['name'].values

    prize_stars = df_player['prize_stars'].values
    prize_rating = df_player['prize_rating'].values

    rating_stars = df_player['rating_stars'].values
    rating = df_player['rating'].values

    win_stars = df_player['win_stars'].values
    win_rate = df_player['win_rate'].values

    n_rep = len(player_rep_id_vec)

    return render_template("choose_player.html", title = 'CSGO Moneyball', team_name=team_name, team_id=team_id, 
        player_name_vec=player_name_vec, player_id_vec=player_id_vec,
        player_rep_id_vec=player_rep_id_vec, player_rep_name_vec=player_rep_name_vec, n_rep=n_rep,
        prize_stars=prize_stars,
        rating_stars=rating_stars,
        win_stars=win_stars,
        prize_rating=["%.2f" % number for number in prize_rating],
        rating=["%.2f" % number for number in rating],
        win_rate=["%.2f" % number for number in win_rate] )



# Suggest players
@app.route('/suggest', methods=['GET','POST'])
def suggest():
    if request.method == 'GET':
        
        team_id = str(request.args.get('team', ''))
        player_id = str(request.args.get('player', ''))
        rep_id = str(request.args.get('ideal_id', ''))

        # Open the team df
        filename = 'webapp_dict_team.sav'
        df_team  = pickle.load(open(filename, 'rb'))

        # Open the player df
        filename = 'webapp_dict_player.sav'
        df_player  = pickle.load(open(filename, 'rb'))

        team_name = df_team.loc[int(team_id)]['team_name']

        player_name = df_player.loc[int(player_id)]['name']
        rep_name    = df_player.loc[int(rep_id)]['name']

        # Do the similarity test
        filename = 'webapp_dict_similarity.sav'
        df_similarity = pickle.load(open(filename, 'rb'))

        df_dist = df_similarity
        df_dist['dist'] = df_similarity['rating']*0.0

        column_vec = ['prize', 'rating', 'hs_perc', 'kills_per_round','deaths_per_round', 'ADR']
        for column in column_vec:
            df_dist[column] = (df_similarity[column]-df_similarity.loc[int(rep_id)][column])**2
            df_dist['dist'] = df_dist['dist'] + df_dist[column]


        df_dist = df_dist.sort_values('dist',ascending=True)

        n_sug = 10
        suggested_name_vec = df_dist['name'].values[0:n_sug]
        suggested_id_vec = df_dist.index.values[0:n_sug]

        prize_rating = df_dist['prize'].values[0:n_sug]
        rating = df_dist['rating'].values[0:n_sug]
        hs = df_dist['hs_perc'].values[0:n_sug] 
        kills_per_round = df_dist['kills_per_round'].values[0:n_sug]
        deaths_per_round = df_dist['deaths_per_round'].values[0:n_sug]
        adr  = df_dist['ADR'].values[0:n_sug]

        n_sug = len(suggested_id_vec)


    return render_template('suggest.html',title='Results',team_id=team_id,player_id=player_id,team_name=team_name,player_name=player_name,rep_name=rep_name,
        suggested_name_vec=suggested_name_vec,suggested_id_vec=suggested_id_vec,n_sug=n_sug,
        prize_rating=["%.2f" % number for number in prize_rating],
        rating=["%.2f" % number for number in rating],
        hs=["%.2f" % number for number in hs],
        kills_per_round=["%.2f" % number for number in kills_per_round],
        deaths_per_round=["%.2f" % number for number in deaths_per_round],
        adr=["%.2f" % number for number in adr] )


# Results
@app.route('/results', methods=['GET','POST'])
def results():
    if request.method == 'GET':
        
        team_id = str(request.args.get('team', ''))
        player_id = str(request.args.get('player', ''))
        rep_id = str(request.args.get('rep_id', ''))

        # Open the team df
        filename = 'webapp_dict_team.sav'
        df_team  = pickle.load(open(filename, 'rb'))

        # Open the player df
        filename = 'webapp_dict_player.sav'
        df_player  = pickle.load(open(filename, 'rb'))

        team_name = df_team.loc[int(team_id)]['team_name']

        player_name = df_player.loc[int(player_id)]['name']
        rep_name    = df_player.loc[int(rep_id)]['name']

        # Get the features for the model

        tmp = df_team.loc[int(team_id)]
        
        player_name_vec = [ 
            tmp.player_name_1, tmp.player_name_2, tmp.player_name_3, tmp.player_name_4, tmp.player_name_5
        ]

        player_id_vec = [ 
            tmp.player_id_1, tmp.player_id_2, tmp.player_id_3, tmp.player_id_4, tmp.player_id_5
        ]

        rating_team = 0.0
        prize_team  = 0.0

        rating_new = 0.0
        prize_new  = 0.0

        for id_tmp in player_id_vec:
            rating_team = rating_team + df_player.loc[id_tmp]['rating']
            prize_team  = prize_team + df_player.loc[id_tmp]['prize_rating']

            if id_tmp == int(player_id):
                # Use the replacement
                rating_new = rating_new + df_player.loc[int(rep_id)]['rating']
                prize_new  = prize_new + df_player.loc[int(rep_id)]['prize_rating']
            else:
                rating_new = rating_new + df_player.loc[id_tmp]['rating']
                prize_new  = prize_new + df_player.loc[id_tmp]['prize_rating']


        rating_team = rating_team / 5.0
        prize_team  = prize_team / 5.0

        rating_new = rating_new / 5.0
        prize_new  = prize_new / 5.0

        rating_op = df_team.loc[int(team_id)]['avg_op_rating']
        prize_op = df_team.loc[int(team_id)]['avg_op_prize_rating']

        # Open the fit model
        filename = 'model_jan30.sav'
        loaded_model = pickle.load(open(filename, 'rb'))

        # Before the change
        if prize_team > prize_op:
            features = [[ (rating_team-rating_op), (prize_team-prize_op) ]]
        else:
            features = [[ -(rating_team-rating_op), -(prize_team-prize_op) ]]

        prob_before = loaded_model.predict_proba(features)

        # After the change
        if prize_new > prize_op:
            features = [[ (rating_new-rating_op), (prize_new-prize_op) ]]
        else:
            features = [[ -(rating_new-rating_op), -(prize_new-prize_op) ]]

        prob_after = loaded_model.predict_proba(features)

        prob_change = '{:.1%}'.format(prob_after[0][1] - prob_before[0][1])
        
        # N = 400
        # x = np.random.random(size=N) * 100
        # y = np.random.random(size=N) * 100
        # radii = np.random.random(size=N) * 1.5
        # colors = [
        #     "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*x, 30+2*y)
        # ]

        # TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

        # p = figure(tools=TOOLS)

        # p.scatter(x, y, radius=radii,
        #         fill_color=colors, fill_alpha=0.6,
        #         line_color=None)

        # output_file("color_scatter.html", title="color_scatter.py example")


    return render_template('results.html',title='Results',team_name=team_name,player_name=player_name,rep_name=rep_name,
        rating_team=rating_team,prob_before=prob_before,prob_after=prob_after,
        prob_change=prob_change,player_name_vec=player_name_vec,player_id_vec=player_id_vec,player_id=int(player_id))

