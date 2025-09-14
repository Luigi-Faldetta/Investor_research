"""
Image search and management for investor photos
"""
import os
import requests
from typing import Optional
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

# Import Cloudinary functionality
try:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from cloudinary_setup import get_cloudinary_url, setup_cloudinary
    from wikipedia_images import get_dynamic_investor_image
    CLOUDINARY_AVAILABLE = True
    DYNAMIC_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Cloudinary import failed: {e}")
    CLOUDINARY_AVAILABLE = False
    DYNAMIC_SEARCH_AVAILABLE = False


def search_investor_image(investor_name: str, firm: str = "") -> Optional[str]:
    """
    Search for investor images using multiple strategies with dynamic Wikipedia integration
    """
    
    # Strategy 1: Try existing Cloudinary images first (fastest)
    if CLOUDINARY_AVAILABLE:
        try:
            cloudinary_url = get_cloudinary_url(investor_name)
            if cloudinary_url and verify_image_url(cloudinary_url):
                print(f"✅ Found existing Cloudinary image: {cloudinary_url}")
                return cloudinary_url
        except Exception as e:
            print(f"Cloudinary search error: {e}")
    
    # Strategy 2: Dynamic Wikipedia -> Cloudinary workflow (NEW!)
    if DYNAMIC_SEARCH_AVAILABLE:
        try:
            dynamic_url = get_dynamic_investor_image(investor_name)
            if dynamic_url and verify_image_url(dynamic_url):
                print(f"🎉 Found/created dynamic image: {dynamic_url}")
                return dynamic_url
        except Exception as e:
            print(f"Dynamic search error: {e}")
    
    # Strategy 3: Try curated/known good URLs
    curated_images = get_curated_images()
    if investor_name.lower() in curated_images:
        urls = curated_images[investor_name.lower()]
        if isinstance(urls, str):
            urls = [urls]
        
        # Try each URL until one works
        for image_url in urls:
            if verify_image_url(image_url):
                print(f"Found working curated image: {image_url}")
                return image_url
    
    # Strategy 4: Use Tavily to search for images
    try:
        search = TavilySearch()
        query = f'"{investor_name}" {firm} professional headshot photo'
        results = search.run(query, include_images=True)
        
        if isinstance(results, dict) and 'images' in results:
            for image in results['images'][:3]:  # Try first 3 images
                image_url = image.get('url', '')
                if image_url and verify_image_url(image_url):
                    print(f"Found image via Tavily: {image_url}")
                    return image_url
                    
    except Exception as e:
        print(f"Tavily image search error: {e}")
    
    # Strategy 5: Generate professional avatar as fallback
    return f"https://ui-avatars.com/api/?name={investor_name.replace(' ', '+')}&size=300&background=4A90E2&color=fff&bold=true&format=png"


def get_curated_images() -> dict:
    """
    Curated collection of working investor image URLs
    Using reliable CDNs and services that don't break
    """
    return {
        # Strategy: Use multiple reliable sources
        
        # Marc Andreessen - Use a combination of sources
        "marc andreessen": [
            "https://cdn.mos.cms.futurecdn.net/J8YZ2K8dZYx8Q7K4P6M3MR.jpg",  # Professional headshot
            "https://techcrunch.com/wp-content/uploads/2015/06/shutterstock_247224075.jpg",  # TechCrunch
            "https://ui-avatars.com/api/?name=Marc+Andreessen&size=300&background=2563eb&color=fff&bold=true"  # Fallback
        ],
        
        # Mark Cuban
        "mark cuban": [
            "https://specials-images.forbesimg.com/imageserve/5f469cb85cc82c0015260e07/0x0.jpg",  # Forbes
            "https://ui-avatars.com/api/?name=Mark+Cuban&size=300&background=dc2626&color=fff&bold=true"
        ],
        
        # Peter Thiel  
        "peter thiel": [
            "https://spectrum.ieee.org/media-library/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.jpg",
            "https://ui-avatars.com/api/?name=Peter+Thiel&size=300&background=7c3aed&color=fff&bold=true"
        ],
        
        # Naval Ravikant
        "naval ravikant": [
            "https://ui-avatars.com/api/?name=Naval+Ravikant&size=300&background=059669&color=fff&bold=true"
        ],
        
        # Reid Hoffman
        "reid hoffman": [
            "https://ui-avatars.com/api/?name=Reid+Hoffman&size=300&background=0369a1&color=fff&bold=true"
        ],
        
        # Balaji Srinivasan
        "balaji srinivasan": [
            "https://ui-avatars.com/api/?name=Balaji+Srinivasan&size=300&background=b91c1c&color=fff&bold=true"
        ]
    }


def verify_image_url(url: str, timeout: int = 5) -> bool:
    """
    Verify that an image URL is accessible and returns an actual image
    """
    try:
        response = requests.head(url, timeout=timeout)
        return (response.status_code == 200 and 
                'image' in response.headers.get('content-type', '').lower())
    except:
        return False


def get_fallback_image(investor_name: str, style: str = "professional") -> str:
    """
    Generate different styles of fallback images
    """
    name_encoded = investor_name.replace(' ', '+')
    
    fallback_options = {
        "professional": f"https://ui-avatars.com/api/?name={name_encoded}&size=300&background=4A90E2&color=fff&bold=true&format=png",
        "minimal": f"https://ui-avatars.com/api/?name={name_encoded}&size=300&background=667eea&color=fff&bold=true&format=png",
        "avatar": f"https://robohash.org/{name_encoded}?size=300x300&set=set5",
        "geometric": f"https://source.boringavatars.com/beam/300/{name_encoded}?colors=264653,2a9d8f,e9c46a,f4a261,e76f51"
    }
    
    return fallback_options.get(style, fallback_options["professional"])


if __name__ == "__main__":
    # Test the function
    test_names = ["Marc Andreessen", "Naval Ravikant", "Unknown Person"]
    
    for name in test_names:
        print(f"\n🔍 Testing: {name}")
        image_url = search_investor_image(name)
        print(f"📸 Result: {image_url}")
        print(f"✅ Valid: {verify_image_url(image_url)}")