#!/usr/bin/env python3
"""
Test script to verify Cloudinary photo integration
"""
import requests
import json

def test_cloudinary_photos():
    """Test the Flask API with Cloudinary integration"""
    print("🧪 Testing Cloudinary Photo Integration")
    print("-" * 50)
    
    try:
        # Test the API endpoint
        print("📡 Making API request...")
        response = requests.post(
            "http://localhost:5001/research",
            data={"investor_name": "Marc Andreessen"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                profile = data["profile"]
                image_url = profile.get('profile_image', '')
                
                print("✅ API Response Success")
                print(f"👤 Investor: {profile.get('name', 'Unknown')}")
                print(f"🏢 Firm: {profile.get('firm', 'Unknown')}")
                print(f"📸 Image URL: {image_url}")
                
                # Check if it's a Cloudinary URL
                if 'cloudinary.com' in image_url:
                    print("🎉 SUCCESS: Using real Cloudinary photo!")
                    print(f"📍 Cloudinary URL: {image_url}")
                elif 'ui-avatars.com' in image_url:
                    print("⚠️  Still using generated avatar")
                    print(f"🔧 Debug: {image_url}")
                else:
                    print(f"❓ Unknown image source: {image_url}")
                
                # Test image accessibility
                print("\n🔍 Testing image accessibility...")
                try:
                    img_response = requests.head(image_url, timeout=10)
                    if img_response.status_code == 200:
                        print("✅ Image is accessible")
                    else:
                        print(f"❌ Image not accessible: {img_response.status_code}")
                except Exception as e:
                    print(f"❌ Image test failed: {e}")
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_cloudinary_photos()