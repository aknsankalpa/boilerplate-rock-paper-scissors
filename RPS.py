import random

def player(prev_play, opponent_history=[], my_history=[]):
    # Initialize on first call
    if not hasattr(player, 'initialized'):
        player.initialized = True
        opponent_history.clear()
        my_history.clear()
        player.play_order = {"RR": 0, "RP": 0, "RS": 0, "PR": 0, "PP": 0, "PS": 0, 
                            "SR": 0, "SP": 0, "SS": 0}
        player.counter = 0
    
    # Track moves
    if prev_play:
        opponent_history.append(prev_play)
    
    player.counter += 1
    
    # Ideal responses
    ideal_response = {'R': 'P', 'P': 'S', 'S': 'R'}
    
    # QUINCY STRATEGY
    # Quincy plays: R, R, P, P, S (cycle repeats)
    quincy_moves = ["R", "R", "P", "P", "S"]
    quincy_next = quincy_moves[player.counter % 5]
    quincy_counter = ideal_response[quincy_next]
    
    # KRIS STRATEGY  
    # Kris plays the counter to MY previous move
    if len(my_history) > 0:
        kris_response = ideal_response[my_history[-1]]
        kris_counter = ideal_response[kris_response]
    else:
        kris_counter = "P"  # Kris assumes first move is R, so plays P
    
    # MRUGESH STRATEGY
    # Mrugesh counters my most frequent move from last 10 games
    if len(my_history) >= 10:
        last_ten_mine = my_history[-10:]
    else:
        last_ten_mine = my_history
    
    if last_ten_mine:
        # Count frequency of my moves
        freq = {'R': 0, 'P': 0, 'S': 0}
        for move in last_ten_mine:
            freq[move] += 1
        
        # Find most frequent (Mrugesh's logic)
        most_frequent = max(freq, key=freq.get)
        if freq[most_frequent] == 0:
            most_frequent = 'S'  # Mrugesh default
        
        mrugesh_response = ideal_response[most_frequent]
        mrugesh_counter = ideal_response[mrugesh_response]
    else:
        mrugesh_counter = "R"  # Default counter to Mrugesh's default S
    
    # ABBEY STRATEGY
    # Abbey predicts based on my last 2 moves pattern frequency
    if len(my_history) >= 2:
        last_two = "".join(my_history[-2:])
        player.play_order[last_two] += 1
        
        # Abbey's prediction logic
        potential_plays = [
            last_two + "R",
            last_two + "P", 
            last_two + "S"
        ]
        
        # Find most frequent pattern
        max_count = -1
        abbey_prediction = "R"
        
        for play in potential_plays:
            if play in player.play_order:
                count = player.play_order[play]
            else:
                count = 0
            
            if count > max_count:
                max_count = count
                abbey_prediction = play[-1]
        
        abbey_response = ideal_response[abbey_prediction]
        abbey_counter = ideal_response[abbey_response]
    else:
        abbey_counter = "S"  # Counter to Abbey's default P
    
    # OPPONENT IDENTIFICATION
    # Use statistical analysis to identify opponent
    
    if player.counter < 5:
        # Early game - use general strategy
        my_move = random.choice([quincy_counter, kris_counter, mrugesh_counter, abbey_counter])
    
    elif player.counter < 20:
        # Test phase - try to identify opponent
        
        # Check Quincy pattern match
        if len(opponent_history) >= 5:
            quincy_score = 0
            for i in range(min(5, len(opponent_history))):
                expected = quincy_moves[i % 5]
                if opponent_history[i] == expected:
                    quincy_score += 1
            
            if quincy_score >= 4:  # Strong Quincy match
                my_move = quincy_counter
            else:
                # Test other strategies
                strategies = [kris_counter, mrugesh_counter, abbey_counter]
                my_move = random.choice(strategies)
        else:
            my_move = quincy_counter
    
    else:
        # Late game - use best performing strategy
        
        # Calculate recent win rates for each strategy
        recent_games = min(10, len(opponent_history))
        if recent_games > 0:
            recent_opponent = opponent_history[-recent_games:]
            recent_mine = my_history[-recent_games:]
            
            # Score each strategy
            quincy_wins = 0
            kris_wins = 0
            mrugesh_wins = 0
            abbey_wins = 0
            
            for i in range(recent_games):
                opp_move = recent_opponent[i]
                
                # What would each strategy have played?
                game_num = player.counter - recent_games + i
                
                # Quincy counter
                q_move = ideal_response[quincy_moves[game_num % 5]]
                if (q_move == "P" and opp_move == "R") or \
                   (q_move == "R" and opp_move == "S") or \
                   (q_move == "S" and opp_move == "P"):
                    quincy_wins += 1
                
                # Kris counter (if we have previous move)
                if i > 0:
                    prev_my_move = recent_mine[i-1]
                    k_move = ideal_response[ideal_response[prev_my_move]]
                    if (k_move == "P" and opp_move == "R") or \
                       (k_move == "R" and opp_move == "S") or \
                       (k_move == "S" and opp_move == "P"):
                        kris_wins += 1
                
                # Mrugesh counter
                if i >= 9:  # Need 10 moves of history
                    hist_for_mrugesh = recent_mine[i-9:i]
                    if hist_for_mrugesh:
                        freq_m = {'R': 0, 'P': 0, 'S': 0}
                        for m in hist_for_mrugesh:
                            freq_m[m] += 1
                        most_freq_m = max(freq_m, key=freq_m.get)
                        m_move = ideal_response[ideal_response[most_freq_m]]
                        if (m_move == "P" and opp_move == "R") or \
                           (m_move == "R" and opp_move == "S") or \
                           (m_move == "S" and opp_move == "P"):
                            mrugesh_wins += 1
            
            # Choose best performing strategy
            scores = [
                (quincy_wins, quincy_counter),
                (kris_wins, kris_counter), 
                (mrugesh_wins, mrugesh_counter),
                (abbey_wins, abbey_counter)
            ]
            
            best_score, my_move = max(scores, key=lambda x: x[0])
            
            # Add some randomness if performance is poor
            if best_score < recent_games * 0.4:
                if random.random() < 0.3:
                    my_move = random.choice(["R", "P", "S"])
        else:
            my_move = quincy_counter
    
    # Anti-exploitation: occasionally play randomly
    if player.counter > 50 and random.random() < 0.05:
        my_move = random.choice(["R", "P", "S"])
    
    my_history.append(my_move)
    return my_move
