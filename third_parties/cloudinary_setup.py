"""
Cloudinary setup and photo management for investor headshots
"""
import os
import requests
from typing import Optional, Dict, List
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import time
from urllib.parse import urlparse

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


def setup_cloudinary() -> bool:
    """
    Verify Cloudinary configuration is working
    """
    try:
        # Test connection by getting cloud usage
        result = cloudinary.api.usage()
        print(f"✅ Cloudinary connected successfully")
        print(f"📊 Storage used: {result.get('storage', {}).get('used_bytes', 0)} bytes")
        return True
    except Exception as e:
        print(f"❌ Cloudinary setup failed: {e}")
        print("\n📝 Setup instructions:")
        print("1. Sign up at https://cloudinary.com")
        print("2. Get your credentials from the dashboard")
        print("3. Add to .env file:")
        print("   CLOUDINARY_CLOUD_NAME=your_cloud_name")
        print("   CLOUDINARY_API_KEY=your_api_key")
        print("   CLOUDINARY_API_SECRET=your_api_secret")
        return False


def get_high_quality_investor_photos() -> Dict[str, List[str]]:
    """
    Curated collection of high-quality investor photo URLs
    Using reliable Wikipedia images that are stable and accessible
    """
    return {
        "marc_andreessen": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Marc_Andreessen-9_%28cropped%29.jpg/500px-Marc_Andreessen-9_%28cropped%29.jpg"
        ],
        "mark_cuban": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Mark_Cuban_2017.jpg/400px-Mark_Cuban_2017.jpg"
        ],
        "peter_thiel": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Peter_Thiel_TechCrunch50.jpg/400px-Peter_Thiel_TechCrunch50.jpg"
        ],
        "naval_ravikant": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Naval_Ravikant_cropped.jpg/400px-Naval_Ravikant_cropped.jpg"
        ],
        "reid_hoffman": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Reid_Hoffman_Web_2.0_Conference.jpg/400px-Reid_Hoffman_Web_2.0_Conference.jpg"
        ],
        "balaji_srinivasan": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Balaji_Srinivasan_2017.jpg/400px-Balaji_Srinivasan_2017.jpg"
        ]
    }


def download_and_upload_photo(investor_name: str, photo_urls: List[str]) -> Optional[str]:
    """
    Download a photo and upload it to Cloudinary
    Returns the Cloudinary URL if successful
    """
    sanitized_name = investor_name.lower().replace(' ', '_').replace('-', '_')
    
    for i, url in enumerate(photo_urls):
        try:
            print(f"📥 Downloading photo for {investor_name} (attempt {i+1}/{len(photo_urls)})")
            print(f"   Source: {url[:60]}...")
            
            # Download the image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, stream=True)
            response.raise_for_status()
            
            # Verify it's an image
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type:
                print(f"   ❌ Not an image: {content_type}")
                continue
                
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                url,
                public_id=f"investors/{sanitized_name}",
                folder="investors",
                overwrite=True,
                quality="auto",
                fetch_format="auto",
                width=400,
                height=400,
                crop="fill",
                gravity="face"  # Focus on face when cropping
            )
            
            cloudinary_url = result['secure_url']
            print(f"   ✅ Uploaded successfully: {cloudinary_url}")
            
            # Test the uploaded URL
            test_response = requests.head(cloudinary_url, timeout=5)
            if test_response.status_code == 200:
                return cloudinary_url
            else:
                print(f"   ❌ Upload verification failed")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    print(f"❌ All photo uploads failed for {investor_name}")
    return None


def upload_all_investor_photos() -> Dict[str, str]:
    """
    Upload all investor photos to Cloudinary
    Returns a mapping of investor names to Cloudinary URLs
    """
    if not setup_cloudinary():
        return {}
    
    photos = get_high_quality_investor_photos()
    cloudinary_urls = {}
    
    print(f"\n🚀 Starting photo upload for {len(photos)} investors...")
    print("=" * 60)
    
    for investor_key, photo_urls in photos.items():
        # Convert key to display name
        display_name = investor_key.replace('_', ' ').title()
        
        print(f"\n👤 Processing: {display_name}")
        print("-" * 40)
        
        cloudinary_url = download_and_upload_photo(display_name, photo_urls)
        
        if cloudinary_url:
            cloudinary_urls[investor_key] = cloudinary_url
            # Also store with display name format
            cloudinary_urls[display_name.lower()] = cloudinary_url
            print(f"✅ Success: {display_name}")
        else:
            print(f"❌ Failed: {display_name}")
        
        # Small delay to be respectful
        time.sleep(1)
    
    print(f"\n📊 Upload Summary:")
    print(f"   Success: {len(cloudinary_urls)}")
    print(f"   Failed: {len(photos) - len(cloudinary_urls)}")
    
    return cloudinary_urls


def get_cloudinary_url(investor_name: str) -> Optional[str]:
    """
    Get the Cloudinary URL for an investor
    """
    sanitized_name = investor_name.lower().replace(' ', '_').replace('-', '_')
    
    try:
        # Try to get the image from Cloudinary (check both possible paths)
        try:
            result = cloudinary.api.resource(f"investors/investors/{sanitized_name}")
            return result['secure_url']
        except:
            result = cloudinary.api.resource(f"investors/{sanitized_name}")
            return result['secure_url']
    except:
        return None


def list_uploaded_photos() -> List[Dict]:
    """
    List all photos uploaded to the investors folder
    """
    try:
        result = cloudinary.api.resources(
            type="upload",
            prefix="investors/",
            max_results=100
        )
        
        photos = []
        for resource in result.get('resources', []):
            photos.append({
                'public_id': resource['public_id'],
                'url': resource['secure_url'],
                'created': resource['created_at'],
                'bytes': resource['bytes']
            })
        
        return photos
    except Exception as e:
        print(f"Error listing photos: {e}")
        return []


if __name__ == "__main__":
    print("🖼️  Cloudinary Investor Photo Setup")
    print("=" * 50)
    
    # Test connection
    if setup_cloudinary():
        
        # Ask user what they want to do
        print("\nWhat would you like to do?")
        print("1. Upload all investor photos")
        print("2. List existing photos")
        print("3. Test photo retrieval")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            urls = upload_all_investor_photos()
            print(f"\n✅ Uploaded {len(urls)} photos to Cloudinary")
            
        elif choice == "2":
            photos = list_uploaded_photos()
            print(f"\n📋 Found {len(photos)} photos:")
            for photo in photos:
                name = photo['public_id'].replace('investors/', '').replace('_', ' ')
                print(f"   👤 {name.title()}: {photo['url']}")
                
        elif choice == "3":
            test_name = input("Enter investor name to test: ").strip()
            url = get_cloudinary_url(test_name)
            if url:
                print(f"✅ Found: {url}")
            else:
                print(f"❌ Not found: {test_name}")