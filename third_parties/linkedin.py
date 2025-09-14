import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def fetch_linkedin_posts(linkedin_url: str, mock: bool = False) -> List[Dict]:
    """
    Fetch recent LinkedIn posts from a profile.
    """
    if mock:
        # Return mock LinkedIn posts for testing
        return [
            {
                "content": "Exciting to announce our latest investment in quantum computing. This technology will revolutionize drug discovery and materials science in ways we're just beginning to understand. Proud to back this exceptional team.",
                "date": "2024-01-15",
                "reactions": 456
            },
            {
                "content": "Reflections on 2023: We saw the emergence of AI as a platform shift comparable to mobile and cloud. In 2024, we're focused on backing founders building the infrastructure layer for this new era.",
                "date": "2024-01-10",
                "reactions": 892
            },
            {
                "content": "The best founders aren't just building products; they're building movements. They have a vision for how the world should be different and the conviction to make it happen.",
                "date": "2024-01-05",
                "reactions": 1234
            }
        ]
    
    # Real implementation - for now return empty list if no API key
    print(f"LinkedIn API not configured, returning empty posts for {linkedin_url}")
    return []