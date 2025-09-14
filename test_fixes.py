#!/usr/bin/env python3
"""
Test script to verify profile image and Medium integration
"""
from agents.investor_lookup_agent import lookup
from third_parties.medium import fetch_medium_articles

def test_profile_image():
    """Test profile image extraction"""
    print("🖼️  Testing Profile Image Extraction")
    print("-" * 40)
    
    test_names = ["Marc Andreessen", "Mark Cuban", "Peter Thiel"]
    
    for name in test_names:
        profile = lookup(name, use_mock=False)
        print(f"✅ {name}:")
        print(f"   Image: {profile.get('image', 'No image')[:60]}...")
        print(f"   Firm: {profile.get('firm', 'No firm')}")
        print()

def test_medium_integration():
    """Test Medium API integration"""
    print("📝 Testing Medium API Integration")
    print("-" * 40)
    
    # Test with known Medium users
    test_urls = [
        "https://medium.com/@pmarca",
        "https://medium.com/@naval",
        "https://medium.com/@balajis"
    ]
    
    for url in test_urls:
        print(f"Testing: {url}")
        articles = fetch_medium_articles(url, mock=False)
        print(f"✅ Found {len(articles)} articles")
        if articles:
            print(f"   Latest: {articles[0].get('title', 'No title')[:50]}...")
        print()

if __name__ == "__main__":
    test_profile_image()
    test_medium_integration()