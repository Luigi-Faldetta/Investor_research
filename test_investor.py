#!/usr/bin/env python3
"""
Test script to verify the investor research functionality
"""
from investor_research import research_investor

def test_investor_research():
    """Test the investor research functionality"""
    print("=" * 50)
    print("Testing Investor Research Assistant")
    print("=" * 50)
    
    # Test with a well-known investor
    test_names = ["Marc Andreessen", "Mark Cuban", "Peter Thiel"]
    
    for name in test_names:
        print(f"\n🔍 Testing with: {name}")
        print("-" * 30)
        
        try:
            profile, portfolio, insights = research_investor(name)
            
            print(f"✅ Profile found:")
            print(f"  - Name: {profile.name}")
            print(f"  - Firm: {profile.firm}")
            print(f"  - Title: {profile.title}")
            print(f"  - URLs: {len(profile.profile_urls)} platforms")
            
            print(f"✅ Portfolio: {len(portfolio)} companies found")
            for company in portfolio[:3]:  # Show first 3
                print(f"  - {company.name} ({company.sector})")
            
            print(f"✅ Insights generated:")
            print(f"  - Themes: {len(insights.investment_themes)}")
            print(f"  - Sectors: {len(insights.sector_focus)}")
            print(f"  - Icebreakers: {len(insights.icebreakers)}")
            
            if insights.icebreakers:
                print(f"  - Sample icebreaker: {insights.icebreakers[0][:80]}...")
                
        except Exception as e:
            print(f"❌ Error testing {name}: {e}")
        
        print()

if __name__ == "__main__":
    test_investor_research()