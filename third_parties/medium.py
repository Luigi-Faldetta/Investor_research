import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def fetch_medium_articles(medium_url: str, mock: bool = False, investor_name: str = "") -> List[Dict]:
    """
    Fetch Medium articles ABOUT an investor (not BY them).
    Now searches for articles mentioning the investor rather than written by them.
    """
    if mock:
        # Return mock Medium articles for testing
        return [
            {
                "title": "The End of Software as We Know It",
                "excerpt": "AI is not just another tool in the software development toolkit. It represents a fundamental shift in how we create, deploy, and maintain software systems...",
                "date": "2024-01-12",
                "read_time": "8 min",
                "claps": 3421
            },
            {
                "title": "Why We're Investing in Climate Tech Now",
                "excerpt": "The convergence of AI, IoT, and renewable energy has created an unprecedented opportunity for innovation in climate technology...",
                "date": "2023-12-28",
                "read_time": "6 min",
                "claps": 2156
            },
            {
                "title": "The Next Platform Shift: Thoughts on Spatial Computing",
                "excerpt": "As we move beyond screens into spatial computing, we're seeing the early signs of a platform shift as significant as the transition from desktop to mobile...",
                "date": "2023-12-15",
                "read_time": "10 min",
                "claps": 1892
            }
        ]
    
    # Real implementation - search for articles ABOUT the investor
    try:
        # Import the new article fetcher
        from .medium_articles import fetch_medium_articles_about
        
        # If investor_name is provided, use that, otherwise try to extract from URL
        if not investor_name and medium_url:
            # Try to extract investor name from URL context
            investor_name = "the investor"
        
        if investor_name:
            print(f"Fetching Medium articles about: {investor_name}")
            return fetch_medium_articles_about(investor_name, limit=5)
        
        # Try Medium RSS feed (free method)
        rss_url = f"https://medium.com/feed/@{username}"
        
        response = requests.get(rss_url, timeout=10)
        
        if response.status_code == 200:
            # Parse RSS XML
            import xml.etree.ElementTree as ET
            
            try:
                root = ET.fromstring(response.content)
                articles = []
                
                # Find all items in the RSS feed
                for item in root.findall('.//item')[:5]:  # Limit to 5 most recent
                    title = item.find('title')
                    description = item.find('description') 
                    pub_date = item.find('pubDate')
                    link = item.find('link')
                    
                    # Extract text content
                    title_text = title.text if title is not None else "Untitled"
                    desc_text = description.text if description is not None else ""
                    
                    # Clean description (remove HTML tags)
                    import re
                    clean_desc = re.sub(r'<[^>]+>', '', desc_text)[:200] + "..."
                    
                    # Parse date
                    date_text = "2024"
                    if pub_date is not None and pub_date.text:
                        try:
                            from datetime import datetime
                            parsed_date = datetime.strptime(pub_date.text, '%a, %d %b %Y %H:%M:%S %Z')
                            date_text = parsed_date.strftime('%Y-%m-%d')
                        except:
                            date_text = pub_date.text[:10] if len(pub_date.text) > 10 else "2024"
                    
                    articles.append({
                        "title": title_text,
                        "excerpt": clean_desc,
                        "date": date_text,
                        "read_time": "5 min",  # Estimate
                        "claps": 0,  # Not available in RSS
                        "url": link.text if link is not None else ""
                    })
                
                print(f"Successfully fetched {len(articles)} Medium articles via RSS")
                return articles
                
            except ET.ParseError as e:
                print(f"RSS parsing error: {e}")
                return []
                
        else:
            print(f"Medium RSS error: {response.status_code}")
            
            # Fallback: try RapidAPI if available
            api_key = os.environ.get("MEDIUM_API_KEY")
            if api_key:
                print("Trying RapidAPI as fallback...")
                return fetch_via_rapidapi(username, api_key)
            
            return []
            
    except Exception as e:
        print(f"Error fetching Medium articles: {e}")
        return []


def fetch_via_rapidapi(username: str, api_key: str) -> List[Dict]:
    """Fallback method using RapidAPI"""
    try:
        # RapidAPI Medium API endpoint
        url = "https://medium2.p.rapidapi.com/user/articles"
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "medium2.p.rapidapi.com"
        }
        
        params = {
            "user_id": username,
            "count": 10
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = []
            
            if isinstance(data, dict) and "articles" in data:
                for article in data["articles"][:5]:
                    articles.append({
                        "title": article.get("title", "Untitled"),
                        "excerpt": article.get("subtitle", "")[:200] + "...",
                        "date": article.get("published_at", "2024"),
                        "read_time": f"{article.get('reading_time', 5)} min",
                        "claps": article.get("claps", 0),
                        "url": article.get("url", "")
                    })
            
            return articles
        else:
            print(f"RapidAPI error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"RapidAPI fallback error: {e}")
        return []