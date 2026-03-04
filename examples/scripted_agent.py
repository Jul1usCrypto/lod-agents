"""
LoD Agent SDK — Scripted Agent
================================
A rule-based agent that uses abilities intelligently based on distance and HP.

Usage:
    python examples/scripted_agent.py
"""

from pylol.env import lol_env
from pylol.env import run_loop
from pylol.agents import base_agent
from pylol.lib import actions
import math


class ScriptedAgent(base_agent.BaseAgent):
    """Rule-based agent with spell rotation and kiting logic."""

    def step(self, obs):
        super().step(obs)

        me = obs.observation["me_unit"]
        enemy = obs.observation["enemy_unit"]

        my_hp_pct = me["current_hp"] / max(me["max_hp"], 1)
        enemy_pos = [enemy["position_x"], enemy["position_y"]]
        my_pos = [me["position_x"], me["position_y"]]

        dx = enemy_pos[0] - my_pos[0]
        dy = enemy_pos[1] - my_pos[1]
        dist = math.sqrt(dx**2 + dy**2)

        # Low HP — run away (kite backward)
        if my_hp_pct < 0.25:
            retreat_x = my_pos[0] - (dx / max(dist, 1)) * 500
            retreat_y = my_pos[1] - (dy / max(dist, 1)) * 500
            return actions.FunctionCall(1, [[0], [retreat_x, retreat_y]])

        # Close range — use full combo
        if dist < 300:
            # Cast W (spell slot 1)
            return actions.FunctionCall(2, [[1], enemy_pos])

        # Medium range — use Q (poke)
        if dist < 800:
            return actions.FunctionCall(2, [[0], enemy_pos])

        # Far — move in
        return actions.FunctionCall(1, [[0], enemy_pos])


def main():
    config_path = "config_dirs.txt"
    host = "localhost"

    players = [
        lol_env.Agent(champion="Ezreal", team="BLUE"),
        lol_env.Agent(champion="Ezreal", team="PURPLE"),
    ]

    agents = [ScriptedAgent(), ScriptedAgent()]

    print("LoD Agent SDK — Scripted Agent (rule-based with kiting)")
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
        run_loop.run_loop(agents, env, max_episodes=1, max_steps=500)


if __name__ == "__main__":
    main()
