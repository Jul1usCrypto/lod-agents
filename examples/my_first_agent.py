"""
LoD Agent SDK — My First Agent
================================
A minimal example that creates an agent which chases and attacks the enemy.

Usage:
    python examples/my_first_agent.py

Prerequisites:
    - Game server built (run setup_server.bat first)
    - Redis installed and available
    - pip install -e .
"""

from pylol.env import lol_env
from pylol.env import run_loop
from pylol.agents import base_agent
from pylol.lib import actions


class ChaseAndAttackAgent(base_agent.BaseAgent):
    """A simple agent that moves toward the enemy and casts Q when in range.
    
    Action format:
        no_op:  FunctionCall(0, [])
        move:   FunctionCall(1, [[dx, dy]])         — move_range point (0-7, center=4)
        spell:  FunctionCall(2, [[slot], [x, y]])   — spell enum + absolute map position
    """

    def step(self, obs):
        super().step(obs)

        me = obs.observation["me_unit"]
        enemy = obs.observation["enemy_unit"]

        # Calculate distance to enemy
        enemy_pos = [enemy["position_x"], enemy["position_y"]]
        my_pos = [me["position_x"], me["position_y"]]
        
        dx = enemy_pos[0] - my_pos[0]
        dy = enemy_pos[1] - my_pos[1]
        dist = (dx**2 + dy**2) ** 0.5

        if dist < 600:
            # In range — cast Q (spell slot 0) at enemy position
            print(f"[Agent {me['user_id']}] Casting Q at enemy! (dist: {dist:.0f})")
            return actions.FunctionCall(2, [[0], enemy_pos])
        else:
            # Too far — move toward enemy using relative move_range
            # move_range is [0..7] where 4 = center (no move)
            # Map direction to a point in [0,7] grid
            import math
            length = max(dist, 1)
            norm_dx = dx / length
            norm_dy = dy / length
            move_x = int(4 + norm_dx * 3)  # 4 = center, ±3 max offset
            move_y = int(4 + norm_dy * 3)
            move_x = max(0, min(7, move_x))
            move_y = max(0, min(7, move_y))
            print(f"[Agent {me['user_id']}] Moving toward enemy (dist: {dist:.0f}) -> [{move_x},{move_y}]")
            return actions.FunctionCall(1, [[move_x, move_y]])


def main():
    # === Configuration ===
    config_path = "config_dirs.txt"
    map_name = "Old Summoners Rift"
    max_steps = 200          # ~26 seconds of game time
    max_episodes = 1
    host = "localhost"
    feature_map_size = 16000
    feature_move_range = 8

    # === Define Players ===
    # Two Ezreals: one on each team
    players = [
        lol_env.Agent(champion="Ezreal", team="BLUE"),
        lol_env.Agent(champion="Ezreal", team="PURPLE"),
    ]

    # === Create Agents ===
    # Both players use our custom agent
    agents = [
        ChaseAndAttackAgent(),
        ChaseAndAttackAgent(),
    ]

    print("=" * 60)
    print("  LoD Agent SDK — My First Agent")
    print("  Two Ezreals chasing and attacking each other")
    print("=" * 60)
    print()

    # === Run the Game ===
    with lol_env.LoLEnv(
        host=host,
        map_name=map_name,
        players=players,
        agent_interface_format=lol_env.parse_agent_interface_format(
            feature_map=feature_map_size,
            feature_move_range=feature_move_range
        ),
        human_observer=True,
        cooldowns_enabled=False,
        config_path=config_path
    ) as env:
        run_loop.run_loop(agents, env, max_episodes=max_episodes, max_steps=max_steps)

    print()
    print("Game complete!")


if __name__ == "__main__":
    main()
