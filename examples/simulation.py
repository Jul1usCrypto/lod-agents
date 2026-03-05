"""
LoD Agent SDK — 5v5 Team Fight Simulation
============================================
Total mayhem: 10 AI agents in a 5v5 team fight at mid lane.

Usage:
    python examples/simulation.py

Prerequisites:
    - Game server built (run setup_server.bat first)
    - Redis installed and available
    - v4.20 League client path set in config_dirs.txt
    - pip install -e .
"""

import math
import random
import time

from pylol.env import lol_env
from pylol.agents import base_agent
from pylol.lib import actions


class BerserkerAgent(base_agent.BaseAgent):
    """All-in melee fighter. Charges at closest enemy, spams all spells."""

    def __init__(self, name="Berserker"):
        super().__init__()
        self.name = name
        self.tick = 0

    def step(self, obs):
        super().step(obs)
        self.tick += 1
        me = obs.observation["me_unit"]
        enemy = obs.observation["enemy_unit"]

        if me["alive"] == 0.0:
            return actions.FunctionCall(0, [])

        enemy_pos = [enemy["position_x"], enemy["position_y"]]
        my_pos = [me["position_x"], me["position_y"]]
        dx = enemy_pos[0] - my_pos[0]
        dy = enemy_pos[1] - my_pos[1]
        dist = max((dx**2 + dy**2) ** 0.5, 1)

        if dist < 600:
            spell = self.tick % 4  # cycle Q W E R
            return actions.FunctionCall(2, [[spell], enemy_pos])
        else:
            move_x = int(4 + (dx / dist) * 3)
            move_y = int(4 + (dy / dist) * 3)
            return actions.FunctionCall(1, [[max(0, min(7, move_x)), max(0, min(7, move_y))]])


class SpellSpamAgent(base_agent.BaseAgent):
    """Ranged mage. Fires abilities from distance, repositions randomly."""

    def __init__(self, name="SpellSpam"):
        super().__init__()
        self.name = name
        self.tick = 0

    def step(self, obs):
        super().step(obs)
        self.tick += 1
        me = obs.observation["me_unit"]
        enemy = obs.observation["enemy_unit"]

        if me["alive"] == 0.0:
            return actions.FunctionCall(0, [])

        enemy_pos = [enemy["position_x"], enemy["position_y"]]
        my_pos = [me["position_x"], me["position_y"]]
        dx = enemy_pos[0] - my_pos[0]
        dy = enemy_pos[1] - my_pos[1]
        dist = max((dx**2 + dy**2) ** 0.5, 1)

        if dist < 900:
            spell = self.tick % 3  # cycle Q W E
            return actions.FunctionCall(2, [[spell], enemy_pos])
        else:
            # Move toward enemy with slight randomness
            jx = random.randint(-1, 1)
            jy = random.randint(-1, 1)
            move_x = int(4 + (dx / dist) * 2) + jx
            move_y = int(4 + (dy / dist) * 2) + jy
            return actions.FunctionCall(1, [[max(0, min(7, move_x)), max(0, min(7, move_y))]])


class ChaosAgent(base_agent.BaseAgent):
    """Pure chaos. Random spells, random movement, total unpredictability."""

    def __init__(self, name="Chaos"):
        super().__init__()
        self.name = name

    def step(self, obs):
        super().step(obs)
        me = obs.observation["me_unit"]
        enemy = obs.observation["enemy_unit"]

        if me["alive"] == 0.0:
            return actions.FunctionCall(0, [])

        enemy_pos = [enemy["position_x"], enemy["position_y"]]

        roll = random.random()
        if roll < 0.5:
            # Random spell at enemy
            spell = random.randint(0, 3)
            return actions.FunctionCall(2, [[spell], enemy_pos])
        else:
            # Random movement
            return actions.FunctionCall(1, [[random.randint(0, 7), random.randint(0, 7)]])


class HunterAgent(base_agent.BaseAgent):
    """Assassin-style. Dashes in, bursts with all spells, then repositions."""

    def __init__(self, name="Hunter"):
        super().__init__()
        self.name = name
        self.burst_phase = 0

    def step(self, obs):
        super().step(obs)
        me = obs.observation["me_unit"]
        enemy = obs.observation["enemy_unit"]

        if me["alive"] == 0.0:
            return actions.FunctionCall(0, [])

        enemy_pos = [enemy["position_x"], enemy["position_y"]]
        my_pos = [me["position_x"], me["position_y"]]
        dx = enemy_pos[0] - my_pos[0]
        dy = enemy_pos[1] - my_pos[1]
        dist = max((dx**2 + dy**2) ** 0.5, 1)

        hp_pct = me["current_hp"] / max(me["max_hp"], 1)

        if dist < 500:
            # Burst combo: Q -> W -> E -> R -> reposition
            if self.burst_phase < 4:
                spell = self.burst_phase
                self.burst_phase += 1
                return actions.FunctionCall(2, [[spell], enemy_pos])
            else:
                # Reposition sideways
                self.burst_phase = 0
                perp_x = int(4 + (dy / dist) * 3)
                perp_y = int(4 - (dx / dist) * 3)
                return actions.FunctionCall(1, [[max(0, min(7, perp_x)), max(0, min(7, perp_y))]])
        elif hp_pct < 0.2:
            # Low HP — run away
            move_x = int(4 - (dx / dist) * 3)
            move_y = int(4 - (dy / dist) * 3)
            return actions.FunctionCall(1, [[max(0, min(7, move_x)), max(0, min(7, move_y))]])
        else:
            # Close the gap
            self.burst_phase = 0
            move_x = int(4 + (dx / dist) * 3)
            move_y = int(4 + (dy / dist) * 3)
            return actions.FunctionCall(1, [[max(0, min(7, move_x)), max(0, min(7, move_y))]])


def run_5v5(agents, env, max_steps=1000):
    """5v5 team fight run loop."""
    controller = env._controllers[0]
    controller.connect()

    steps = 0
    start_time = time.time()
    num_agents = len(agents)

    observation_spec = [env.observation_spec() for _ in agents]
    action_spec = [env.action_spec() for _ in agents]

    for agent, obs_spec, act_spec in zip(agents, observation_spec, action_spec):
        agent.setup(obs_spec, act_spec)

    try:
        timesteps = env.reset()

        # Teleport all players to mid-lane for team fight
        num_players = len(agents)
        half = num_players // 2
        for i in range(1, half + 1):
            x = 6800.0 + random.uniform(-200, 200)
            y = 6800.0 + random.uniform(-200, 200)
            controller.player_teleport(i, x, y)
        for i in range(half + 1, num_players + 1):
            x = 7400.0 + random.uniform(-200, 200)
            y = 7400.0 + random.uniform(-200, 200)
            controller.player_teleport(i, x, y)

        env.broadcast_msg("TEAM FIGHT!")
        print("\nWaiting 3s for setup...")
        time.sleep(3)

        for a in agents:
            a.reset()

        while True:
            steps += 1
            if max_steps and steps > max_steps:
                break

            if steps % 50 == 0:
                elapsed = time.time() - start_time
                print(f"\n{'='*60}")
                print(f"  STEP {steps}/{max_steps}  |  {elapsed:.0f}s elapsed  |  {steps/elapsed:.1f} fps")
                print(f"{'='*60}")

            act_list = [agent.step(timestep)
                        for agent, timestep in zip(agents, timesteps)]

            if timesteps[0].last():
                print("\n" + "!" * 60)
                print("  GAME OVER — TEAM FIGHT CONCLUDED!")
                print("!" * 60)
                break

            timesteps = env.step(act_list)

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    finally:
        elapsed_time = time.time() - start_time
        print(f"\nSimulation: {steps-1} steps in {elapsed_time:.1f}s ({(steps-1)/max(elapsed_time,0.1):.1f} fps)")


def main():
    config_path = "config_dirs.txt"
    map_name = "Old Summoners Rift"

    # ========== 5v5 MELEE BRAWL ==========
    players = [
        lol_env.Agent(champion="Garen",      team="BLUE"),
        lol_env.Agent(champion="Darius",     team="BLUE"),
        lol_env.Agent(champion="MasterYi",   team="BLUE"),
        lol_env.Agent(champion="Tryndamere", team="BLUE"),
        lol_env.Agent(champion="Garen",      team="BLUE"),
        lol_env.Agent(champion="Tryndamere", team="PURPLE"),
        lol_env.Agent(champion="Garen",      team="PURPLE"),
        lol_env.Agent(champion="Darius",     team="PURPLE"),
        lol_env.Agent(champion="MasterYi",   team="PURPLE"),
        lol_env.Agent(champion="Darius",     team="PURPLE"),
    ]

    agents = [
        BerserkerAgent(name="BLUE Garen"),
        BerserkerAgent(name="BLUE Darius"),
        HunterAgent(name="BLUE MasterYi"),
        BerserkerAgent(name="BLUE Tryndamere"),
        BerserkerAgent(name="BLUE Garen2"),
        BerserkerAgent(name="PURPLE Tryndamere"),
        BerserkerAgent(name="PURPLE Garen"),
        BerserkerAgent(name="PURPLE Darius"),
        HunterAgent(name="PURPLE MasterYi"),
        HunterAgent(name="PURPLE Darius2"),
    ]

    print()
    print("=" * 60)
    print("  LoD Agent SDK — 5v5 MELEE BRAWL")
    print("=" * 60)
    print("  BLUE:   Garen + Darius + MasterYi + Tryndamere + Garen")
    print("  PURPLE: Tryndamere + Garen + Darius + MasterYi + Darius")
    print("  All melee — 10 agents!")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)
    print()

    with lol_env.LoLEnv(
        host="localhost",
        map_name=map_name,
        players=players,
        agent_interface_format=lol_env.parse_agent_interface_format(
            feature_map=16000,
            feature_move_range=8
        ),
        human_observer=True,
        cooldowns_enabled=True,
        manacosts_enabled=False,
        minion_spawns_enabled=False,
        multiplier=3.0,
        config_path=config_path
    ) as env:
        run_5v5(agents, env, max_steps=1000)

    print("\nSimulation finished!")


if __name__ == "__main__":
    main()
