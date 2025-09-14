"""
Wikipedia image search and dynamic Cloudinary upload
"""
import requests
import re
from typing import Optional, List
from urllib.parse import unquote
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


def search_wikipedia_image(person_name: str) -> Optional[str]:
    """
    Search for a person's image on Wikipedia and return the best image URL
    """
    try:
        # Step 1: Search Wikipedia for the person
        search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + person_name.replace(" ", "_")
        
        headers = {
            'User-Agent': 'InvestorResearch/1.0 (https://github.com/user/investor-research) Contact: user@example.com'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if there's a thumbnail (main image)
            if 'thumbnail' in data and 'source' in data['thumbnail']:
                image_url = data['thumbnail']['source']
                
                # Get higher resolution version
                # Wikipedia thumbnails often have resolution in URL like /320px-image.jpg
                # We can replace with higher res
                high_res_url = re.sub(r'/\d+px-', '/800px-', image_url)
                
                print(f"📸 Found Wikipedia image: {high_res_url}")
                return high_res_url
        
        # Step 2: If summary doesn't have image, try searching Wikipedia images directly
        search_query = f"{person_name} investor entrepreneur"
        return search_wikipedia_images_api(search_query)
        
    except Exception as e:
        print(f"Wikipedia search error for {person_name}: {e}")
        return None


def search_wikipedia_images_api(query: str) -> Optional[str]:
    """
    Search Wikipedia Commons for images using the API
    """
    try:
        # Use Wikipedia Commons API to search for images
        api_url = "https://commons.wikimedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srnamespace': '6',  # File namespace
            'srlimit': '10'
        }
        
        headers = {
            'User-Agent': 'InvestorResearch/1.0 (https://github.com/user/investor-research)'
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'query' in data and 'search' in data['query']:
                for result in data['query']['search'][:3]:  # Try first 3 results
                    filename = result['title']
                    
                    # Get the actual image URL
                    image_url = get_wikimedia_image_url(filename)
                    if image_url and is_valid_portrait_image(image_url, filename):
                        print(f"📸 Found Commons image: {image_url}")
                        return image_url
        
        return None
        
    except Exception as e:
        print(f"Commons search error: {e}")
        return None


def get_wikimedia_image_url(filename: str) -> Optional[str]:
    """
    Get the direct URL for a Wikimedia image file
    """
    try:
        api_url = "https://commons.wikimedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'titles': filename,
            'prop': 'imageinfo',
            'iiprop': 'url',
            'iiurlwidth': '400'  # Get 400px wide version
        }
        
        headers = {
            'User-Agent': 'InvestorResearch/1.0'
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'imageinfo' in page_data and len(page_data['imageinfo']) > 0:
                    image_info = page_data['imageinfo'][0]
                    # Prefer thumb URL if available, otherwise use full URL
                    return image_info.get('thumburl') or image_info.get('url')
        
        return None
        
    except Exception as e:
        print(f"Image URL fetch error: {e}")
        return None


def is_valid_portrait_image(image_url: str, filename: str) -> bool:
    """
    Check if this looks like a good portrait image based on filename and URL
    """
    filename_lower = filename.lower()
    
    # Skip obvious non-portrait images
    skip_terms = ['logo', 'graph', 'chart', 'diagram', 'screenshot', 'building', 'company']
    if any(term in filename_lower for term in skip_terms):
        return False
    
    # Prefer images that likely contain portraits
    good_terms = ['portrait', 'headshot', 'photo', '.jpg', 'cropped']
    if any(term in filename_lower for term in good_terms):
        return True
    
    # Test if the image is accessible
    try:
        response = requests.head(image_url, timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_to_cloudinary_dynamic(investor_name: str, image_url: str) -> Optional[str]:
    """
    Upload an image to Cloudinary with dynamic processing
    """
    try:
        sanitized_name = investor_name.lower().replace(' ', '_').replace('-', '_')
        
        print(f"📤 Uploading {investor_name} to Cloudinary...")
        
        # Upload to Cloudinary with optimization
        result = cloudinary.uploader.upload(
            image_url,
            public_id=f"investors/dynamic/{sanitized_name}",
            folder="investors/dynamic",
            overwrite=True,
            quality="auto",
            fetch_format="auto",
            width=400,
            height=400,
            crop="fill",
            gravity="face",  # Focus on face when cropping
            transformation=[
                {"quality": "auto"},
                {"fetch_format": "auto"}
            ]
        )
        
        cloudinary_url = result['secure_url']
        print(f"✅ Uploaded successfully: {cloudinary_url}")
        
        # Verify the upload worked
        test_response = requests.head(cloudinary_url, timeout=5)
        if test_response.status_code == 200:
            return cloudinary_url
        else:
            print(f"❌ Upload verification failed")
            return None
            
    except Exception as e:
        print(f"❌ Cloudinary upload failed: {e}")
        return None


def get_dynamic_investor_image(investor_name: str) -> Optional[str]:
    """
    Complete workflow: Search Wikipedia -> Upload to Cloudinary -> Return URL
    """
    print(f"🔍 Starting dynamic image search for: {investor_name}")
    
    # Step 1: Check if we already have this image in Cloudinary
    sanitized_name = investor_name.lower().replace(' ', '_').replace('-', '_')
    
    try:
        # Check dynamic folder first
        result = cloudinary.api.resource(f"investors/dynamic/{sanitized_name}")
        existing_url = result['secure_url']
        print(f"✅ Found existing Cloudinary image: {existing_url}")
        return existing_url
    except:
        pass  # Image doesn't exist yet, continue with search
    
    # Step 2: Search Wikipedia for image
    wikipedia_url = search_wikipedia_image(investor_name)
    
    if not wikipedia_url:
        print(f"❌ No Wikipedia image found for {investor_name}")
        return None
    
    # Step 3: Upload to Cloudinary
    cloudinary_url = upload_to_cloudinary_dynamic(investor_name, wikipedia_url)
    
    if cloudinary_url:
        print(f"🎉 Dynamic workflow complete for {investor_name}")
        return cloudinary_url
    else:
        print(f"❌ Dynamic workflow failed for {investor_name}")
        return None


def test_dynamic_workflow():
    """
    Test the dynamic workflow with various investors
    """
    test_investors = [
        "Mark Cuban",
        "Naval Ravikant", 
        "Reid Hoffman",
        "Balaji Srinivasan",
        "Cathie Wood"
    ]
    
    print("🧪 Testing Dynamic Wikipedia -> Cloudinary Workflow")
    print("=" * 60)
    
    for investor in test_investors:
        print(f"\n👤 Testing: {investor}")
        print("-" * 40)
        
        url = get_dynamic_investor_image(investor)
        if url:
            print(f"✅ Success: {url}")
        else:
            print(f"❌ Failed: {investor}")
        
        print()


if __name__ == "__main__":
    test_dynamic_workflow()