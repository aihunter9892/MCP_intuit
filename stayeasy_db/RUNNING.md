# StayEasy DB — Running Guide

SQLite-backed MCP server. Builds on `stayeasy_auth` (keeps the API-key bearer
auth) and replaces the in-memory `LISTINGS` list with a real database.

Covers:
- Database integration patterns for an MCP tool server
- Security: every query is parameterized (`?` placeholders) — user input
  (city, listing_id, guest_name, etc.) is never string-formatted into SQL,
  so there's no SQL injection surface
- Writes wrapped in a transaction (`book_listing` inserts a booking row and
  flips `available` atomically, rolls back on error)

Files:
- `db.py` — SQLite schema (`listings`, `bookings` tables) + seed data + connection helper
- `app.py` — MCP server: `search_listings`, `check_availability`, `book_listing`, `list_bookings`
- `stayeasy.db` — created automatically on first run (gitignored, see below)
- `requirements.txt` — `fastmcp`

---

## 1. Start the server

From `stayeasy_db/`:

```powershell
$env:STAYEASY_API_KEY = "dbkey123"
python -c "import app; app.mcp.run(transport='streamable-http', port=8004)"
```

First run auto-creates `stayeasy.db` next to `app.py` and seeds it with 4
listings. Delete the file to reset to a clean seed state.

Confirm it's up:

```powershell
curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8004/mcp
```

---

## 2. Run it through MCP Inspector

```powershell
npx -y @modelcontextprotocol/inspector
```

Add a server card:

- **Transport Type:** Streamable HTTP
- **URL:** `http://127.0.0.1:8004/mcp`
- **Headers:**
  - Key: `Authorization`
  - Value: `Bearer dbkey123`

Connect, then try:

1. `search_listings` (city=Dubai, guests=2, bedrooms=1, max_price=500) — reads from SQLite
2. `book_listing` (listing_id=ST003, guest_name=Test Guest, check_in=2026-09-01, check_out=2026-09-05) — writes a row, flips availability
3. `list_bookings` — confirms the write actually persisted
4. Re-run `search_listings` — the booked listing no longer appears (available=0)

---

## 3. Connect via `.mcp.json`

```json
{
  "mcpServers": {
    "stayeasydb": {
      "type": "http",
      "url": "http://127.0.0.1:8004/mcp",
      "headers": {
        "Authorization": "Bearer dbkey123"
      }
    }
  }
}
```

Restart the client (or `/mcp` in Claude Code) to pick it up.

---

## 4. Security notes (what this lab demonstrates)

- **Parameterized queries only.** Every tool passes user input as a `?`
  placeholder tuple to `conn.execute(...)`, never via f-string/`.format()`
  into the SQL text. Try passing `city="Dubai' OR '1'='1"` to `search_listings`
  — it's treated as a literal string to match, not executed as SQL.
- **API key still required** — same bearer-token gate as `stayeasy_auth`.
  A DB backend doesn't help if the endpoint itself is open.
- **No raw SQL tool exposed.** Tools are fixed, parameterized operations —
  the model can never construct arbitrary SQL, only call these functions
  with typed arguments.

---

## 5. Deploying (FastMCP Cloud)

`app.py` is the entrypoint. Same flow as `stayeasy_auth`:

1. Push to GitHub, connect repo at fastmcp.cloud, point entrypoint at
   `stayeasy_db/app.py`.
2. Set `STAYEASY_API_KEY` env var in the dashboard.
3. **Caveat:** SQLite is a local file — on most cloud platforms the
   filesystem is ephemeral or not shared across instances, so `stayeasy.db`
   won't persist reliably in production. Fine for this lab/demo; for real
   deployment swap `db.py`'s connection for a hosted database (Postgres,
   Turso, etc.) instead of local SQLite.
