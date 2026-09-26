# ⚡ THE SYSTEM — REAL LIFE RPG // HUNTER OPERATING SYSTEM

A rebuilt, persistent Life OS designed for year-long daily use: quests, XP, finances, shopping, faith, Qur'an, charity, study/BAC planning, lessons, fitness, meals, personal care, skills with sources, calendar/deadlines, reviews, analytics, Pomodoro, rewards, university and scholarships.

## Run locally

1. Install Python 3.11+ from https://www.python.org/downloads/windows/ (use the Windows installer `.exe`).
2. Open a terminal inside this folder.
3. Run:

```bash
python server.py
```

4. Open `http://localhost:3000`.

The app uses SQLite and persists data in `system.sqlite3`.

## Phone + PC synchronization

The app is a PWA and the backend is server-based. For real cross-device synchronization, deploy this folder to a server reachable from both devices and put it behind HTTPS. Local `localhost` data is only on the machine running the server. Do not use `file://` for the synchronized version.

Before public deployment, set a strong `JWT_SECRET`, use HTTPS, backups, rate limiting, and preferably PostgreSQL for multi-instance production.

## Design

Dark/white theme, responsive desktop/tablet/mobile layout, installable PWA shell, live dashboards, SVG/CSS-native visualizations, persistent relational data, user isolation, and real calculations.
