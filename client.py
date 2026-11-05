import asyncio
import os
import httpx  # Naya import network connection ko stable karne ke liye

# Ye lines network/proxy issues (DNS errors) ko block karne ke liye hain
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY .env file mein nahi mili.")

# 1. Gemini client initialize karein
gemini = genai.Client(api_key=API_KEY)

# 2. Custom HTTP client banayein ReadError se bachne ke liye
custom_http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(timeout=120.0), # Server ko 2 minutes tak wait karne dega
    http2=False, # HTTP/1.1 force karega taaki firewall connection drop na kare
)
# 3. Gemini ko hamara robust custom client use karne ko bolein
gemini._async_httpx_client = custom_http_client


server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            print("\nAvailable MCP tools:")
            for tool in tools_result.tools:
                print("-", tool.name)

            print("\nFetching placement statistics...")

            stats = await session.call_tool("get_stats", arguments={})

            print("\nMCP Statistics:")
            print(stats.content)

            prompt = f"""
            You are a placement application assistant.
            Analyze these placement application statistics:
            {stats.content}

            Give a concise review with:
            1. Current application progress
            2. Important observations
            3. Recommended next actions
            Do not invent missing information.
            """

            print("\nGenerating AI review...")

            # CORRECTED: Yahan par 'await' aur 'gemini.aio' ka use kiya gaya hai 
            # taaki async event loop block na ho aur 503 aane par auto-retry ho sake
            response = await gemini.aio.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )

            print("\n===== AI PLACEMENT REVIEW =====\n")
            print(response.text)


if __name__ == "__main__":
    asyncio.run(main())