"""
Pure game logic for Rock-Paper-Scissors-Plus.
No ADK dependencies - can be tested independently.
"""

from typing import Literal, Tuple
from dataclasses import dataclass

Move = Literal["rock", "paper", "scissors", "bomb"]
Outcome = Literal["user", "bot", "draw"]


@dataclass
class GameState:
    """Represents the current state of the game."""
    round_number: int = 0
    user_score: int = 0
    bot_score: int = 0
    user_bomb_used: bool = False
    bot_bomb_used: bool = False
    game_over: bool = False


def is_valid_move(move: str) -> bool:
    """Check if a move is valid."""
    return move.lower() in ["rock", "paper", "scissors", "bomb"]


def normalize_move(move: str) -> Move:
    """Normalize move to lowercase."""
    return move.lower()


def can_use_bomb(player: str, state: GameState) -> bool:
    """Check if a player can use bomb."""
    if player == "user":
        return not state.user_bomb_used
    elif player == "bot":
        return not state.bot_bomb_used
    return False


def resolve_round(user_move: Move, bot_move: Move) -> Outcome:
    """
    Determine the winner of a round.
    
    Rules:
    - bomb beats all other moves
    - bomb vs bomb → draw
    - rock beats scissors
    - scissors beats paper
    - paper beats rock
    """
    if user_move == bot_move:
        return "draw"
    
    # Bomb logic
    if user_move == "bomb" and bot_move == "bomb":
        return "draw"
    if user_move == "bomb":
        return "user"
    if bot_move == "bomb":
        return "bot"
    
    # Standard RPS logic
    wins = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }
    
    if wins[user_move] == bot_move:
        return "user"
    else:
        return "bot"


def update_score(state: GameState, winner: Outcome) -> GameState:
    """Update the game state based on round outcome."""
    if winner == "user":
        state.user_score += 1
    elif winner == "bot":
        state.bot_score += 1
    return state


def mark_bomb_used(state: GameState, player: str, move: Move) -> GameState:
    """Mark bomb as used if player used it."""
    if move == "bomb":
        if player == "user":
            state.user_bomb_used = True
        elif player == "bot":
            state.bot_bomb_used = True
    return state


def is_game_over(state: GameState) -> bool:
    """Check if game is over (3 rounds completed)."""
    return state.round_number >= 3


def get_final_result(state: GameState) -> str:
    """Get the final game result."""
    if state.user_score > state.bot_score:
        return "User wins"
    elif state.bot_score > state.user_score:
        return "Bot wins"
    else:
        return "Draw"
