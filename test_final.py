#!/usr/bin/env python3
"""
Final test to verify both image and Medium article fixes
"""
import requests
import json

def test_api_endpoint():
    """Test the Flask API endpoint"""
    print("🧪 Testing Flask API with Marc Andreessen")
    print("-" * 50)
    
    try:
        # Test the API endpoint
        response = requests.post(
            "http://localhost:5001/research",
            data={"investor_name": "Marc Andreessen"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                profile = data["profile"]
                medium_articles = data.get("medium_articles", [])
                
                print("✅ API Response Success")
                print(f"📸 Profile Image: {profile.get('profile_image', 'None')[:50]}...")
                print(f"📝 Medium Articles: {len(medium_articles)} found")
                
                if medium_articles:
                    print("📄 Sample Article:")
                    article = medium_articles[0]
                    print(f"   Title: {article.get('title', 'No title')[:50]}...")
                    print(f"   Date: {article.get('date', 'No date')}")
                    
                print(f"🏢 Portfolio Companies: {len(data.get('portfolio', []))}")
                
                # Show first few companies
                portfolio = data.get("portfolio", [])
                if portfolio:
                    print("💼 Sample Companies:")
                    for company in portfolio[:3]:
                        print(f"   - {company.get('name', 'Unknown')} ({company.get('sector', 'Unknown')})")
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_api_endpoint()