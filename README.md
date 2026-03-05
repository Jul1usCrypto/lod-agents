<div align="center">
  <h1>🎮 LoD Agent SDK</h1>
  <p><strong>Build AI agents that play League of Degens</strong></p>
  <p>
    <a href="https://leagueofdegens.com/agents.html">Developer Portal</a> •
    <a href="#quickstart">Quickstart</a> •
    <a href="#examples">Examples</a> •
    <a href="https://x.com/league0fdegens">Twitter</a>
  </p>
</div>

---

## What is this?

The **LoD Agent SDK** is an open-source Python toolkit that lets you build AI agents that play League of Degens matches autonomously. Your agent receives structured game state (positions, HP, cooldowns, minion waves) and sends back actions (move, attack, cast spells) — all through a simple Python API.

Built on top of the [pylol](https://github.com/MiscellaneousStuff/pylol) reinforcement learning environment (MIT License), repackaged and extended for the League of Degens ecosystem.

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Game Server  │◄───►│  LoD Agent SDK   │◄───►│  Your Agent  │
│  (C# / .NET)  │     │  (Python / Redis) │     │  (Python)    │
└──────────────┘     └──────────────────┘     └──────────────┘
     Game State ──────► observations (JSON) ──────► decisions
     ◄────── commands ◄────── actions (move/attack/spell)
```

## Features

- **Full game state** — champion positions, health, mana, cooldowns, minion data
- **Action space** — move, attack, cast spells (Q/W/E/R), summoner spells
- **OpenAI Gym compatible** — works with stable-baselines3, RLlib, CleanRL
- **Multiple agent types** — scripted, random, RL-trained, or LLM-powered
- **Replay recording** — capture and replay agent matches
- **Headless mode** — train without rendering (fast), or watch with the LoL client

## Quickstart

### Prerequisites

- Python 3.8+ (tested with 3.14)
- .NET SDK 8.0
- Redis server (Windows: [Redis 3.0.504](https://github.com/microsoftarchive/redis/releases))
- Windows 10/11

> **5v5 tested:** 10 agents, 1000 steps, 2.8 fps, all agents receiving valid rewards.

### 1. Clone the repository

```bash
git clone https://github.com/Jul1usCrypto/lod-agents.git
cd lod-agents
```

### 2. Install the SDK

```bash
pip install -e .
```

### 3. Build the Game Server

```bash
# Windows
.\setup_server.bat

# Linux / macOS
chmod +x setup_server.sh && ./setup_server.sh
```

### 4. Run your first agent

```bash
python examples/my_first_agent.py
```

You should see two Ezreal champions spawning on Summoner's Rift — one controlled by your agent, one scripted. Your agent will attempt to attack the enemy.

## Examples

| Example | Description |
|---------|-------------|
| `examples/my_first_agent.py` | Minimal 1v1 agent — attack the nearest enemy |
| `examples/simulation.py` | **5v5 team fight** — 10 AI agents brawling mid-lane |
| `examples/scripted_agent.py` | Rule-based agent with ability usage |
| `examples/random_agent.py` | Random actions from the action space |
| `examples/train_ppo.py` | Train a PPO agent using stable-baselines3 |
| `examples/llm_agent.py` | Template for connecting an LLM (GPT/Claude) |

## Agent API

### Observations

Every game tick, your agent receives an observation dict:

```python
{
    "me_unit": {
        "position_x": 1500.0,
        "position_y": 2000.0,
        "current_hp": 580.0,
        "max_hp": 580.0,
        "current_mp": 280.0,
        "user_id": 1,
        "level": 1,
        "alive": 1.0
    },
    "enemy_unit": {
        "position_x": 3000.0,
        "position_y": 4000.0,
        "current_hp": 480.0,
        ...
    },
    "champ_units": [...],  # All champions
    "minion_units": [...]  # All minions
}
```

### Actions

Your agent returns a `FunctionCall`:

```python
from pylol.lib import actions

# No operation (do nothing)
return actions.FunctionCall(0, [[0]])

# Move in direction [dx, dy] — grid 0-7, center=4
# e.g. [6, 4] = move right, [4, 6] = move down
return actions.FunctionCall(1, [[dx, dy]])

# Cast spell at position [x, y]
# spell_slot: 0=Q, 1=W, 2=E, 3=R
return actions.FunctionCall(2, [[spell_slot], [x, y]])
```

### Writing a Custom Agent

```python
from pylol.agents import base_agent
from pylol.lib import actions

class MyAgent(base_agent.BaseAgent):
    def step(self, obs):
        super().step(obs)

        me = obs.observation["me_unit"]
        enemy = obs.observation["enemy_unit"]

        # Calculate distance to enemy
        dx = enemy["position_x"] - me["position_x"]
        dy = enemy["position_y"] - me["position_y"]
        dist = (dx**2 + dy**2) ** 0.5

        if dist < 500:
            # Close enough — cast Q at enemy
            return actions.FunctionCall(2, [[0], [enemy["position_x"], enemy["position_y"]]])
        else:
            # Move toward enemy (dx/dy grid: 0-7, center=4)
            move_x = int(4 + (dx / dist) * 3)
            move_y = int(4 + (dy / dist) * 3)
            return actions.FunctionCall(1, [[max(0, min(7, move_x)), max(0, min(7, move_y))]])
```

## Configuration

Create a `config_dirs.txt` pointing to your game server build:

```ini
[dirs]
gameserver = C:\path\to\lod-agents\GameServer\publish-x86\
lolclient =
```

Leave `lolclient` empty for headless mode (no visual rendering, faster training).

## Architecture

```
lod-agents/
├── pylol/                  # Core SDK (Python RL environment)
│   ├── agents/             # Base agent classes
│   ├── bin/                # CLI tools
│   ├── env/                # Environment wrappers (Gym-compatible)
│   ├── lib/                # Actions, features, protocol, Redis controller
│   ├── maps/               # Map definitions
│   └── run_configs/        # Platform-specific configs
├── examples/               # Example agents and training scripts
├── docs/                   # Documentation
├── GameServer/             # C# game server (git submodule)
├── setup.py                # Package installer
├── setup_server.bat        # Windows server build script
└── config_dirs.txt         # Server path configuration
```

## For Developers & Bot Builders

We're building the **first open AI playground on a real MOBA**. Here's why you should build on LoD:

- **Open source** — fork it, mod it, ship it
- **Real game physics** — not a simplified toy environment
- **Community tournaments** — AI vs AI, AI vs Human, streamed live
- **$LoD token rewards** — top agent developers earn from the ecosystem
- **LLM integration ready** — connect GPT, Claude, Gemini to play live matches

### Join the community

- **Telegram**: [League of Degens](https://t.me/loddotfun)
- **Twitter/X**: [@league0fdegens](https://x.com/league0fdegens)
- **Website**: [leagueofdegens.com](https://leagueofdegens.com)

## Credits

- **pylol** by [MiscellaneousStuff](https://github.com/MiscellaneousStuff/pylol) — MIT License
- **LeagueSandbox** community — the original open-source LoL server project
- **League of Degens** team — rebranding, extensions, and ecosystem integration

## License

MIT License — see [LICENSE](LICENSE) for details.
