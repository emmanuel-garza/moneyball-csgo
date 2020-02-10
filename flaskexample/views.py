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
    filename = 'webapp_dict_team_feb9.sav'
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
    filename = 'webapp_dict_team_feb9.sav'
    df_team  = pickle.load(open(filename, 'rb'))

    # Replacement options
    filename = 'webapp_dict_player_feb9.sav'
    df_player  = pickle.load(open(filename, 'rb'))

    tmp = df_team.loc[int(team_id)]
    team_name = tmp.team_name
 
    player_name_vec = [ 
        tmp.player_name_1, tmp.player_name_2, tmp.player_name_3, tmp.player_name_4, tmp.player_name_5
    ]

    player_id_vec = [ 
        tmp.player_id_1, tmp.player_id_2, tmp.player_id_3, tmp.player_id_4, tmp.player_id_5
    ]

    team_rating_vec = []
    team_prize_vec  = []
    team_kill_vec   = []

    team_st_rating_vec = []
    team_st_prize_vec  = []
    team_st_kill_vec   = []

    for player_id_tmp in player_id_vec:
        team_rating_vec.append( df_player.at[player_id_tmp,'rating'])
        team_prize_vec.append( df_player.at[player_id_tmp,'prize_rating'])
        team_kill_vec.append( df_player.at[player_id_tmp,'kills_per_round'])

        # Stars
        team_st_rating_vec.append( df_player.at[player_id_tmp,'rating_stars'])
        team_st_prize_vec.append( df_player.at[player_id_tmp,'prize_stars'])
        team_st_kill_vec.append( df_player.at[player_id_tmp,'kills_stars'])
        

    

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
        team_rating_vec = ["%.2f" % number for number in team_rating_vec],
        team_prize_vec  = ["%.2f" % number for number in team_prize_vec],
        team_kill_vec   = ["%.2f" % number for number in team_kill_vec],
        team_st_rating_vec = team_st_rating_vec,
        team_st_prize_vec  = team_st_prize_vec,
        team_st_kill_vec   = team_st_kill_vec,
        player_rep_id_vec=player_rep_id_vec, player_rep_name_vec=player_rep_name_vec, n_rep=n_rep,
        prize_stars=prize_stars,
        rating_stars=rating_stars,
        win_stars=win_stars,
        prize_rating=["%.2f" % number for number in prize_rating],
        rating=["%.2f" % number for number in rating],
        win_rate=["%.2f" % number for number in win_rate] )




# Results
@app.route('/results', methods=['GET','POST'])
def results():
    if request.method == 'GET':
        
        team_id = str(request.args.get('team', ''))
        player_id = str(request.args.get('player', ''))
        ideal_id = str(request.args.get('ideal_id', ''))

        # Open the team df
        filename = 'webapp_dict_team_feb9.sav'
        df_team  = pickle.load(open(filename, 'rb'))

        # Open the player df
        filename = 'webapp_dict_player_feb9.sav'
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

