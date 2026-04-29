# 🐍 Snake Game — TSIS-3

A feature-complete Snake game in **Pygame** with PostgreSQL persistence, poison food, power-ups, obstacles, and a full screen UI.

---

## Project layout

```
TSIS3/
├── main.py             # Entry point & all game screens
├── game.py             # Core game logic (snake, food, power-ups, obstacles)
├── db.py               # PostgreSQL layer (psycopg2)
├── settings_manager.py # JSON settings load/save
├── config.py           # Constants & colour palette
├── settings.json       # User preferences (auto-created)
└── README.md
```

---

## Quick start

### 1 — Install dependencies

```bash
pip install pygame psycopg2-binary
```

### 2 — Set up PostgreSQL

Create a database and export the connection string:

```bash
# Example (adjust as needed)
createdb snakedb

export DATABASE_URL="postgresql://postgres:yourpassword@localhost:5432/snakedb"
```

Alternatively set individual variables:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=snakedb
export DB_USER=postgres
export DB_PASS=yourpassword
```

The game will create the `players` and `game_sessions` tables automatically on first run.

> **No PostgreSQL?** The game runs fine without a DB — leaderboard and personal-best features are simply skipped.

### 3 — Run

```bash
python main.py
```

---

## Features

### 3.1 Leaderboard (PostgreSQL + psycopg2)
- Username entry on the Main Menu
- Score, level, and timestamp saved automatically after Game Over
- Top-10 leaderboard screen with rank, username, score, level, date
- Personal best fetched at game start, displayed in HUD

### 3.2 Poison Food
- Dark-red food with an `×` mark spawns randomly (~20% of spawns)
- Eating it **shortens the snake by 2 segments**
- Snake length ≤ 1 after eating poison → **Game Over**
- Poison food never expires on its own

### 3.3 Power-ups
| Power-up     | Effect                              | Duration   |
|-------------|-------------------------------------|------------|
| ⚡ Speed Boost | Increases snake speed (×1.8)       | 5 seconds  |
| 🧊 Slow Motion | Decreases snake speed (×0.5)      | 5 seconds  |
| 🛡 Shield    | Ignores next wall/self/obstacle hit | Until used |

- Only one power-up on the field at a time
- Disappears after **8 seconds** if uncollected
- Active effect shown in HUD with countdown

### 3.4 Obstacles
- Start at **Level 3**; more blocks added each level
- Random wall placement guaranteed not to trap the snake
- Collision → Game Over (same as border)
- Food and power-ups never spawn on obstacles

### 3.5 Settings (JSON)
Settings saved to `settings.json` and loaded on startup:
- **Snake colour** — 7 colour options
- **Grid overlay** — toggle on/off
- **Sound** — toggle on/off

### 3.6 Game Screens
- **Main Menu** — username input, Play / Leaderboard / Settings / Quit
- **Game** — HUD with score, level, personal best, food progress, active effect
- **Game Over** — final score, level, personal best, Retry / Main Menu
- **Leaderboard** — top-10 table, current player highlighted
- **Settings** — grid toggle, sound toggle, colour picker, Save & Back

---

## Controls

| Key               | Action              |
|-------------------|---------------------|
| Arrow keys / WASD | Move snake          |
| P                 | Pause / Resume      |
| Escape            | Return to Main Menu |

---

## Schema

```sql
CREATE TABLE players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
```