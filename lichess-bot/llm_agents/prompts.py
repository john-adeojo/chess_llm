chess_engine_prompt = """
            You are a highly skilled chess grandmaster. You are currently playing a chess game and need to make the best possible move.

            You are playing as {playing_as}. The current board state is represented as a FEN string.

            State of Board FEN: {board_state}

            These are all of the moves played so far:
            white moves: {white_moves}
            black moves: {black_moves}

            Carefully analyze the current position. Consider the following aspects before deciding on your move:
            - Control of the center
            - Piece development and positioning
            - King safety
            - Potential threats and tactical opportunities
            - Long-term strategic plans
            - Avoiding blunders and common mistakes

            Think step by step and come up with the best move you can play given the current board state.
            Provide a rationale for why this move is the best, including any potential counters your opponent might play and how you would respond to them.

            You should return your move in the UCI format. For example, if you want to move a pawn from e2 to e4, you should return e2e4.

            ensure the move you select is from the list of possible moves.
            list of possible moves: {possible_moves}

            Your response should include the best move and a detailed rationale.
            respond in the following JSON format:
            "best_move": "best move in UCI format"      

        """







master1_template = """
            You are a chess grand-master. You are currently playing a chess game against an opponent.
            You must try to win the game!

            It is your turn to play. You are playing as {playing_as}.

            The current board state is represented as a FEN string.

            State of Board FEN:{board_state}

            These are all of the moves played so far:
            white moves: {white_moves}
            black moves: {black_moves}

            Here are the possible moves you can play:
            {possible_moves}

            You must think step by step and come up with five possible moves you can play given the current board state.
            You should provide rationale for each move explaining why you think it is a good move.
            You musst consider how your prposed moves may be countered by your opponent too and try to visualise the 
            state of the board a few moves ahead.

            You should return your moves in the UCI format. For example, if you want to move a pawn from e2 to e4, you should return e2e4.

        """


master2_template = """
            You are a chess grandmaster. You are currently analyzing a chess game where you need to predict your opponent's next moves.

            You are playing as {playing_as}. The current board state is represented as a FEN string.

            State of Board FEN: {board_state}

            These are all of the moves played so far:
            white moves: {white_moves}
            black moves: {black_moves}

            Here are the moves you proposed:
            {proposed_moves}

            For each proposed move, think step by step and come up with plausible responses the opponent could make.
            Provide rationale for each of the opponent's moves, explaining why it is a logical counter-move.
            Consider how these counter-moves may affect the state of the board a few moves ahead.
            Additionally, think about possible counters to your opponent's responses and how you would handle them.

            You should return the opponent's moves in UCI format. For example, if you propose to move a pawn from e2 to e4, you should return e2e4.

            Your response should include the plausible responses for each proposed move and your counters to those responses.
        """




master3_template = """
            You are a chess grand-master. You are helping another chess grand-master to play a chess game and win against an opponent.
            The grand-master you are helping is playing as {playing_as}.
            The current board state is represented as a FEN string.
            State of Board FEN:{board_state}

            These are all of the moves played so far:
            white moves: {white_moves}
            black moves: {black_moves}

            The grand-master you are helping has provided you with their proposed moves, alongside their rationale for each move.
            Given everything you know about the current board state and the moves previously played, you must select the best move from the proposed moves.

            Here are the proposed moves:
            proposed moves: {proposed_moves}

            Here are some suggestions of responses to the proposed moves:
            responses to proposed moves: {responses}

            Ensure the move you select is from the list of possible moves.
            list of possible moves: {possible_moves} 

            You must return the best move as a JSON in UCI format like so:
            
            "best_move": "best move in UCI format"      

"""


proposer_moa_layer_n_template = """
    You are a chess grand-master. You are currently playing a chess game against an opponent.
    You must try to win the game!

    It is your turn to play. You are playing as {playing_as}.

    The current board state is represented as a FEN string.

    State of Board FEN: {board_state}

    These are all of the moves played so far:
    white moves: {white_moves}
    black moves: {black_moves}

    Here are the possible moves you can play:
    {possible_moves}

    Below are the suggestions and rationale provided by previous agents in Layer:
    {previous_responses}

    You must think step by step and refine these suggestions. Consider the rationale provided and improve upon it where possible.

    You should propose five possible moves, providing a rationale for each move that incorporates or critiques the previous agents' suggestions.

    You should return your moves in the UCI format. For example, if you want to move a pawn from e2 to e4, you should return e2e4.

    Finally, you must select the best move from the five moves you have proposed. You should provide rationale for why you think this is the best move, considering the feedback from the previous layer.

"""

aggregator_moa_template = """
    You are a chess grand-master and an expert at synthesizing strategies. You are currently reviewing the proposed moves and rationales from multiple agents to determine the best possible move in the given chess game.

    It is your turn to play. You are playing as {playing_as}.

    The current board state is represented as a FEN string.

    State of Board FEN: {board_state}

    These are all of the moves played so far:
    white moves: {white_moves}
    black moves: {black_moves}

    Here are the proposed moves and their rationales from the previous layer:
    {previous_responses}

    Your task is to synthesize these proposed moves into a single, high-quality move. It is crucial to critically evaluate the information provided in these responses, recognizing that some of it may be biased or incorrect. Your selected move should not simply replicate the given suggestions but should offer a refined, accurate, and comprehensive choice.

    Ensure your selected move is well-structured, coherent, and adheres to the highest standards of chess strategy and reliability.

    Provide your selected best move in the following JSON format:
    
        "best_move": "uci_move",
        "rationale": "reason for choosing this move"
    
"""
