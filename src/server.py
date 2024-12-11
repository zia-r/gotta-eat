from typing import Any
import asyncio
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

server = Server("gotta-eat")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="search-restaurants",
            description="Look at available restaurants in a given area",
            inputSchema={
                "type": "object",
                "properties": {
                    "cuisine": {
                        "type": "string",
                        "description": "Cuisine to search for",
                    },
                },
                "required": [""],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can fetch weather data and notify clients of changes.
    """
    if not arguments:
        raise ValueError("Missing arguments")
  
    if name == "search-restaurants":
        return [types.TextContent(type="text", text="Adda")]
        # state = arguments.get("state")
        # if not state:
        #     raise ValueError("Missing state parameter")

        # # Convert state to uppercase to ensure consistent format
        # state = state.upper()
        # if len(state) != 2:
        #     raise ValueError("State must be a two-letter code (e.g. CA, NY)")

        # async with httpx.AsyncClient() as client:
        #     alerts_url = f"{NWS_API_BASE}/alerts?area={state}"
        #     alerts_data = await make_nws_request(client, alerts_url)

        #     if not alerts_data:
        #         return [types.TextContent(type="text", text="Failed to retrieve alerts data")]

        #     features = alerts_data.get("features", [])
        #     if not features:
        #         return [types.TextContent(type="text", text=f"No active alerts for {state}")]

        #     # Format each alert into a concise string
        #     formatted_alerts = [format_alert(feature) for feature in features[:20]] # only take the first 20 alerts
        #     alerts_text = f"Active alerts for {state}:\n\n" + "\n".join(formatted_alerts)

        #     return [
        #         types.TextContent(
        #             type="text",
        #             text=alerts_text
        #         )
        #     ]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gotta-eat",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

# This is needed if you'd like to connect to a custom client
if __name__ == "__main__":
    print("Starting server")
    asyncio.run(main())

