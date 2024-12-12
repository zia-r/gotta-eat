import asyncio

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
import httpx

import subprocess

import os
import logging

# Configure the logging
logging.basicConfig(
    filename='app.log',           # Name of the log file
    level=logging.INFO,           # Log level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

server = Server("gotta-eat")

AUTH_HEADER = 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """
    return [
        types.Resource(
            uri=AnyUrl(f"note://internal/{name}"),
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """
    if uri.scheme != "note":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    name = uri.path
    if name is not None:
        name = name.lstrip("/")
        return notes[name]
    raise ValueError(f"Note not found: {name}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return [
        types.Prompt(
            name="summarize-notes",
            description="Creates a summary of all notes",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Style of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    if name != "summarize-notes":
        raise ValueError(f"Unknown prompt: {name}")

    style = (arguments or {}).get("style", "brief")
    detail_prompt = " Give extensive details." if style == "detailed" else ""

    return types.GetPromptResult(
        description="Summarize the current notes",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                    + "\n".join(
                        f"- {name}: {content}"
                        for name, content in notes.items()
                    ),
                ),
            )
        ],
    )

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="search-restaurants",
            description="Search for restaurants in a given area",
            inputSchema={
                "type": "object",
                "properties": {
                    "cuisine": {"type": "string"},
                },
                "required": ["cuisine"],
            },
        ),
        types.Tool(
            name="find-reservation-times",
            description="Find reservation times for a restaurant",
            inputSchema={
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "string"},
                    "party_size": {"type": "number"},
                    "date": {"type": "string"},
                },
                "required": ["restaurant_id", "party_size", "date"],
            },
        ),
        types.Tool(
            name="let-me-see",
            description="Show me the restaurant",
            inputSchema={
                "type": "object",
                "properties": {
                    "restaurant_name": {"type": "string"},
                },
                "required": ["restaurant_name"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    logging.info(f'calling tool {name} with arguments {arguments}')
    if name == "search-restaurants":
        logging.info(f'calling search-restaurants with arguments {arguments}')
        return await search_restaurants(arguments.get("cuisine"))
    if name == "find-reservation-times":
        logging.info(f'calling find-reservation-times with arguments {arguments}')
        return await find_reservation_times(arguments.get("restaurant_id"), arguments.get("party_size"), arguments.get("date"))
    if name == "let-me-see":
        if not arguments or "restaurant_name" not in arguments:
            raise ValueError("Missing restaurant name")
        logging.info(f'calling let-me-see with arguments {arguments}')
        os.chdir("/Users/stankley/Development/gotta-eat/frontend")
        subprocess.call(f"/Users/stankley/Development/gotta-eat/frontend/.venv/bin/viewer \"{arguments.get('restaurant_name')} New York Restaurant\"", shell=True)

        return [types.TextContent(type="text", text="Launched videos")]
    if name != "add-note":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    note_name = arguments.get("name")
    content = arguments.get("content")

    if not note_name or not content:
        raise ValueError("Missing name or content")

    # Update server state
    notes[note_name] = content

    # Notify clients that resources have changed
    await server.request_context.session.send_resource_list_changed()

    return [
        types.TextContent(
            type="text",
            text=f"Added note '{note_name}' with content: {content}",
        )
    ]

def get_search_url(cuisine: str) -> str:
    return f"https://api.resy.com/3/venuesearch/search"

async def search_restaurants(cuisine: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    return [types.TextContent(type="text", text="Adda venue id: 7291")]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            get_search_url(cuisine), 
            data = {
                "geo": {
                    "latitude": 40.744679,
                    "longitude": -73.9485424
                },
                "highlight": {
                    "pre_tag": "<b>",
                    "post_tag": "</b>"
                },
                "per_page": 5,
                "query": cuisine,
                "slot_filter": {
                    "day": "2024-12-11",
                    "party_size": 2
                },
                "types": [
                    "venue",
                    "cuisine"
                ]
            },
            headers={'Authorization': AUTH_HEADER, 'User-Agent': USER_AGENT}
        )
        response.raise_for_status()
        return [types.TextContent(type="text", text=str(response.json()))]

    return [types.TextContent(type="text", text="Adda")]

def get_reservation_url(venue_id: str, party_size: int, date: str) -> str:
    # https://api.resy.com/4/find?lat=0&long=0&day=2024-12-11&party_size=2&venue_id=7291
    return f"https://api.resy.com/4/find?lat=0&long=0&day={date}&party_size={party_size}&venue_id={venue_id}"

async def find_reservation_times(restaurant_id: str, party_size: int, date: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    async with httpx.AsyncClient() as client:
        logging.info(f'finding reservation times for {restaurant_id} on {date} for {party_size} people')
        response = await client.get(get_reservation_url(restaurant_id, party_size, date), headers={'Authorization': AUTH_HEADER, 'User-Agent': USER_AGENT})
        response.raise_for_status()
        return [types.TextContent(type="text", text=str(response.json()))]


async def main():
    # Run the server using stdin/stdout streams
    logging.info(f'starting server')
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