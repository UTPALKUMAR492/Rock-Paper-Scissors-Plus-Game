"""
ADK tools for game state management.
These tools are called by the agent to validate moves, resolve rounds, and update state.
"""

from google import genai
from google.genai import types
import random
from game_logic import (
    GameState, is_valid_move, normalize_move, can_use_bomb,
    resolve_round, update_score, mark_bomb_used, is_game_over
)


# Global game state (persists across agent calls)
game_state = GameState()


def get_bot_move() -> str:
    """Generate bot's move. Bot uses bomb strategically."""
    global game_state
    
    # Bot uses bomb in round 2 if not used yet (simple strategy)
    if not game_state.bot_bomb_used and game_state.round_number == 1:
        if random.random() > 0.5:  # 50% chance to use bomb in round 2
            return "bomb"
    
    # Otherwise, random move
    available_moves = ["rock", "paper", "scissors"]
    if not game_state.bot_bomb_used and random.random() > 0.7:  # 30% chance to use bomb
        available_moves.append("bomb")
    
    return random.choice(available_moves)


validate_move_declaration = types.FunctionDeclaration(
    name="validate_move",
    description="Validates the user's move and checks if it's legal (valid move type and bomb availability)",
    parameters={
        "type": "object",
        "properties": {
            "user_input": {
                "type": "string",
                "description": "The raw user input to validate"
            }
        },
        "required": ["user_input"]
    }
)


def validate_move(user_input: str) -> dict:
    """
    Validate user's move.
    Returns: {valid: bool, move: str, reason: str}
    """
    global game_state
    
    user_input = user_input.strip().lower()
    
    if not is_valid_move(user_input):
        return {
            "valid": False,
            "move": user_input,
            "reason": f"Invalid move '{user_input}'. Valid moves: rock, paper, scissors, bomb"
        }
    
    move = normalize_move(user_input)
    
    # Check bomb availability
    if move == "bomb" and not can_use_bomb("user", game_state):
        return {
            "valid": False,
            "move": move,
            "reason": "You have already used your bomb!"
        }
    
    return {
        "valid": True,
        "move": move,
        "reason": "Valid move"
    }


resolve_round_declaration = types.FunctionDeclaration(
    name="resolve_round",
    description="Resolves the current round by comparing user and bot moves, determining the winner, and updating scores",
    parameters={
        "type": "object",
        "properties": {
            "user_move": {
                "type": "string",
                "description": "The user's validated move"
            }
        },
        "required": ["user_move"]
    }
)


def resolve_round_tool(user_move: str) -> dict:
    """
    Resolve the round and update game state.
    Returns: {user_move: str, bot_move: str, winner: str, user_score: int, bot_score: int, round: int}
    """
    global game_state
    
    # Get bot's move
    bot_move = get_bot_move()
    
    # Mark bombs as used
    game_state = mark_bomb_used(game_state, "user", user_move)
    game_state = mark_bomb_used(game_state, "bot", bot_move)
    
    # Determine winner
    winner = resolve_round(user_move, bot_move)
    
    # Update score
    game_state = update_score(game_state, winner)
    
    # Increment round
    game_state.round_number += 1
    
    # Check if game is over
    if is_game_over(game_state):
        game_state.game_over = True
    
    return {
        "user_move": user_move,
        "bot_move": bot_move,
        "winner": winner,
        "user_score": game_state.user_score,
        "bot_score": game_state.bot_score,
        "round": game_state.round_number,
        "game_over": game_state.game_over,
        "user_bomb_available": not game_state.user_bomb_used,
        "bot_bomb_available": not game_state.bot_bomb_used
    }


update_game_state_declaration = types.FunctionDeclaration(
    name="update_game_state",
    description="Updates the game state or retrieves current state information",
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: 'get_state' or 'reset'"
            }
        },
        "required": ["action"]
    }
)


def update_game_state_tool(action: str) -> dict:
    """
    Update or retrieve game state.
    Returns current game state information.
    """
    global game_state
    
    if action == "reset":
        game_state = GameState()
    
    return {
        "round": game_state.round_number,
        "user_score": game_state.user_score,
        "bot_score": game_state.bot_score,
        "user_bomb_available": not game_state.user_bomb_used,
        "bot_bomb_available": not game_state.bot_bomb_used,
        "game_over": game_state.game_over
    }


# Tool implementations mapping
TOOLS_IMPL = {
    "validate_move": validate_move,
    "resolve_round": resolve_round_tool,
    "update_game_state": update_game_state_tool
}


# Tool declarations for ADK
TOOLS_DECLARATIONS = [
    validate_move_declaration,
    resolve_round_declaration,
    update_game_state_declaration
]


def reset_game():
    """Reset the game state."""
    global game_state
    game_state = GameState()
