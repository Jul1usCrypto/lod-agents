"""
LoD Agent SDK — Random Agent
================================
An agent that picks random actions from the action space.
Useful as a baseline for comparison.

Usage:
    python examples/random_agent.py
"""

from pylol.env import lol_env
from pylol.env import run_loop
from pylol.agents import base_agent
from pylol.lib import actions
import random


class RandomAgent(base_agent.BaseAgent):
    """Agent that takes completely random actions each step."""

    def step(self, obs):
        super().step(obs)

        me = obs.observation["me_unit"]
        
        # Random action type: 0=noop, 1=move, 2=spell
        action_type = random.choice([0, 1, 1, 2])  # Bias toward movement

        if action_type == 0:
            return actions.FunctionCall(0, [[0]])

        elif action_type == 1:
            # Random move within range of current position
            x = me["position_x"] + random.uniform(-1000, 1000)
            y = me["position_y"] + random.uniform(-1000, 1000)
            return actions.FunctionCall(1, [[0], [x, y]])

        else:
            # Random spell (Q=0, W=1, E=2, R=3)
            spell = random.randint(0, 3)
            x = me["position_x"] + random.uniform(-600, 600)
            y = me["position_y"] + random.uniform(-600, 600)
            return actions.FunctionCall(2, [[spell], [x, y]])


def main():
    config_path = "config_dirs.txt"
    host = "localhost"

    players = [
        lol_env.Agent(champion="Ezreal", team="BLUE"),
        lol_env.Agent(champion="Ezreal", team="PURPLE"),
    ]

    agents = [RandomAgent(), RandomAgent()]

    print("LoD Agent SDK — Random Agent (baseline)")
    print()

    with lol_env.LoLEnv(
        host=host,
        map_name="Old Summoners Rift",
        players=players,
        agent_interface_format=lol_env.parse_agent_interface_format(
            feature_map=16000, feature_move_range=8
        ),
        human_observer=False,
        cooldowns_enabled=False,
        config_path=config_path
    ) as env:
        run_loop.run_loop(agents, env, max_episodes=1, max_steps=300)


if __name__ == "__main__":
    main()
