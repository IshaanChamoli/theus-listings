import asyncio
from browser_use import Agent
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Configuration variables
COMPANY_PAGE = "https://foresitecre.com/investment-sales/"
PROPERTY_NAME = "The Offices at Rogers Creek (Rogers BTW Wiseman & MT Evans, San Antonio, TX 78251, USA)"

async def run_browser_task():
    """
    Run a browser task using Browser Use agent to find a specific property listing
    """
    try:
        # Initialize the LLM using OpenRouter API key
        llm = ChatOpenAI(
            model="openai/gpt-4",  # Using OpenAI's model through OpenRouter
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1",
            temperature=0
        )
        
        # Construct the task prompt
        task = (
            f"go to {COMPANY_PAGE} and open up the individual property listing for {PROPERTY_NAME}. "
            "You might have to scroll down, manage lazy loading, or pagination. "
            "Finally return the url you went to for that individual property listing"
        )
        
        # Create the agent
        agent = Agent(
            task=task,
            llm=llm,
            use_vision=True,  # Enable vision capabilities for better web interaction
            save_conversation_path="logs/conversation.json"  # Save logs for debugging
        )

        # Run the agent and get history
        history = await agent.run()

        # Print results
        print("\n=== Task Completed ===")
        print("Visited URLs:", history.urls())
        print("Final Result:", history.final_result())
        
        if history.has_errors():
            print("\nErrors encountered:", history.errors())

        return history.final_result()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

async def main():
    """
    Main function to run the browser assistant
    """
    # Load environment variables
    load_dotenv()
    
    # Ensure OPENROUTER_API_KEY is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Please set your OPENROUTER_API_KEY in the .env file")
        return

    print("=== Browser Assistant ===")
    print(f"Searching for: {PROPERTY_NAME}")
    print(f"On website: {COMPANY_PAGE}")
    
    print("\nExecuting task...")
    result = await run_browser_task()
    
    if result:
        print(f"\nProperty URL found: {result}")

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the main function
    asyncio.run(main()) 