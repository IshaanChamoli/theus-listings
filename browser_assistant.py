import asyncio
from browser_use import Agent
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from typing import List

async def get_property_urls(company_page: str, property_names: List[str]) -> List[tuple[str, str]]:
    """
    Get URLs for multiple property listings from a company page.
    Limited to 20 steps per property to avoid infinite loops.
    
    Args:
        company_page: URL of the company's property listings page
        property_names: List of property names to search for
        
    Returns:
        List of tuples containing (property_name, property_url)
    """
    # Load environment variables
    load_dotenv()
    
    # Ensure OPENROUTER_API_KEY is set
    if not os.getenv("OPENROUTER_API_KEY"):
        raise ValueError("Please set your OPENROUTER_API_KEY in the .env file")

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Initialize results list
    results = []
    
    # Initialize the LLM using OpenRouter API key
    llm = ChatOpenAI(
        model="openai/gpt-4",
        api_key=os.getenv('OPENROUTER_API_KEY'),
        base_url="https://openrouter.ai/api/v1",
        temperature=0
    )

    # Process each property
    for property_name in property_names:
        try:
            print(f"\n=== Processing: {property_name} ===")
            print(f"On website: {company_page}")
            
            # Construct the task prompt
            task = (
                f"go to {company_page} and open up the individual property listing for {property_name}. "
                "You might have to scroll down, manage lazy loading, or pagination. "
                "Finally return the url you went to for that individual property listing"
            )
            
            # Create the agent with max_steps limit
            agent = Agent(
                task=task,
                llm=llm,
                use_vision=True,
                save_conversation_path="logs/conversation.json",
                max_steps=20
            )

            # Run the agent and get history
            history = await agent.run()
            
            # Get the result URL
            result_url = history.final_result()
            
            if result_url:
                print(f"✅ Found URL: {result_url}")
                results.append((property_name, result_url))
            else:
                print(f"❌ No URL found for: {property_name} (may have exceeded 20 steps)")
                results.append((property_name, None))
            
            if history.has_errors():
                print("Errors encountered:", history.errors())

        except Exception as e:
            print(f"Error processing {property_name}: {str(e)}")
            results.append((property_name, None))
            
        # Add a small delay between requests
        await asyncio.sleep(2)
    
    return results

async def main():
    """
    Example usage of the get_property_urls function
    """
    # Example properties
    company_page = "https://foresitecre.com/investment-sales/"
    property_names = [
        "The Offices at Rogers Creek (Rogers BTW Wiseman & MT Evans, San Antonio, TX 78251, USA)",
        "Live Oak Pad Sites (NWC Loop 1604 & Palisades Dr., Live Oak, TX, 78233)",
    ]
    
    try:
        results = await get_property_urls(company_page, property_names)
        # Just print the array of URLs
        urls = [url for _, url in results if url]
        print("\nFound URLs:", urls)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 