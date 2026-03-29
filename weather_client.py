import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Tell the client how to start the server
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"],
        env=None,
    )

    # Start the server and connect to it
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Step 1: initialize connection
            await session.initialize()

            print("\nConnected to MCP weather server.\n")

            # Step 2: list available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            # Step 3: call get_alerts
            print("\nCalling get_alerts for CA...\n")
            alerts_result = await session.call_tool(
                "get_alerts",
                arguments={"state": "CA"}
            )
            print("Result from get_alerts:")
            print(alerts_result.content)

            # Step 4: call get_forecast
            print("\nCalling get_forecast for San Francisco coordinates...\n")
            forecast_result = await session.call_tool(
                "get_forecast",
                arguments={"latitude": 37.7749, "longitude": -122.4194}
            )
            print("Result from get_forecast:")
            print(forecast_result.content)


if __name__ == "__main__":
    asyncio.run(main())