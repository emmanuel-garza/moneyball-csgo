
def get_suggestions( player_id ):
    
    n_per_tier = 5

    # Open the player df
    filename = 'webapp_dict_player.sav'
    df_dist  = pickle.load(open(filename, 'rb'))
    
    column_vec = ['prize_rating', 'rating', 'hs_kills', 'kills_per_round','deaths_per_round', 'ADR']
    
    df_dist['dist'] = 0.0*df_player['prize_stars'].values
    
    # Normalize
    for column in column_vec:
        df_dist[column] = (df_dist[column]-df_dist[column].mean()) / (df_dist[column].std())

    for column in column_vec:
        df_dist['dist'] = df_dist['dist'] + (df_dist[column]-df_dist.loc[player_id][column])**2


    df_dist = df_dist.sort_values('dist',ascending=True)


    # Top 5 from each tier
    tier_sug_ids = {}
    tier_sug_ids[5] = df_dist[ df_dist['prize_stars']==5 ].values[0:n_per_tier]
    tier_sug_ids[4] = df_dist[ df_dist['prize_stars']==4 ].values[0:n_per_tier]
    tier_sug_ids[3] = df_dist[ df_dist['prize_stars']==3 ].values[0:n_per_tier]
    tier_sug_ids[2] = df_dist[ df_dist['prize_stars']==2 ].values[0:n_per_tier]
    tier_sug_ids[1] = df_dist[ df_dist['prize_stars']==1 ].values[0:n_per_tier]

    return tier_sug_ids