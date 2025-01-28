from playwright.sync_api import sync_playwright
import os
from urllib.parse import urlparse
from typing import List

def create_directory(url: str) -> str:
    """
    Creates nested directory structure: Companies/domain_name/
    
    Args:
        url: Website URL to create folder for
    Returns:
        Path to the created directory
    """
    # Parse the domain name from the URL and remove www if present
    domain = urlparse(url).netloc.replace('www.', '').split('.')[0]
    
    # Create main Companies directory if it doesn't exist
    if not os.path.exists("Companies"):
        os.makedirs("Companies")
    
    # Create company-specific directory inside Companies
    company_dir = os.path.join("Companies", domain)
    if not os.path.exists(company_dir):
        os.makedirs(company_dir)
    
    return company_dir

def capture_viewport_screenshots(url: str) -> List[str]:
    """
    Captures viewport-by-viewport screenshots of a webpage with overlap
    
    Args:
        url (str): The URL of the webpage to screenshot
        
    Returns:
        List[str]: List of paths to the generated screenshot files
    """
    screenshot_paths = []
    
    with sync_playwright() as p:
        # Launch browser in headed mode (visible)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to URL and wait fixed time
        page.goto(url)
        page.wait_for_timeout(7000)  # Wait 7 seconds for initial load
        
        # Get page dimensions
        page_height = page.evaluate('document.documentElement.scrollHeight')
        viewport_height = page.viewport_size['height']
        
        # Create directory for screenshots
        save_dir = create_directory(url)
        
        # Take screenshots viewport by viewport
        current_scroll = 0
        screenshot_count = 0
        
        # Reduce scroll step to create overlap
        scroll_step = int(viewport_height * 0.8)  # 20% overlap
        
        while current_scroll < page_height:
            # Smooth scroll to position
            page.evaluate('''
                (scrollTo) => {
                    window.scrollTo({
                        top: scrollTo,
                        behavior: 'smooth'
                    });
                }
            ''', current_scroll)
            
            # Wait for scroll and content to load
            page.wait_for_timeout(3000)  # Wait 3 seconds after scroll
            
            # Scroll a tiny bit more to trigger any remaining lazy load
            page.evaluate('window.scrollBy(0, 150)')
            page.wait_for_timeout(2000)  # Wait 2 seconds after jiggle
            
            # Scroll back to the correct position
            page.evaluate(f'window.scrollTo(0, {current_scroll})')
            page.wait_for_timeout(1000)  # Wait 1 second after repositioning
            
            # Take screenshot of current viewport
            screenshot_path = os.path.abspath(f"{save_dir}/screenshot_{screenshot_count}.png")
            page.screenshot(path=screenshot_path, full_page=False)
            screenshot_paths.append(screenshot_path)
            
            # Update scroll position for next iteration with overlap
            current_scroll += scroll_step
            screenshot_count += 1
            
            # Update page height in case it changed due to dynamic content
            new_height = page.evaluate('document.documentElement.scrollHeight')
            if new_height > page_height:
                page_height = new_height
        
        # Take one final screenshot at the bottom to ensure we didn't miss anything
        page.evaluate(f'window.scrollTo(0, {page_height})')
        page.wait_for_timeout(3000)  # Wait 3 seconds before final screenshot
        screenshot_path = os.path.abspath(f"{save_dir}/screenshot_{screenshot_count}.png")
        page.screenshot(path=screenshot_path, full_page=False)
        screenshot_paths.append(screenshot_path)
        
        browser.close()
    
    return screenshot_paths

# Example usage:
if __name__ == "__main__":
    paths = capture_viewport_screenshots("https://foresitecre.com/investment-sales/")
    print("Screenshots saved to:", paths) 