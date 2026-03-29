import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"],
        env=None,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\nConnected to MCP weather server.\n")

            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"- {tool.name}")

            while True:
                print("\nChoose an option:")
                print("1. Get alerts by state")
                print("2. Get forecast by latitude and longitude")
                print("3. Exit")

                choice = input("Enter 1, 2, or 3: ").strip()

                if choice == "1":
                    state = input("Enter US state code (example: CA, TX, NY): ").strip().upper()
                    result = await session.call_tool(
                        "get_alerts",
                        arguments={"state": state}
                    )
                    print("\nWeather Alerts:\n")
                    print(result.content)

                elif choice == "2":
                    lat = float(input("Enter latitude: ").strip())
                    lon = float(input("Enter longitude: ").strip())
                    result = await session.call_tool(
                        "get_forecast",
                        arguments={"latitude": lat, "longitude": lon}
                    )
                    print("\nForecast:\n")
                    print(result.content)

                elif choice == "3":
                    print("Goodbye!")
                    break

                else:
                    print("Invalid choice. Try again.")


if __name__ == "__main__":
    asyncio.run(main())