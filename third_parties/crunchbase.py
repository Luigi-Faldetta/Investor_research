import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def fetch_portfolio_data(investor_name: str, mock: bool = False) -> List[Dict]:
    """
    Fetch portfolio data from Crunchbase.
    """
    if mock:
        # Return mock portfolio data
        return [
            {
                "company": "Example Startup",
                "funding_round": "Series A",
                "amount": "$10M",
                "date": "2023-12-01",
                "sector": "SaaS"
            }
        ]
    
    # Real implementation would use Crunchbase API
    # api_key = os.environ.get("CRUNCHBASE_API_KEY")
    # Would fetch real portfolio data here
    
    return []