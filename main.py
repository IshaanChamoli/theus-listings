import asyncio
import os
from listings_screenshotter import capture_viewport_screenshots
from image_analyzer import analyze_real_estate_images
from browser_assistant import get_property_urls
from typing import List, Optional

async def process_real_estate_listings(listings_url: str) -> Optional[List[str]]:
    """
    Process a real estate listings page to get individual property URLs
    
    Args:
        listings_url: URL of the main listings page
    Returns:
        List of individual property listing URLs
    """
    try:
        print("\n=== Real Estate Listings Processor ===")
        
        # Step 1: Capture screenshots of the listings page
        print("\n1. Capturing screenshots of listings page...")
        screenshot_paths = await capture_viewport_screenshots(listings_url)
        print(f"✅ Captured {len(screenshot_paths)} screenshots")
        
        # Get the company directory where screenshots were saved
        company_dir = os.path.dirname(screenshot_paths[0])
        
        # Step 2: Analyze screenshots to get property names
        print("\n2. Analyzing screenshots to extract property names...")
        property_names = analyze_real_estate_images(company_dir)
        print(f"✅ Found {len(property_names)} properties")
        
        # Step 3: Get individual property URLs
        print("\n3. Getting individual property URLs...")
        results = await get_property_urls(listings_url, property_names)
        
        # Filter out successful results and extract URLs
        property_urls = [url for _, url in results if url]
        print(f"✅ Successfully found {len(property_urls)} property URLs")
        
        return property_urls
        
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        return None

async def main():
    """
    Main function to run the real estate listings processor
    """
    # Get the listings URL from user
    print("=== Real Estate Listings URL Extractor ===")
    listings_url = input("\nEnter the listings page URL (e.g., https://foresitecre.com/investment-sales/): ").strip()
    
    if not listings_url:
        print("❌ No URL provided")
        return
    
    # Process the listings
    property_urls = await process_real_estate_listings(listings_url)
    
    # Print results
    if property_urls:
        print("\n=== Final Results ===")
        print(f"Found {len(property_urls)} property URLs:")
        for i, url in enumerate(property_urls, 1):
            print(f"{i}. {url}")
    else:
        print("\n❌ No property URLs were found")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("Companies", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Run the main function
    asyncio.run(main()) 