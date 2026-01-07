"""
Main entry point for Rock-Paper-Scissors-Plus Game Referee.
CLI-based conversational game loop.
"""

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError
from referee_agent import create_referee_agent, process_agent_response, REFEREE_SYSTEM_PROMPT
from game_tools import reset_game, game_state

# Load environment variables from .env file
load_dotenv()


def print_banner():
    """Print game banner."""
    print("\n" + "="*50)
    print("🎮  ROCK-PAPER-SCISSORS-PLUS GAME REFEREE  🎮")
    print("="*50 + "\n")


def get_api_key():
    """Get Google API key from environment or user input."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found in environment variables.")
        api_key = input("Please enter your Google API key: ").strip()
    return api_key


def handle_api_call(func, *args, max_retries=3, **kwargs):
    """Handle API calls with retry logic for rate limits."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "retryDelay" in error_str:
                # Extract retry delay if available
                retry_delay = 30  # Increased default delay
                if "retryDelay" in error_str:
                    try:
                        import re
                        match = re.search(r"'retryDelay':\s*'(\d+)(\.\d+)?s'", error_str)
                        if match:
                            retry_delay = float(match.group(1))
                            if retry_delay < 1:
                                retry_delay = 2  # Enforce minimum delay
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    print(f"⏳ Rate limit hit. Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Rate limit exceeded. Please wait a few minutes and try again.")
                    raise
            else:
                raise
        except Exception as e:
            raise
    

def main():
    """Main game loop."""
    print_banner()
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    # Initialize agent
    try:
        client, agent_config = create_referee_agent(api_key)
        print("✅ Agent initialized successfully!\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Reset game state
    reset_game()
    
    # Start chat session
    try:
        chat = client.chats.create(
            model="gemini-2.0-flash-lite",
            config=agent_config
        )
    except Exception as e:
        print(f"❌ Failed to create chat session: {e}")
        return
    
    # Welcome message
    print("🤖 Referee: Welcome! Let me explain the rules...\n")
    try:
        welcome_response = handle_api_call(
            process_agent_response,
            client, chat, 
            "Hello! Please explain the game rules briefly and ask me for my first move."
        )
        print(f"🤖 Referee:\n{welcome_response}\n")
    except Exception as e:
        print(f"❌ Error getting welcome message: {e}")
        print("\n💡 Tip: If you're seeing rate limit errors, wait 1-2 minutes and try again.")
        print("Google's free tier has limits of 15 requests per minute.\n")
        return
    
    # Game loop
    while not game_state.game_over:
        # Get user input
        user_input = input("Your move: ").strip()
        
        if not user_input:
            continue
        
        # Check for quit command
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n👋 Thanks for playing! Goodbye.")
            break
        
        # Process move
        try:
            response = handle_api_call(process_agent_response, client, chat, user_input)
            print(f"\n🤖 Referee:\n{response}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("💡 Rate limit reached. Please wait a minute and try again.\n")
                break
            continue
        
        # Check if game is over
        if game_state.game_over:
            print("\n" + "="*50)
            print("Thanks for playing! 🎮")
            print("="*50 + "\n")
            break
    
    # Ask if user wants to play again
    if game_state.game_over:
        play_again = input("\nWould you like to play again? (yes/no): ").strip().lower()
        if play_again in ["yes", "y"]:
            reset_game()
            main()


if __name__ == "__main__":
    main()
