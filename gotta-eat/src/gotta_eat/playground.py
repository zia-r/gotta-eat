import asyncio
import httpx
import mcp.types as types

AUTH_HEADER = 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"'
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
