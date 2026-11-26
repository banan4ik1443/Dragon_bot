# Dragon PvP — Telegram Mini App prototype

## Included
- Existing game frontend/assets retained.
- PvP matchmaking queue for Telegram users, with queue cancellation.
- Telegram notification on match found and match result.
- Server-side player leaderboard and rating/wins/losses.
- Admin-only test-resource endpoint (`/api/admin/test-resources`).
- Separate balance configuration (`config/balance.js`).
- SQLite database.

## Setup
1. Install Node.js 20+.
2. `npm install`
3. Copy `.env.example` to `.env`, set Telegram bot token, admin Telegram numeric IDs, and a public HTTPS URL.
4. `npm start`
5. Set the bot's Mini App URL to the public HTTPS address serving this app.

## Environment
- `BOT_TOKEN`: bot token from BotFather (required for Telegram WebApp data validation and notifications).
- `ADMIN_IDS`: comma-separated Telegram numeric user IDs.
- `PORT`: optional, defaults to 3000.
- `DB_FILE`: optional SQLite file path.

## PvP prototype caveat
This is a prototype of matchmaking and server-owned result handling, not a fully playable combat engine. Matches resolve after the configured match timeout with a server-generated winner; this should be replaced with actual combat rules and a server-authoritative battle state before public launch. Telegram notifications require users to have started the bot first. Existing legacy client-side PvE/economy code is retained and has not been fully migrated to the server.

## Admin test resources
After Telegram authentication, admin-only endpoint: `POST /api/admin/test-resources` (the server validates Telegram identity and `ADMIN_IDS`). This is intentionally not exposed as a client button.

## Deployment recommendation
Use HTTPS behind a reverse proxy (Caddy/Nginx), persistent storage for the SQLite file, and backups. Never commit `.env` or the database to source control.

## Elemental combat model (prototype)

`config/balance.js` contains six element profiles (HP, attack, defense, speed), counter relationships and multipliers. `backend/combat.js` provides server-side deterministic combat simulation with level scaling, advantage/disadvantage and capped levels. Fire is strong into Wind but weak to Water; Water into Fire but weak to Earth; Earth into Water but weak to Wind; Wind into Earth but weak to Fire; Light/Dark counter one another. Tune values in the balance config. This simulation module is a foundation; it is not yet wired into the queue match flow or dragon ownership selection.

## Combat simulation update

The matchmaking queue now stores the player's selected dragon element and level (the frontend sends the active dragon automatically). Match resolution uses the configured elemental combat simulator rather than a random winner. The simulator produces round-by-round damage log and remaining HP, which are saved with the match record. This is still an automatic simulation, not an interactive turn-by-turn arena; the timeout-based resolver remains until the action/state UI is implemented.
