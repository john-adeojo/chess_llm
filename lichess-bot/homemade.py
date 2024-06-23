"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
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

lichess_id = 'llmchess'


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

    pass


def get_lichess_pgn(game_id):
    url = f"https://lichess.org/game/export/{game_id}.pgn"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

class SingleAgentLLM(MinimalEngine):

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)
        move_history = list(board.move_stack)
        white_moves = [move for index, move in enumerate(move_history) if index % 2 == 0]
        black_moves = [move for index, move in enumerate(move_history) if index % 2 == 1]
        playing_as = 'White' if board.turn == chess.WHITE else 'Black'
        # board_state = board.fen()
        board_state = get_lichess_pgn(lichess_id)
        logging.info(board_state)
        model = 'claude-3-5-sonnet-20240620'
        master1_system_prompt = chess_engine_prompt.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves
                                                        )
        
        master1_response = get_llm_response_claude(json_mode=True, system_prompt=master1_system_prompt, temperature=0, model=model)
        logger.info(master1_response)

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
        board_state = get_lichess_pgn(lichess_id)

        model = 'gpt-4o'
        master1_system_prompt = master1_template.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves
                                                        )
        
        master1_response = get_llm_response_openai(json_mode=False, system_prompt=master1_system_prompt, model=model)
        logger.info(master1_response)

        master2_system_prompt = master2_template.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        proposed_moves=master1_response
                                                        )
        master2_response = get_llm_response_openai(json_mode=False, system_prompt=master2_system_prompt, model=model)
        logger.info(master2_response)

        master3_response = master3_template.format(playing_as=playing_as,
                                                    board_state=board_state,
                                                    white_moves=white_moves,
                                                    black_moves=black_moves,
                                                    proposed_moves=master1_response,
                                                    possible_moves=possible_moves,
                                                    responses=master2_response
                                                    )
        
        master3_response = get_llm_response_openai(json_mode=True, system_prompt=master3_response, model=model)

        
        logger.info(master3_response)

        move = master3_response['best_move']
        return PlayResult(move, None, draw_offered=draw_offered)
    
class LLMMixtureofAgents(MinimalEngine):

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)
        move_history = list(board.move_stack)
        white_moves = [move for index, move in enumerate(move_history) if index % 2 == 0]
        black_moves = [move for index, move in enumerate(move_history) if index % 2 == 1]
        playing_as = 'White' if board.turn == chess.WHITE else 'Black'
        board_state = get_lichess_pgn(lichess_id)
        proposer_layer1_prompt = master1_template.format(playing_as=playing_as, 
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        possible_moves=possible_moves
                                       )
        
        
        model = 'gpt-4o'
        proposer_1_1 = get_llm_response_openai(json_mode=False, system_prompt=proposer_layer1_prompt, model=model, temperature=0.5)
        proposer_1_2 = get_llm_response_openai(json_mode=False, system_prompt=proposer_layer1_prompt, model=model, temperature=0.5)
        proposer_1_3 = get_llm_response_openai(json_mode=False, system_prompt=proposer_layer1_prompt, model=model, temperature=0.5)

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
        proposer_2_2 = get_llm_response_openai(json_mode=False, system_prompt=proposer_2_2_prompt, model=model, temperature=0.5)
        proposer_2_3 = get_llm_response_openai(json_mode=False, system_prompt=proposer_2_3_prompt, model=model, temperature=0.5)


        final_layers_concatenated_responses = proposer_2_1 + proposer_2_2 + proposer_2_3


        aggregator_prompt = aggregator_moa_template.format(playing_as=playing_as,
                                                        board_state=board_state, 
                                                        white_moves=white_moves, 
                                                        black_moves=black_moves, 
                                                        previous_responses=final_layers_concatenated_responses
                                                        )
        
        model = 'claude-3-5-sonnet-20240620'
        aggregator_response = get_llm_response_claude(json_mode=True, system_prompt=aggregator_prompt, model=model)
        

        # master2_response = get_llm_response(json_mode=True, system_prompt=master2_system_prompt)
        # logger.info(master2_response)
        move = aggregator_response['best_move']
        return PlayResult(move, None, draw_offered=draw_offered)