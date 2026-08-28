import os

from fastmcp import FastMCP
from fastmcp.server.auth.auth import AccessToken, TokenVerifier


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
    "StayEasy Auth MCP",
    auth=ApiKeyVerifier(),
)


# ============================================================
# FAKE DATABASE
# ============================================================

LISTINGS = [
    {
        "id": "ST001",
        "title": "Modern Downtown Apartment",
        "city": "Dubai",
        "area": "Downtown Dubai",
        "bedrooms": 2,
        "guests": 4,
        "price_per_night": 150,
        "rating": 4.8,
        "amenities": ["WiFi", "Pool", "Gym", "Parking"],
        "available": True,
    },
    {
        "id": "ST002",
        "title": "Luxury Marina View Apartment",
        "city": "Dubai",
        "area": "Dubai Marina",
        "bedrooms": 2,
        "guests": 4,
        "price_per_night": 220,
        "rating": 4.9,
        "amenities": [
            "WiFi",
            "Pool",
            "Gym",
            "Sea View",
            "Parking",
        ],
        "available": True,
    },
    {
        "id": "ST003",
        "title": "Cozy JBR Beach Apartment",
        "city": "Dubai",
        "area": "JBR",
        "bedrooms": 1,
        "guests": 2,
        "price_per_night": 130,
        "rating": 4.7,
        "amenities": [
            "WiFi",
            "Beach Access",
            "Pool",
        ],
        "available": True,
    },
    {
        "id": "ST004",
        "title": "Palm Luxury Villa",
        "city": "Dubai",
        "area": "Palm Jumeirah",
        "bedrooms": 4,
        "guests": 8,
        "price_per_night": 600,
        "rating": 4.95,
        "amenities": [
            "WiFi",
            "Private Pool",
            "Beach Access",
            "Parking",
            "Sea View",
        ],
        "available": True,
    },
]


# ============================================================
# TOOL 1 — SEARCH
# ============================================================

@mcp.tool()
def search_listings(
    city: str,
    guests: int,
    bedrooms: int,
    max_price: float,
) -> list:
    """Search StayEasy accommodation listings."""

    results = []

    for listing in LISTINGS:

        if listing["city"].lower() != city.lower():
            continue

        if listing["guests"] < guests:
            continue

        if listing["bedrooms"] < bedrooms:
            continue

        if listing["price_per_night"] > max_price:
            continue

        if not listing["available"]:
            continue

        results.append(listing)

    return results


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

    for listing in LISTINGS:

        if listing["id"] == listing_id:

            return {
                "listing_id": listing_id,
                "check_in": check_in,
                "check_out": check_out,
                "available": listing["available"],
            }

    return {
        "error": "Listing not found"
    }


# ============================================================
# TOOL 3 — BOOK
# ============================================================

@mcp.tool()
def book_listing(
    listing_id: str,
    guest_name: str,
    check_in: str,
    check_out: str,
) -> dict:
    """Create a fake booking."""

    for listing in LISTINGS:

        if listing["id"] == listing_id:

            if not listing["available"]:
                return {
                    "success": False,
                    "message": "Listing is not available",
                }

            listing["available"] = False

            return {
                "success": True,
                "booking_id": f"BOOK-{listing_id}",
                "listing_id": listing_id,
                "guest": guest_name,
                "check_in": check_in,
                "check_out": check_out,
            }

    return {
        "success": False,
        "message": "Listing not found",
    }


# ============================================================
# RESOURCE
# ============================================================

@mcp.resource("listing://{listing_id}")
def get_listing(listing_id: str) -> str:
    """Get detailed information about a listing."""

    for listing in LISTINGS:

        if listing["id"] == listing_id:

            return f"""
Listing ID: {listing["id"]}
Name: {listing["title"]}
City: {listing["city"]}
Area: {listing["area"]}
Bedrooms: {listing["bedrooms"]}
Guests: {listing["guests"]}
Price: ${listing["price_per_night"]}/night
Rating: {listing["rating"]}
Amenities: {", ".join(listing["amenities"])}
Available: {listing["available"]}
"""

    return "Listing not found"


# ============================================================
# PROMPT
# ============================================================

@mcp.prompt()
def plan_stay(
    city: str,
    guests: int,
    bedrooms: int,
    max_price: float,
) -> str:
    """Create a stay-planning workflow."""

    return f"""
Plan accommodation for:

City: {city}
Guests: {guests}
Bedrooms: {bedrooms}
Maximum price: ${max_price}

Search the available StayEasy listings.

Compare:
- Price
- Rating
- Location
- Amenities

Recommend the best options.

Do not invent information.
"""


# ============================================================
# LOCAL DEV ENTRYPOINT (FastMCP Cloud imports `mcp` directly,
# this only runs when executed locally)
# ============================================================

if __name__ == "__main__":
    mcp.run()
