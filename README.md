# Rock-Paper-Scissors-Plus-Game
# AI Game Referee: Rock-Paper-Scissors-Plus

An intelligent game referee powered by the **Google Gemini API**. This project demonstrates a deterministic approach to building AI agents by strictly separating **intent understanding** (LLM) from **game rules** (Code).

## 🚀 System Workflow (Step-by-Step)
Here is how the system processes a single turn, ensuring rules are never broken:

1.  **User Input**: The player enters a move (e.g., *"I choose the Bomb!"*).
2.  **Intent Classification**: The **Gemini Agent** interprets this natural language to understand the user's desired action.
3.  **Validation**: The agent calls the `validate_move` tool.
    *   *System Check*: Is "Bomb" a valid move? Has the user already used their one Bomb per game?
    *   *Result*: If invalid, the turn is rejected immediately.
4.  **Resolution**: If valid, the agent calls the `resolve_round` tool.
    *   *Logic Execution*: The Python backbone calculates the winner based on the rules.
        *   *Example*: User plays `Bomb` vs Bot plays `Rock` -> **User Wins** (Bomb > Rock).
    *   *State Update*: The score and game status are updated atomically.
5.  **Response**: The agent receives the structured result and generates a natural language response for the user.

## 1. State Model Architecture
I utilized a **Centralized Transactional State** to guarantee consistency.
*   **Design**: A global `GameState` dataclass serves as the single source of truth.
*   **Attributes**: Tracks `round_number`, `user_score`, `bot_score`, and `bomb_usage_flags`.
*   **Safety**: The state is effectively immutable to the Agent; only specific Tool functions can modify it. This prevents the AI from "hallucinating" score changes.

## 2. Agent & Tool Design
The architecture follows a strict **Controller-Worker pattern**:

*   **The Agent (Controller)**:
    *   **Role**: Natural Language Processing and Orchestration.
    *   **Constraint**: Forbidden from calculating game logic internally. It must delegate to tools.
*   **The Tools (Workers)**:
    *   `validate_move`: Input sanitization and rule enforcement.
    *   `resolve_round`: Deterministic game logic execution.
    *   `update_game_state`: State management and synchronization.

## 3. Engineering Tradeoffs
| Decision | Tradeoff | Rationale |

| **CLI over Web UI** | limited visual appeal | allowed 100% focus on **Agent Architecture** and **State Correctness** within the time constraints. |
| **Global State** | not scalable to multi-user | The most efficient and readable pattern for a single-threaded, local application. |
| **Strict Tooling** | higher latency | Delegating every action to a tool is slower than internal LLM logic, but guarantees **zero rule-breaking**. |

## 4. Future Improvements
*   **Backend Scaling**: Migrate `GameState` to a **Redis** instance to support concurrent users in a web environment.
*   **Contextual Memory**: Inject game history into the system prompt to allow the agent to reference past turns (e.g., *"You're relying too much on Rock!"*).
*   **Automated Evaluation**: Implement a `pytest` suite to simulate 100 games and verify the agent's adherence to the "One Bomb" rule statistically.

**Run Code**: `python main.py`

**SecretKey**:GOOGLE_API_KEY=`Your_API_KEY`
