from mcp.server import MCPServer

mcp = MCPServer("StayEasy Airbnb MCP")


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
        "amenities": [
            "WiFi",
            "Pool",
            "Gym",
            "Parking"
        ],
        "available": True
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
            "Parking"
        ],
        "available": True
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
            "Pool"
        ],
        "available": True
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
            "Sea View"
        ],
        "available": True
    },
    {
        "id": "ST005",
        "title": "Budget Business Studio",
        "city": "Dubai",
        "area": "Business Bay",
        "bedrooms": 1,
        "guests": 2,
        "price_per_night": 90,
        "rating": 4.5,
        "amenities": [
            "WiFi",
            "Kitchen",
            "Parking"
        ],
        "available": True
    },
    {
        "id": "ST006",
        "title": "Downtown Family Residence",
        "city": "Dubai",
        "area": "Downtown Dubai",
        "bedrooms": 3,
        "guests": 6,
        "price_per_night": 280,
        "rating": 4.85,
        "amenities": [
            "WiFi",
            "Pool",
            "Gym",
            "Parking",
            "Kitchen"
        ],
        "available": True
    }
]


# ============================================================
# TOOL 1 — SEARCH LISTINGS
# ============================================================

@mcp.tool()
def search_listings(
    city: str,
    guests: int,
    bedrooms: int,
    max_price: float
) -> list:
    """
    Search StayEasy listings based on location,
    guests, bedrooms and maximum price.
    """

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

        results.append({
            "id": listing["id"],
            "title": listing["title"],
            "area": listing["area"],
            "bedrooms": listing["bedrooms"],
            "guests": listing["guests"],
            "price_per_night": listing["price_per_night"],
            "rating": listing["rating"],
            "amenities": listing["amenities"]
        })

    return results


# ============================================================
# TOOL 2 — CHECK AVAILABILITY
# ============================================================

@mcp.tool()
def check_availability(
    listing_id: str,
    check_in: str,
    check_out: str
) -> dict:
    """
    Check whether a StayEasy listing is available
    for the requested dates.
    """

    for listing in LISTINGS:

        if listing["id"] == listing_id:

            return {
                "listing_id": listing_id,
                "check_in": check_in,
                "check_out": check_out,
                "available": listing["available"]
            }

    return {
        "error": f"Listing {listing_id} not found."
    }


# ============================================================
# TOOL 3 — BOOK LISTING
# ============================================================

@mcp.tool()
def book_listing(
    listing_id: str,
    guest_name: str,
    check_in: str,
    check_out: str
) -> dict:
    """
    Create a fake reservation for a StayEasy listing.
    """

    for listing in LISTINGS:

        if listing["id"] == listing_id:

            if not listing["available"]:
                return {
                    "success": False,
                    "message": "Listing is not available."
                }

            # Fake booking
            listing["available"] = False

            return {
                "success": True,
                "booking_id": "BOOK-" + listing_id,
                "listing_id": listing_id,
                "guest": guest_name,
                "check_in": check_in,
                "check_out": check_out,
                "message": "Booking successfully created."
            }

    return {
        "success": False,
        "message": "Listing not found."
    }


# ============================================================
# RESOURCE — LISTING DETAILS
# ============================================================

@mcp.resource("listing://{listing_id}")
def get_listing(listing_id: str) -> str:
    """
    Return detailed information about a specific listing.
    """

    for listing in LISTINGS:

        if listing["id"] == listing_id:

            return f"""
Listing ID: {listing["id"]}
Name: {listing["title"]}
City: {listing["city"]}
Area: {listing["area"]}
Bedrooms: {listing["bedrooms"]}
Maximum Guests: {listing["guests"]}
Price per Night: ${listing["price_per_night"]}
Rating: {listing["rating"]}
Amenities: {", ".join(listing["amenities"])}
Available: {listing["available"]}
"""

    return f"Listing {listing_id} not found."


# ============================================================
# PROMPT — PLAN A STAY
# ============================================================

@mcp.prompt()
def plan_stay(
    city: str,
    guests: int,
    bedrooms: int,
    max_price: float,
    nights: int
) -> str:
    """
    Create a structured accommodation planning workflow.
    """

    return f"""
You are a travel accommodation assistant.

The customer is looking for accommodation with:

City: {city}
Guests: {guests}
Bedrooms: {bedrooms}
Maximum price per night: ${max_price}
Number of nights: {nights}

Follow this workflow:

1. Search for matching listings.
2. Compare the available properties.
3. Consider price, rating, location and amenities.
4. Calculate the approximate total cost for {nights} nights.
5. Recommend the best three options.
6. Explain the trade-offs between the options.
7. Do not invent listing information.
8. Use the available MCP tools and resources when necessary.
"""


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    mcp.run()