import os
import uuid

from fastmcp import FastMCP
from fastmcp.server.auth.auth import AccessToken, TokenVerifier

from db import get_connection, init_db


API_KEY = os.environ.get("STAYEASY_API_KEY", "changeme-dev-key")


class ApiKeyVerifier(TokenVerifier):
    """Treats the bearer token as a static API key (no OAuth)."""

    async def verify_token(self, token: str) -> AccessToken | None:
        if token != API_KEY:
            return None

        return AccessToken(
            token=token,
            client_id="stayeasy-client",
            scopes=["stayeasy:full"],
            expires_at=None,
        )


mcp = FastMCP(
    "StayEasy DB MCP",
    auth=ApiKeyVerifier(),
)

init_db()


def _listing_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "city": row["city"],
        "area": row["area"],
        "bedrooms": row["bedrooms"],
        "guests": row["guests"],
        "price_per_night": row["price_per_night"],
        "rating": row["rating"],
        "amenities": row["amenities"].split(","),
        "available": bool(row["available"]),
    }


# ============================================================
# TOOL 1 — SEARCH (parameterized query — never string-format
# user input directly into SQL)
# ============================================================

@mcp.tool()
def search_listings(
    city: str,
    guests: int,
    bedrooms: int,
    max_price: float,
) -> list:
    """Search StayEasy accommodation listings stored in SQLite."""

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT * FROM listings
        WHERE LOWER(city) = LOWER(?)
          AND guests >= ?
          AND bedrooms >= ?
          AND price_per_night <= ?
          AND available = 1
        """,
        (city, guests, bedrooms, max_price),
    ).fetchall()

    conn.close()

    return [_listing_to_dict(r) for r in rows]


# ============================================================
# TOOL 2 — CHECK AVAILABILITY
# ============================================================

@mcp.tool()
def check_availability(
    listing_id: str,
    check_in: str,
    check_out: str,
) -> dict:
    """Check availability for a listing."""

    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM listings WHERE id = ?",
        (listing_id,),
    ).fetchone()

    conn.close()

    if row is None:
        return {"error": "Listing not found"}

    return {
        "listing_id": listing_id,
        "check_in": check_in,
        "check_out": check_out,
        "available": bool(row["available"]),
    }


# ============================================================
# TOOL 3 — BOOK (writes a real row, uses a transaction)
# ============================================================

@mcp.tool()
def book_listing(
    listing_id: str,
    guest_name: str,
    check_in: str,
    check_out: str,
) -> dict:
    """Create a booking against the SQLite database."""

    conn = get_connection()

    try:
        row = conn.execute(
            "SELECT available FROM listings WHERE id = ?",
            (listing_id,),
        ).fetchone()

        if row is None:
            return {"success": False, "message": "Listing not found"}

        if not row["available"]:
            return {"success": False, "message": "Listing is not available"}

        booking_id = f"BOOK-{uuid.uuid4().hex[:8].upper()}"

        conn.execute(
            """
            INSERT INTO bookings (booking_id, listing_id, guest_name, check_in, check_out)
            VALUES (?, ?, ?, ?, ?)
            """,
            (booking_id, listing_id, guest_name, check_in, check_out),
        )

        conn.execute(
            "UPDATE listings SET available = 0 WHERE id = ?",
            (listing_id,),
        )

        conn.commit()

        return {
            "success": True,
            "booking_id": booking_id,
            "listing_id": listing_id,
            "guest": guest_name,
            "check_in": check_in,
            "check_out": check_out,
        }
    finally:
        conn.close()


# ============================================================
# TOOL 4 — LIST BOOKINGS (read-only audit tool)
# ============================================================

@mcp.tool()
def list_bookings(listing_id: str | None = None) -> list:
    """List bookings, optionally filtered by listing_id."""

    conn = get_connection()

    if listing_id:
        rows = conn.execute(
            "SELECT * FROM bookings WHERE listing_id = ?",
            (listing_id,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM bookings").fetchall()

    conn.close()

    return [dict(r) for r in rows]


# ============================================================
# LOCAL DEV ENTRYPOINT (FastMCP Cloud imports `mcp` directly)
# ============================================================

if __name__ == "__main__":
    mcp.run()
