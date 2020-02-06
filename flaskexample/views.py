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

    # Make sure the suggested replacement is not in the team
    for p_id in player_id_vec:
        df_player = df_player[ df_player.index.values != p_id ]

    player_rep_id_vec   = df_player.index.values
    player_rep_name_vec = df_player['name'].values

    prize_stars = df_player['prize_stars'].values
    prize_rating = df_player['prize_rating'].values

    rating_stars = df_player['rating_stars'].values
    rating = df_player['rating'].values

    win_stars = df_player['win_stars'].values
    win_rate = df_player['win_rate'].values

    n_rep = len(win_stars)

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
        ideal_id = str(request.args.get('ideal_id', ''))

        # Open the team df
        filename = 'webapp_dict_team.sav'
        df_team  = pickle.load(open(filename, 'rb'))

        # Open the player df
        filename = 'webapp_dict_player.sav'
        df_player  = pickle.load(open(filename, 'rb'))

        team_name = df_team.loc[int(team_id)]['team_name']

        player_name = df_player.loc[int(player_id)]['name']
        ideal_name  = df_player.loc[int(ideal_id)]['name']


        tmp = df_team.loc[int(team_id)]

        player_name_vec = [ tmp.player_name_1, tmp.player_name_2, tmp.player_name_3, tmp.player_name_4, tmp.player_name_5 ]    
        player_id_vec = [ tmp.player_id_1, tmp.player_id_2, tmp.player_id_3, tmp.player_id_4, tmp.player_id_5 ]
        
        tier_sug_ids = csgo.get_suggestions( int(ideal_id), player_id_vec )

        sug_results = csgo.get_proba_change( int(team_id), int(player_id), tier_sug_ids)
        # sug_results = {}
        # for tier in range(1,6):

        #     sug_results[tier] = {}
        #     sug_results[tier]['name']   = []

        #     sug_results[tier]['rating'] = []
        #     sug_results[tier]['rating_stars'] = []

        #     sug_results[tier]['kills_per_round'] = []
        #     sug_results[tier]['kills_stars'] = []

        #     sug_results[tier]['win_rate'] = []
        #     sug_results[tier]['win_stars'] = []    

        #     sug_results[tier]['change_proba'] = []          


        #     for p_id in tier_sug_ids[tier]:
        #         sug_results[tier]['name'].append( df_player.loc[p_id]['name'] )
                
        #         sug_results[tier]['rating'].append( "%.2f" % df_player.loc[p_id]['rating'] )
        #         sug_results[tier]['kills_per_round'].append( "%.2f" % df_player.loc[p_id]['kills_per_round'] )
        #         sug_results[tier]['win_rate'].append( "%.2f" % df_player.loc[p_id]['win_rate'] )

        #         sug_results[tier]['change_proba'].append( "%.2f" % 0.0 )
                


    return render_template('results.html',title='Results',
        team_name=team_name,
        sug_results=sug_results,
        player_name_vec=player_name_vec,
        player_name=player_name,
        player_id_vec=player_id_vec,
        player_id=int(player_id))

