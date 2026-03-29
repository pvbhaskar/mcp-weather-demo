from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("weather")

# Weather API details
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-demo/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the National Weather Service API."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=20.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Turn one weather alert into readable text."""
    props = feature.get("properties", {})
    event = props.get("event", "Unknown event")
    area = props.get("areaDesc", "Unknown area")
    severity = props.get("severity", "Unknown severity")
    description = props.get("description", "No description available")
    instruction = props.get("instruction", "No instructions provided")

    return (
        f"Event: {event}\n"
        f"Area: {area}\n"
        f"Severity: {severity}\n"
        f"Description: {description}\n"
        f"Instructions: {instruction}"
    )


@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    Get active weather alerts for a US state.

    Example input: CA, TX, NY
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data:
        return "Sorry, I could not fetch alerts right now."

    features = data.get("features", [])
    if not features:
        return f"No active alerts found for {state}."

    results = [format_alert(feature) for feature in features[:5]]
    return "\n\n---\n\n".join(results)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Get weather forecast for a location using latitude and longitude.

    Example input:
    latitude = 37.7749
    longitude = -122.4194
    """
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Sorry, I could not fetch forecast data for that location."

    forecast_url = points_data.get("properties", {}).get("forecast")
    if not forecast_url:
        return "Forecast URL not found for that location."

    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return "Sorry, I could not fetch the detailed forecast."

    periods = forecast_data.get("properties", {}).get("periods", [])
    if not periods:
        return "No forecast periods found."

    lines = []
    for period in periods[:5]:
        name = period.get("name", "Unknown")
        temp = period.get("temperature", "Unknown")
        unit = period.get("temperatureUnit", "")
        forecast = period.get("detailedForecast", "No forecast available")

        lines.append(f"{name}: {temp}{unit} - {forecast}")

    return "\n\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")