import asyncio
from browser_use import Agent
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

async def run_browser_agent():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get OpenRouter API key from environment variables
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not openrouter_api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        return

    # Initialize the language model with OpenRouter configuration
    llm = ChatOpenAI(
        model="openai/gpt-4",  # OpenRouter model ID format
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost:3000",  # Your site URL
            "X-Title": "Browser Agent"  # Your app name
        }
    )

    # Get user input
    user_task = input("What would you like the browser to do? (e.g., 'Search for latest news about AI'): ")

    try:
        # Initialize the agent
        agent = Agent(
            task=user_task,
            llm=llm,
            use_vision=True,  # Enable vision capabilities
            save_conversation_path="conversation_logs.json"  # Save chat logs
        )

        # Run the agent and get history
        print("\nExecuting your request...")
        history = await agent.run()

        # Print results
        print("\nTask completed!")
        print("\nVisited URLs:")
        for url in history.urls():
            print(f"- {url}")

        print("\nExtracted Content:")
        content = history.extracted_content()
        if content:
            print(content)
        
        # Check for any errors
        if history.has_errors():
            print("\nErrors encountered:")
            for error in history.errors():
                print(f"- {error}")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(run_browser_agent())
