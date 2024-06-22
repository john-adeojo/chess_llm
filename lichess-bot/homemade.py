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


# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

    pass


# Bot names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    """Get a random move."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose a random move."""
        return PlayResult(random.choice(list(board.legal_moves)), None)


class Alphabetical(ExampleEngine):
    """Get the first move when sorted by san representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose the first move alphabetically."""
        moves = list(board.legal_moves)
        moves.sort(key=board.san)
        return PlayResult(moves[0], None)


class FirstMove(ExampleEngine):
    """Get the first move when sorted by uci representation."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        """Choose the first move alphabetically in uci representation."""
        moves = list(board.legal_moves)
        moves.sort(key=str)
        return PlayResult(moves[0], None)


class ComboEngine(ExampleEngine):
    """
    Get a move using multiple different methods.

    This engine demonstrates how one can use `time_limit`, `draw_offered`, and `root_moves`.
    """

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:
        """
        Choose a move using multiple different methods.

        :param board: The current position.
        :param time_limit: Conditions for how long the engine can search (e.g. we have 10 seconds and search up to depth 10).
        :param ponder: Whether the engine can ponder after playing a move.
        :param draw_offered: Whether the bot was offered a draw.
        :param root_moves: If it is a list, the engine should only play a move that is in `root_moves`.
        :return: The move to play.
        """
        if isinstance(time_limit.time, int):
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, int) else 0
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, int) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, int) else 0
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, int) else 0

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)

        if my_time / 60 + my_inc > 10:
            # Choose a random move.
            move = random.choice(possible_moves)
        else:
            # Choose the first move alphabetically in uci representation.
            possible_moves.sort(key=str)
            move = possible_moves[0]
        return PlayResult(move, None, draw_offered=draw_offered)
    
# config_path = os.path.join(os.path.dirname(__file__), 'api_keys.yaml')
config_path = 'api_keys.yaml'

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

load_config(config_path)


class LLMEngine(MinimalEngine):

    def search(self, board: chess.Board, time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE) -> PlayResult:

        api_key = os.getenv('OPENAI_API_KEY')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)
        move_history = list(board.move_stack)
        white_moves = [move for index, move in enumerate(move_history) if index % 2 == 0]
        black_moves = [move for index, move in enumerate(move_history) if index % 2 == 1]

        model_endpoint = 'https://api.openai.com/v1/chat/completions'
        temperature = 0
        model = 'gpt-4o'
        system_prompt = f"""
            You are a chess grand-master. You are currently playing a chess game against an opponent.

            It is your turn to play. You are playing as {'White' if board.turn == chess.WHITE else 'Black'}.

            The current board state is represented as a FEN string.

            State of Board FEN:{board.fen()}

            These are all of the moves played so far:
            white moves: f{white_moves}
            black moves: f{black_moves}

            Here are the possible moves you can play:
            {possible_moves}

            Think about the best move you can play and return it as a UCI string following the json format below:
            {{"move": "best move in UCI format"}}

        """
        query = """
            Your opponent has just played a move. Now you must play a move.
        """


        payload = {
                    "model": model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "stream": False,
                    "temperature": temperature,
                }
        
        response_dict = requests.post(model_endpoint, headers=headers, data=json.dumps(payload))
        response_json = response_dict.json()
        response = json.loads(response_json['choices'][0]['message']['content'])
        move = response['move']

        return PlayResult(move, None, draw_offered=draw_offered)