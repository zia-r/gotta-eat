import asyncio
import httpx
import mcp.types as types
import os

RESY_API_KEY = os.environ.get("RESY_API_KEY", None)

if RESY_API_KEY is None:
    with open(".env", "r") as r:
        for line in r:
            key, value = line.strip().split("=")
            if key == "RESY_API_KEY":
                RESY_API_KEY = value
                break

AUTH_HEADER = f"ResyAPI api_key=\"{RESY_API_KEY}\""
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'


def get_search_url(cuisine: str) -> str:
    return f"https://api.resy.com/3/venuesearch/search"

async def search_restaurants(cuisine: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
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
    "query": "i",
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

async def main():
    await search_restaurants("indian")

if __name__ == "__main__":
    asyncio.run(main())
