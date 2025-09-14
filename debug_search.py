#!/usr/bin/env python3
"""
Debug script to test Tavily search functionality
"""
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

def test_tavily_search():
    """Test Tavily search with different queries"""
    try:
        search = TavilySearch()
        
        # Test queries
        test_queries = [
            "Marc Andreessen portfolio companies",
            "Andreessen Horowitz investments list",
            "a16z portfolio companies 2024",
            "Marc Andreessen invested in Coinbase Facebook",
            "site:crunchbase.com Marc Andreessen"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: {query}")
            print("-" * 50)
            
            try:
                results = search.run(query)
                print(f"✅ Results type: {type(results)}")
                print(f"✅ Results length: {len(results) if results else 0}")
                
                if results:
                    # Handle different result types
                    if isinstance(results, list):
                        print(f"✅ List of {len(results)} results")
                        for i, result in enumerate(results[:2]):  # Show first 2
                            print(f"  Result {i+1}: {type(result)} - {str(result)[:100]}...")
                    else:
                        results_str = str(results)
                        print(f"✅ First 200 chars: {results_str[:200]}...")
                        # Check if results mention companies
                        companies = ["Coinbase", "Facebook", "Instagram", "Airbnb", "Uber", "Twitter"]
                        mentioned = [c for c in companies if c.lower() in results_str.lower()]
                        if mentioned:
                            print(f"✅ Companies mentioned: {mentioned}")
                else:
                    print("❌ No results returned")
                    
            except Exception as e:
                print(f"❌ Search error: {e}")
            
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"❌ Tavily setup error: {e}")

if __name__ == "__main__":
    test_tavily_search()