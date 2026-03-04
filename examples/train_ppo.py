"""
LoD Agent SDK — PPO Training Example
=======================================
Train a reinforcement learning agent using Proximal Policy Optimization (PPO)
with stable-baselines3.

Usage:
    pip install stable-baselines3
    python examples/train_ppo.py

This example wraps the LoL environment in an OpenAI Gym interface and trains
an agent to maximize distance from (or damage to) the enemy champion.
"""

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:
    import gym
    from gym import spaces

from pylol.env import lol_env
from pylol.lib import actions, features


class LoLGymEnv(gym.Env):
    """OpenAI Gym wrapper around the LoD Agent SDK environment.
    
    Observation space: [my_x, my_y, my_hp, my_mp, enemy_x, enemy_y, enemy_hp]
    Action space: Discrete(5) — noop, move_up, move_down, move_left, move_right
                  + spell Q at enemy
    """
    metadata = {"render_modes": ["human"]}

    def __init__(self, config_path="config_dirs.txt", host="localhost"):
        super().__init__()
        self.config_path = config_path
        self.host = host
        
        # Simplified action space
        # 0: no-op, 1: move toward enemy, 2: move away, 3: cast Q, 4: cast W
        self.action_space = spaces.Discrete(5)
        
        # Observation: [my_x, my_y, my_hp_pct, my_mp_pct, enemy_x, enemy_y, enemy_hp_pct, distance]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32),
            high=np.array([16000, 16000, 1, 1, 16000, 16000, 1, 16000], dtype=np.float32)
        )
        
        self.env = None
        self.max_steps = 300
        self.current_step = 0
        self.prev_enemy_hp = 1.0
        
    def _make_env(self):
        players = [
            lol_env.Agent(champion="Ezreal", team="BLUE"),
            lol_env.Agent(champion="Ezreal", team="PURPLE"),
        ]
        return lol_env.LoLEnv(
            host=self.host,
            map_name="Old Summoners Rift",
            players=players,
            agent_interface_format=lol_env.parse_agent_interface_format(
                feature_map=16000, feature_move_range=8
            ),
            human_observer=False,
            cooldowns_enabled=True,
            config_path=self.config_path
        )

    def _obs_to_array(self, obs):
        me = obs[0].observation["me_unit"]
        enemy = obs[0].observation["enemy_unit"]
        
        my_hp_pct = me["current_hp"] / max(me["max_hp"], 1)
        my_mp_pct = me["current_mp"] / max(me.get("max_mp", 1), 1)
        enemy_hp_pct = enemy["current_hp"] / max(enemy["max_hp"], 1)
        
        dx = enemy["position_x"] - me["position_x"]
        dy = enemy["position_y"] - me["position_y"]
        dist = np.sqrt(dx**2 + dy**2)
        
        return np.array([
            me["position_x"], me["position_y"],
            my_hp_pct, my_mp_pct,
            enemy["position_x"], enemy["position_y"],
            enemy_hp_pct, dist
        ], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if self.env is not None:
            try:
                self.env.close()
            except Exception:
                pass
        
        self.env = self._make_env()
        self.env.__enter__()
        obs = self.env.reset()
        self.current_step = 0
        self.prev_enemy_hp = 1.0
        
        return self._obs_to_array(obs), {}

    def step(self, action):
        self.current_step += 1
        me = None
        enemy = None
        
        # Convert discrete action to game action
        try:
            obs = self.env._observe()
            if obs:
                me = obs[0].observation["me_unit"]
                enemy = obs[0].observation["enemy_unit"]
        except Exception:
            pass
        
        if me is None or enemy is None:
            # Environment died
            return np.zeros(8, dtype=np.float32), 0.0, True, False, {}
        
        enemy_pos = [enemy["position_x"], enemy["position_y"]]
        my_pos = [me["position_x"], me["position_y"]]
        dx = enemy_pos[0] - my_pos[0]
        dy = enemy_pos[1] - my_pos[1]
        dist = np.sqrt(dx**2 + dy**2)
        
        if action == 0:
            game_action = [actions.FunctionCall(0, [[0]])]
        elif action == 1:
            game_action = [actions.FunctionCall(1, [[0], enemy_pos])]
        elif action == 2:
            retreat = [my_pos[0] - dx, my_pos[1] - dy]
            game_action = [actions.FunctionCall(1, [[0], retreat])]
        elif action == 3:
            game_action = [actions.FunctionCall(2, [[0], enemy_pos])]
        elif action == 4:
            game_action = [actions.FunctionCall(2, [[1], enemy_pos])]
        else:
            game_action = [actions.FunctionCall(0, [[0]])]
        
        # Also need an action for player 2 (scripted: attack player 1)
        game_action.append(actions.FunctionCall(2, [[0], my_pos]))
        
        try:
            obs = self.env.step(game_action)
        except Exception:
            return np.zeros(8, dtype=np.float32), 0.0, True, False, {}
        
        obs_array = self._obs_to_array(obs)
        enemy_hp_pct = obs_array[6]
        
        # Reward: damage dealt to enemy
        damage_dealt = self.prev_enemy_hp - enemy_hp_pct
        self.prev_enemy_hp = enemy_hp_pct
        
        reward = damage_dealt * 10.0  # Scale up damage reward
        
        # Small penalty for being too far (encourage engaging)
        if dist > 1000:
            reward -= 0.01
        
        # Bonus for killing enemy
        if enemy_hp_pct <= 0:
            reward += 50.0
        
        # Check termination
        my_hp_pct = obs_array[2]
        terminated = my_hp_pct <= 0 or enemy_hp_pct <= 0
        truncated = self.current_step >= self.max_steps
        
        return obs_array, reward, terminated, truncated, {}

    def close(self):
        if self.env is not None:
            try:
                self.env.close()
            except Exception:
                pass


def main():
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import DummyVecEnv
    except ImportError:
        print("ERROR: stable-baselines3 not installed.")
        print("       pip install stable-baselines3")
        return

    print("=" * 60)
    print("  LoD Agent SDK — PPO Training")
    print("  Training an RL agent to fight in League of Degens")
    print("=" * 60)
    print()

    # Create environment
    env = DummyVecEnv([lambda: LoLGymEnv()])

    # Create PPO model
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=128,
        batch_size=64,
        n_epochs=4,
        gamma=0.99,
        tensorboard_log="./runs/"
    )

    # Train
    print("Starting training... (Ctrl+C to stop)")
    total_timesteps = 10000
    model.learn(total_timesteps=total_timesteps)

    # Save
    model.save("lod_ppo_agent")
    print(f"\nModel saved to lod_ppo_agent.zip")
    print("To load: model = PPO.load('lod_ppo_agent')")

    env.close()


if __name__ == "__main__":
    main()
