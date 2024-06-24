"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
import pprint
import os
import requests
import json
import yaml
import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.types import MOVE, HOMEMADE_ARGS_TYPE
import logging
from llm_agents.prompts import (
    chess_engine_prompt,
    master1_template, 
    master2_template,
    master3_template,
    proposer_moa_layer_n_template,
    aggregator_moa_template,
)

from llm_agents.llms import get_llm_response_groq, get_llm_response_openai, get_llm_response_claude



# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)

global lichess_id 

lichess_id = 'llmchess'


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

    pass


def load_game_state():
    if os.path.exists("game_state.json"):
        with open("game_state.json", "r") as file:
            return json.load(file)
    return {}


class SingleAgentLLM(MinimalEngine):

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)
        logging.info("POSSIBLE MOVES: %s", pprint.pformat(possible_moves))
        move_history = list(board.move_stack)
        white_moves = [move for index, move in enumerate(move_history) if index % 2 == 0]
        black_moves = [move for index, move in enumerate(move_history) if index % 2 == 1]
        playing_as = 'White' if board.turn == chess.WHITE else 'Black'
        board_state = load_game_state()
        logger.info("\n\nBOARD STATE ♟️: %s", pprint.pformat(board_state))
        model = 'claude-3-5-sonnet-20240620'
        master1_system_prompt = chess_engine_prompt.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves
                                                        )
        
        master1_response = get_llm_response_claude(json_mode=True, system_prompt=master1_system_prompt, temperature=0, model=model)
        logger.info("\n\n CHESS MASTER ♞: %s", master1_response)

        move = master1_response['best_move']
        return PlayResult(move, None, draw_offered=draw_offered)
    


# Agent
class LLMMultiAgent(MinimalEngine):

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)
        move_history = list(board.move_stack)
        white_moves = [move for index, move in enumerate(move_history) if index % 2 == 0]
        black_moves = [move for index, move in enumerate(move_history) if index % 2 == 1]
        playing_as = 'White' if board.turn == chess.WHITE else 'Black'
        board_state = load_game_state()
        logger.info("\n\nBOARD STATE ♟️: %s", pprint.pformat(board_state))


        model = 'claude-3-5-sonnet-20240620'
        master1_system_prompt = master1_template.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves
                                                        )
        
        master1_response = get_llm_response_claude(json_mode=False, system_prompt=master1_system_prompt, model=model)
        logger.info("\n\n CHESS MASTER 1 ♟️: %s", master1_response)

        master2_system_prompt = master2_template.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        proposed_moves=master1_response
                                                        )
        master2_response = get_llm_response_claude(json_mode=False, system_prompt=master2_system_prompt, model=model)
        logger.info("\n\n CHESS MASTER 2 ♟️: %s", master2_response)

        master3_response = master3_template.format(playing_as=playing_as,
                                                    board_state=board_state,
                                                    white_moves=white_moves,
                                                    black_moves=black_moves,
                                                    proposed_moves=master1_response,
                                                    possible_moves=possible_moves,
                                                    responses=master2_response
                                                    )
        
        master3_response = get_llm_response_claude(json_mode=True, system_prompt=master3_response, model=model)
        logger.info("\n\n CHESS MASTER 3 ♟️: %s", master3_response)

        move = master3_response['best_move']
        return PlayResult(move, None, draw_offered=draw_offered)
    
class LLMMixtureofAgents(MinimalEngine):

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)
        move_history = list(board.move_stack)
        white_moves = [move for index, move in enumerate(move_history) if index % 2 == 0]
        black_moves = [move for index, move in enumerate(move_history) if index % 2 == 1]
        playing_as = 'White' if board.turn == chess.WHITE else 'Black'
        board_state = load_game_state()
        logger.info("\n\nBOARD STATE ♟️: %s", pprint.pformat(board_state))

        proposer_layer1_prompt = master1_template.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves
                                       )
        
        
        model = 'gpt-4o'
        proposer_1_1 = get_llm_response_openai(json_mode=False, system_prompt=proposer_layer1_prompt, model=model, temperature=0.5)
        logger.info("\n\n PROPOSER 1_1 ♟️: %s", proposer_1_1)
        proposer_1_2 = get_llm_response_openai(json_mode=False, system_prompt=proposer_layer1_prompt, model=model, temperature=0.5)
        logger.info("\n\n PROPOSER 1_2 ♟️: %s", proposer_1_2)
        proposer_1_3 = get_llm_response_openai(json_mode=False, system_prompt=proposer_layer1_prompt, model=model, temperature=0.5)
        logger.info("\n\n PROPOSER 1_3 ♟️: %s", proposer_1_3)

        proposer_2_1_prompt = proposer_moa_layer_n_template.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves,
                                                        previous_responses=proposer_1_1
                                                        )
        proposer_2_2_prompt = proposer_moa_layer_n_template.format(playing_as=playing_as,
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves,
                                                        previous_responses=proposer_1_2
                                                        )
        proposer_2_3_prompt = proposer_moa_layer_n_template.format(playing_as=playing_as,
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves,
                                                        previous_responses=proposer_1_3
                                                        )
        
        proposer_2_1 = get_llm_response_openai(json_mode=False, system_prompt=proposer_2_1_prompt, model=model, temperature=0.5)
        logger.info("\n\n PROPOSER 2_1 ♟️: %s", proposer_2_1)
        proposer_2_2 = get_llm_response_openai(json_mode=False, system_prompt=proposer_2_2_prompt, model=model, temperature=0.5)
        logger.info("\n\n PROPOSER 2_2 ♟️: %s", proposer_2_2)
        proposer_2_3 = get_llm_response_openai(json_mode=False, system_prompt=proposer_2_3_prompt, model=model, temperature=0.5)
        logger.info("\n\n PROPOSER 2_3 ♟️: %s", proposer_2_3)


        final_layers_concatenated_responses = proposer_2_1 + proposer_2_2 + proposer_2_3


        aggregator_prompt = aggregator_moa_template.format(playing_as=playing_as,
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        previous_responses=final_layers_concatenated_responses
                                                        )
        
        model = 'claude-3-5-sonnet-20240620'
        aggregator_response = get_llm_response_claude(json_mode=True, system_prompt=aggregator_prompt, model=model)
        logger.info("\n\n AGGREGATOR ♟️: %s", aggregator_response)
        

  
        move = aggregator_response['best_move']
        return PlayResult(move, None, draw_offered=draw_offered)