import pandas as pd
import pickle




def get_proba_change( team_id, player_id, tier_sug_ids):

    # Open the team df
    filename = 'webapp_dict_team_feb9.sav'
    df_team  = pickle.load(open(filename, 'rb'))

    # Open the player df
    filename = 'webapp_dict_player_feb9.sav'
    df_player  = pickle.load(open(filename, 'rb'))

    # Get the features for the model
    tmp = df_team.loc[int(team_id)]
    
    feature_names = ['prize_rating',  'score_dif', 
        'win_rate', 'scaled_win', 'scaled_rating','win_rate_map', 'kd_per_round',
        'momentum']

    # rating_op = df_team.loc[team_id]['avg_op_rating']
    # prize_op  = df_team.loc[team_id]['avg_op_prize_rating']
    
    player_id_vec = [ 
        tmp.player_id_1, tmp.player_id_2, tmp.player_id_3, tmp.player_id_4, tmp.player_id_5
    ]

    # Open the fit model
    # filename = 'model_jan30.sav'
    filename = 'final_model_rand_forest_feb_9_2020.sav'
    loaded_model = pickle.load(open(filename, 'rb'))


    filename = 'dict_normalization_feb9.sav'
    dict_normalization = pickle.load(open(filename, 'rb'))


    sug_results = {}
    for tier in range(1,6):

        sug_results[tier] = {}
        sug_results[tier]['name']   = []

        sug_results[tier]['rating'] = []
        sug_results[tier]['rating_stars'] = []

        sug_results[tier]['kills_per_round'] = []
        sug_results[tier]['kills_stars'] = []

        sug_results[tier]['win_rate'] = []
        sug_results[tier]['win_stars'] = []    

        sug_results[tier]['change_proba'] = []  
        sug_results[tier]['change_proba_str'] = []          

        for p_id in tier_sug_ids[tier]:
            sug_results[tier]['name'].append( df_player.loc[p_id]['name'] )
            
            sug_results[tier]['rating'].append( "%.2f" % df_player.loc[p_id]['rating'] )
            sug_results[tier]['kills_per_round'].append( "%.2f" % df_player.loc[p_id]['kills_per_round'] )
            sug_results[tier]['win_rate'].append( "%.2f" % df_player.loc[p_id]['win_rate'] )

            sug_results[tier]['rating_stars'].append( df_player.loc[p_id]['rating_stars'] )
            sug_results[tier]['kills_stars'].append( df_player.loc[p_id]['kills_stars'] )
            sug_results[tier]['win_stars'].append( df_player.loc[p_id]['win_stars'] )

            # Compute the model part
            rep_id = p_id


            # rating_team = 0.0
            # prize_team  = 0.0

            # rating_new = 0.0
            # prize_new  = 0.0

            
            features_before = []
            features_after  = []

            for feat in feature_names:

                feat_team = 0.0  
                feat_new  = 0.0          

                for id_tmp in player_id_vec:

                    feat_team = feat_team + df_player.loc[id_tmp][feat]

                #     rating_team = rating_team + df_player.loc[id_tmp]['rating']
                #     prize_team  = prize_team + df_player.loc[id_tmp]['prize_rating']

                    if id_tmp == int(player_id):
                        # Use the replacement
                        feat_new = feat_new + df_player.loc[rep_id][feat]
                    else:
                        feat_new = feat_new + df_player.loc[id_tmp][feat]

                # Average
                feat_team = feat_team / 5.0
                feat_new  = feat_new / 5.0

                # Normalize!
                feat_team = (feat_team - dict_normalization[feat]['mean'])/dict_normalization[feat]['std']
                feat_new  = (feat_new  - dict_normalization[feat]['mean'])/dict_normalization[feat]['std']


                features_before.append( feat_team )
                features_after.append ( feat_new )
                # # Average
                # rating_team = rating_team / 5.0
                # prize_team  = prize_team / 5.0

                # rating_new = rating_new / 5.0
                # prize_new  = prize_new / 5.0

            
            
            prob_before = loaded_model.predict_proba([features_before])
            prob_after  = loaded_model.predict_proba([features_after])
                     

            #prob_change = '{:.1%}'.format(prob_after[0][1] - prob_before[0][1])
            prob_change = (prob_after[0][1] - prob_before[0][1])


            # Append the probability change
            sug_results[tier]['change_proba'].append( (prob_after[0][1] - prob_before[0][1]) )
            sug_results[tier]['change_proba_str'].append( '{:.1%}'.format(prob_after[0][1] - prob_before[0][1]) )
            

    

    return sug_results




def get_suggestions( player_id, team_player_ids ):
    
    n_per_tier = 5

    # Open the player df
    filename = 'webapp_dict_player_feb9.sav'
    df_dist  = pickle.load(open(filename, 'rb'))

    # Remove the players in the team
    for p_id in team_player_ids:
        df_dist = df_dist[ df_dist.index.values != p_id ]
    
    column_vec = ['prize_rating', 'rating', 'hs_kills', 'kills_per_round','deaths_per_round', 'ADR']
    
    df_dist['dist'] = 0.0*df_dist['prize_stars'].values
    
    # Normalize
    for column in column_vec:
        df_dist[column] = (df_dist[column]-df_dist[column].mean()) / (df_dist[column].std())

    for column in column_vec:
        df_dist['dist'] = df_dist['dist'] + (df_dist[column]-df_dist.loc[player_id][column])**2


    df_dist = df_dist.sort_values('dist',ascending=True)


    # Top 5 from each tier
    tier_sug_ids = {}
    tier_sug_ids[5] = df_dist[ df_dist['prize_stars']==5 ].index.values[0:n_per_tier]
    tier_sug_ids[4] = df_dist[ df_dist['prize_stars']==4 ].index.values[0:n_per_tier]
    tier_sug_ids[3] = df_dist[ df_dist['prize_stars']==3 ].index.values[0:n_per_tier]
    tier_sug_ids[2] = df_dist[ df_dist['prize_stars']==2 ].index.values[0:n_per_tier]
    tier_sug_ids[1] = df_dist[ df_dist['prize_stars']==1 ].index.values[0:n_per_tier]

    return tier_sug_ids