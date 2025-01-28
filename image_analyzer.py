import base64
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List
from pathlib import Path
import time

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def encode_image(image_path):
    """Function to encode the image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_paths(folder_path: str) -> List[str]:
    """
    Get paths of all image files in the specified folder, sorted by screenshot number
    
    Args:
        folder_path: Path to folder containing images
    Returns:
        List of image file paths, sorted numerically by screenshot number
    """
    image_extensions = ('.png', '.jpg', '.jpeg')
    folder = Path(folder_path)
    
    # Get all image files and sort them by the number in their filename
    image_files = [f for f in folder.glob('*') if f.suffix.lower() in image_extensions]
    
    # Sort based on the number in "screenshot_X.png"
    def get_screenshot_number(filepath):
        filename = filepath.stem  # Get filename without extension
        try:
            return int(filename.split('_')[1])  # Extract number after underscore
        except (IndexError, ValueError):
            return float('inf')  # Put invalid names at the end
    
    sorted_files = sorted(image_files, key=get_screenshot_number)
    return [str(f) for f in sorted_files]


def analyze_real_estate_images(folder_path: str) -> List[str]:
    """
    Analyze all real estate listing screenshots in a folder to extract property names
    
    Args:
        folder_path: Path to folder containing screenshot images
    Returns:
        List of property names in order of appearance
    """
    print(f"\n🔍 Analyzing screenshots in folder: {folder_path}")
    
    # Get all image paths from the folder
    image_paths = get_image_paths(folder_path)
    
    if not image_paths:
        raise ValueError(f"No image files found in {folder_path}")
    
    print(f"\n📸 Found {len(image_paths)} screenshots to analyze:")
    for idx, path in enumerate(image_paths, 1):
        print(f"  {idx}. {os.path.basename(path)}")
    
    print("\n🔄 Preparing images for analysis...")
    
    # Updated prompt for specific format
    message_content = [
        {
            "type": "text",
            "text": """Analyze these real estate listing screenshots and list ALL properties in order of appearance.
            
Format your response EXACTLY like this, with one property per line, starting with a hyphen:
- Property Name 1
- Property Name 2 (123 Main St)
- Property Name 3
- Property Name 2 (456 Oak Ave)

Rules:
1. Start each line with "- "
2. If properties have the same name, add unique identifying info in parentheses
3. No extra text or explanations - just the list
4. No blank lines between properties
5. No numbering, just hyphens"""
        }
    ]
    
    # Add each image to the message content
    for image_path in image_paths:
        base64_image = encode_image(image_path)
        message_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    print("\n🚀 Sending request to OpenAI...")
    print("⏳ Waiting for response (this may take a minute)...")
    start_time = time.time()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": message_content
            }
        ],
        max_tokens=1000
    )
    
    end_time = time.time()
    processing_time = round(end_time - start_time, 2)
    print(f"\n✅ Response received! (took {processing_time} seconds)")
    
    # Parse the response into a list
    raw_response = response.choices[0].message.content
    
    # Convert the response to a list by splitting on newlines and cleaning up
    property_list = [
        line[2:].strip()  # Remove "- " prefix and any whitespace
        for line in raw_response.split('\n')
        if line.strip().startswith('-')  # Only include lines starting with hyphen
    ]
    
    # Print formatted results
    print("\n📋 Property Names Found:")
    for idx, prop in enumerate(property_list, 1):
        print(f"{idx}. {prop}")
    
    return property_list


if __name__ == "__main__":
    # Example usage when run directly
    screenshots_folder = "levyretail/"
    try:
        properties = analyze_real_estate_images(screenshots_folder)
        print(f"\nReturned value:")
        print(properties)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")