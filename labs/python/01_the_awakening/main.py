"""
Lab P01 - The Awakening 🌅  
A Microsoft Agent Framework ChatAgent comes alive,  
speaking through a local model powered by Docker Model Runner.
"""

import asyncio
import os
from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# Load local .env file (contains OPENAI_API_BASE, OPENAI_API_KEY, etc.)
load_dotenv()

async def main():
    # Pull config from environment (defaults are for local DMR)
    base_url = os.getenv("OPENAI_API_BASE", "http://localhost:12434/engines/llama.cpp/v1")
    api_key = os.getenv("OPENAI_API_KEY", "none")
    model_id = os.getenv("MODEL_ID", "ai/gpt-oss:latest")

    print(f"🧠 Using Microsoft Agent Framework with local model: {model_id}")
    print(f"📡 Endpoint: {base_url}")

    async with ChatAgent(
        chat_client=OpenAIChatClient(
            base_url=base_url,
            api_key=api_key,
            model_id=model_id,
        ),
        instructions="You are a friendly local assistant running using Docker Model Runner.",
    ) as agent:
        # Interact
        user_prompt = "Explain in one line what a local AI agent is."
        
        # Run the agent synchronously:
        result = await agent.run(user_prompt)
        print("\n💬 User:", user_prompt)
        print("🤖 Agent (sync answer):", result.text)

        # Run the agent asynchronously (streaming):
        user_prompt = "Now explain it in a poetic way, with a sonnet, considering the beauty of running it locally instead of relying on the cloud."
        print("\n💬 User:", user_prompt)
        print("🤖 Agent (streaming): \n", end="")
        async for chunk in agent.run_stream(user_prompt):
            if chunk.text:
                print(chunk.text, end="")
        print("")

if __name__ == "__main__":
    asyncio.run(main())
