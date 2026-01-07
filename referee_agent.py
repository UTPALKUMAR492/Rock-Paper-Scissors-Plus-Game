"""
ADK Agent configuration for the Game Referee.
Handles intent understanding and response generation.
"""

from google import genai
from google.genai import types
from game_tools import TOOLS_DECLARATIONS, TOOLS_IMPL


# System prompt for the referee agent
REFEREE_SYSTEM_PROMPT = """You are a Game Referee for Rock-Paper-Scissors-Plus.

GAME RULES (explain in ≤5 lines when game starts):
• Best of 3 rounds
• Valid moves: rock, paper, scissors, bomb
• Bomb beats all moves (bomb vs bomb = draw)
• Each player can use bomb ONCE per game
• Invalid input wastes the round

YOUR ROLE:
1. INTENT UNDERSTANDING: Interpret what the user wants to do
2. VALIDATION: Use validate_move tool to check if move is legal
3. RESOLUTION: Use resolve_round tool to determine winner
4. RESPONSE: Provide clear, round-by-round feedback

RESPONSE FORMAT (for each round):
━━━━━━━━━━━━━━━━━━━━━━━━━━
ROUND [X]/3
Your move: [user_move]
Bot's move: [bot_move]
Result: [outcome explanation]
Score: You [X] - [X] Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT:
• Always validate moves using validate_move tool
• For invalid moves, explain why and count it as a wasted round
• After round 3, automatically end game with final result
• Track bomb usage carefully
• Be concise but clear

When the game ends, display:
🏁 GAME OVER 🏁
Final Score: You [X] - [X] Bot
Result: [User wins/Bot wins/Draw]
"""


def create_referee_agent(api_key: str):
    """Create and configure the ADK agent."""
    client = genai.Client(api_key=api_key)
    
    # Create agent with tools
    agent_config = types.GenerateContentConfig(
        system_instruction=REFEREE_SYSTEM_PROMPT,
        tools=TOOLS_DECLARATIONS,
        temperature=0.7
    )
    
    return client, agent_config


def process_agent_response(client, chat, user_message: str) -> str:
    """
    Send user message to agent and handle tool calls.
    Returns the agent's final response.
    """
    response = chat.send_message(user_message)
    
    # Handle tool calls
    while response.candidates[0].content.parts:
        parts = response.candidates[0].content.parts
        
        # Check if there are function calls
        function_calls = [part.function_call for part in parts if part.function_call]
        
        if not function_calls:
            break
        
        # Execute function calls
        function_responses = []
        for fc in function_calls:
            tool_name = fc.name
            tool_args = dict(fc.args)
            
            # Execute the tool
            if tool_name in TOOLS_IMPL:
                result = TOOLS_IMPL[tool_name](**tool_args)
                function_responses.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response=result
                    )
                )
        
        # Send function responses back to agent
        if function_responses:
            response = chat.send_message(function_responses)
    
    # Extract text response
    text_parts = [part.text for part in response.candidates[0].content.parts if part.text]
    return "\n".join(text_parts)
