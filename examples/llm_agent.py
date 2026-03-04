"""
LoD Agent SDK — LLM Agent Template
=====================================
Template for connecting a Large Language Model (GPT, Claude, etc.) to play
League of Degens. The LLM receives game state as text and returns decisions.

Usage:
    1. Set your API key as an environment variable
    2. python examples/llm_agent.py

NOTE: This is a TEMPLATE. You need to implement the LLM API call for your
      preferred provider (OpenAI, Anthropic, local model, etc.)
"""

from pylol.env import lol_env
from pylol.env import run_loop
from pylol.agents import base_agent
from pylol.lib import actions
import json


class LLMAgent(base_agent.BaseAgent):
    """Agent powered by an LLM. Sends game state as text, gets decisions back.
    
    Override `call_llm()` with your preferred API.
    """

    def __init__(self):
        super().__init__()
        self.step_count = 0
        self.decision_interval = 10  # Only call LLM every N steps (save tokens)
        self.last_action = actions.FunctionCall(0, [[0]])  # Default: no-op

    def format_game_state(self, obs):
        """Convert observation to a text prompt for the LLM."""
        me = obs.observation["me_unit"]
        enemy = obs.observation["enemy_unit"]

        state = f"""You are controlling a champion in League of Legends.

YOUR CHAMPION:
- Position: ({me['position_x']:.0f}, {me['position_y']:.0f})
- HP: {me['current_hp']:.0f} / {me['max_hp']:.0f}
- Mana: {me['current_mp']:.0f}
- Level: {me['level']}
- Alive: {bool(me['alive'])}

ENEMY CHAMPION:
- Position: ({enemy['position_x']:.0f}, {enemy['position_y']:.0f})
- HP: {enemy['current_hp']:.0f} / {enemy['max_hp']:.0f}
- Alive: {bool(enemy['alive'])}

AVAILABLE ACTIONS:
1. MOVE x y — Move to position (x, y)
2. SPELL slot x y — Cast spell at position. slot: 0=Q, 1=W, 2=E, 3=R
3. NOOP — Do nothing

Respond with EXACTLY one action in the format above. Think about positioning,
HP management, and when to engage vs retreat."""

        return state

    def parse_llm_response(self, response, obs):
        """Parse the LLM's text response into a game action."""
        me = obs.observation["me_unit"]
        response = response.strip().upper()

        try:
            if response.startswith("MOVE"):
                parts = response.split()
                x, y = float(parts[1]), float(parts[2])
                return actions.FunctionCall(1, [[0], [x, y]])

            elif response.startswith("SPELL"):
                parts = response.split()
                slot = int(parts[1])
                x, y = float(parts[2]), float(parts[3])
                return actions.FunctionCall(2, [[slot], [x, y]])

            elif response.startswith("NOOP"):
                return actions.FunctionCall(0, [[0]])

        except (IndexError, ValueError) as e:
            print(f"[LLM] Failed to parse: {response} — {e}")

        # Fallback: no-op
        return actions.FunctionCall(0, [[0]])

    def call_llm(self, prompt):
        """Override this method with your LLM API call.
        
        Examples:
            # OpenAI
            import openai
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            return response.choices[0].message.content

            # Anthropic
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        """
        # DEFAULT: Simple rule-based fallback (replace with your LLM)
        print("[LLM] No LLM configured — using fallback logic")
        return "MOVE 2000 2000"

    def step(self, obs):
        super().step(obs)
        self.step_count += 1

        # Only query LLM every N steps to save tokens
        if self.step_count % self.decision_interval == 0:
            prompt = self.format_game_state(obs)
            response = self.call_llm(prompt)
            print(f"[LLM] Step {self.step_count}: {response.strip()}")
            self.last_action = self.parse_llm_response(response, obs)

        return self.last_action


def main():
    config_path = "config_dirs.txt"
    host = "localhost"

    players = [
        lol_env.Agent(champion="Ezreal", team="BLUE"),
        lol_env.Agent(champion="Ezreal", team="PURPLE"),
    ]

    # One LLM agent vs one LLM agent
    agents = [LLMAgent(), LLMAgent()]

    print("=" * 60)
    print("  LoD Agent SDK — LLM Agent Template")
    print("  Override call_llm() with your API provider")
    print("=" * 60)
    print()

    with lol_env.LoLEnv(
        host=host,
        map_name="Old Summoners Rift",
        players=players,
        agent_interface_format=lol_env.parse_agent_interface_format(
            feature_map=16000, feature_move_range=8
        ),
        human_observer=False,
        cooldowns_enabled=True,
        config_path=config_path
    ) as env:
        run_loop.run_loop(agents, env, max_episodes=1, max_steps=200)


if __name__ == "__main__":
    main()
