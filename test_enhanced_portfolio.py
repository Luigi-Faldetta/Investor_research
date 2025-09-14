#!/usr/bin/env python3
"""
Test script for enhanced portfolio companies with website and stock links
"""
import requests
import json

def test_enhanced_portfolio():
    """Test the full system with enhanced portfolio links"""
    print("🧪 Testing Enhanced Portfolio System")
    print("=" * 50)
    
    try:
        print("📡 Making API request for Marc Andreessen...")
        response = requests.post(
            "http://localhost:5001/research",
            data={"investor_name": "Marc Andreessen"},
            timeout=120  # Longer timeout for link enhancement
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                portfolio = data.get("portfolio", [])
                
                print("✅ API Response Success")
                print(f"💼 Found {len(portfolio)} portfolio companies")
                
                # Check if companies have enhanced links
                companies_with_links = 0
                companies_with_stock = 0
                
                print("\n📊 Portfolio Company Links:")
                print("-" * 60)
                
                for i, company in enumerate(portfolio[:5], 1):  # Show first 5
                    name = company.get('name', 'Unknown')
                    website = company.get('website', '')
                    stock = company.get('stock_symbol', '')
                    yahoo_url = company.get('yahoo_finance_url', '')
                    
                    print(f"\n{i}. 🏢 {name}")
                    print(f"   📂 Sector: {company.get('sector', 'Unknown')}")
                    
                    if website:
                        companies_with_links += 1
                        print(f"   🌐 Website: {website}")
                    else:
                        print(f"   🌐 Website: Not found")
                    
                    if stock and yahoo_url:
                        companies_with_stock += 1
                        print(f"   📈 Stock: {stock}")
                        print(f"   💹 Yahoo Finance: {yahoo_url}")
                    else:
                        print(f"   📈 Stock: Not public/found")
                
                print(f"\n📈 Enhancement Summary:")
                print(f"   🌐 Companies with websites: {companies_with_links}/{len(portfolio[:5])}")
                print(f"   📊 Companies with stock info: {companies_with_stock}/{len(portfolio[:5])}")
                
                # Test if enhanced data structure is correct
                if portfolio:
                    first_company = portfolio[0]
                    required_fields = ['name', 'sector', 'stage', 'investment_date', 'description', 'website', 'stock_symbol', 'yahoo_finance_url']
                    missing_fields = [field for field in required_fields if field not in first_company]
                    
                    if missing_fields:
                        print(f"❌ Missing fields in portfolio data: {missing_fields}")
                    else:
                        print("✅ Portfolio data structure is correct!")
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_enhanced_portfolio()