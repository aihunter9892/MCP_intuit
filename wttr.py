import httpx
from mcp.server import MCPServer

mcp = MCPServer("Weather MCP Server")


@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a city using wttr.in."""

    url = f"https://wttr.in/{city}?format=j1"

    response = httpx.get(
        url,
        headers={"User-Agent": "MCP-Weather-Demo"},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    current = data["current_condition"][0]

    temperature = current["temp_C"]
    feels_like = current["FeelsLikeC"]
    humidity = current["humidity"]
    description = current["weatherDesc"][0]["value"]
    wind_speed = current["windspeedKmph"]

    return (
        f"Weather in {city}:\n"
        f"Condition: {description}\n"
        f"Temperature: {temperature}°C\n"
        f"Feels like: {feels_like}°C\n"
        f"Humidity: {humidity}%\n"
        f"Wind: {wind_speed} km/h"
    )


if __name__ == "__main__":
    mcp.run()