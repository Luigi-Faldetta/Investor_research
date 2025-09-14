"""
Smart profile finder that searches the internet to find and verify actual profile URLs
"""
import requests
import re
from typing import Optional, Dict
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()


def convert_to_profile_url(url: str) -> str:
    """
    Convert any Twitter/X URL to a clean profile URL
    """
    # Remove query parameters and fragments
    clean_url = url.split('?')[0].split('#')[0]
    
    # Extract the base parts
    parts = clean_url.split('/')
    if len(parts) < 4:
        return url  # Return as-is if can't parse
    
    protocol = parts[0]  # https:
    domain = parts[2]    # twitter.com or x.com
    username = parts[3]  # username
    
    # Build clean profile URL
    if domain in ['twitter.com', 'x.com', 'www.twitter.com', 'www.x.com']:
        # Always use x.com for consistency and return just the profile
        return f"https://x.com/{username}"
    
    return url  # Return original if not a Twitter URL


def smart_find_linkedin(investor_name: str) -> Optional[str]:
    """
    Simply search for "[investor name] LinkedIn" and use the first result
    """
    try:
        search = TavilySearch()
        
        # Simple search for LinkedIn profile
        query = f'"{investor_name}" LinkedIn'
        print(f"🔍 Searching: {query}")
        
        results = search.run(query)
        
        if isinstance(results, dict) and 'results' in results:
            # Just use the first result that contains a LinkedIn URL
            for result in results['results'][:1]:  # Only check first result
                url = result.get('url', '')
                
                # If it's a LinkedIn URL, use it
                if 'linkedin.com' in url:
                    print(f"✅ Found LinkedIn profile: {url}")
                    return url
                
                # Otherwise, check if there's a LinkedIn URL in the content
                content = result.get('content', '')
                linkedin_match = re.search(r'(https?://(?:www\.)?linkedin\.com/[^\s]+)', content)
                if linkedin_match:
                    url = linkedin_match.group(1)
                    print(f"✅ Found LinkedIn in content: {url}")
                    return url
        
        print(f"ℹ️ No LinkedIn profile found for {investor_name}")
        return None
        
    except Exception as e:
        print(f"LinkedIn search error: {e}")
        return None


def smart_find_twitter(investor_name: str) -> Optional[str]:
    """
    Simply search for "[investor name] Twitter" and use the first result
    """
    try:
        search = TavilySearch()
        
        # Simple search for Twitter profile
        query = f'"{investor_name}" Twitter'
        print(f"🔍 Searching: {query}")
        
        results = search.run(query)
        
        if isinstance(results, dict) and 'results' in results:
            # Check first few results for Twitter URLs
            for result in results['results'][:5]:  # Check more results
                url = result.get('url', '')
                content = result.get('content', '')
                title = result.get('title', '')
                
                print(f"🔍 Checking URL: {url}")
                
                # If it's a direct Twitter/X URL
                if 'twitter.com' in url or 'x.com' in url:
                    profile_url = convert_to_profile_url(url)
                    print(f"✅ Found Twitter profile: {profile_url}")
                    return profile_url
                
                # Check content and title for Twitter URLs
                all_text = f"{content} {title}"
                twitter_matches = re.findall(r'(https?://(?:www\.)?(?:twitter\.com|x\.com)/[^\s\)]+)', all_text)
                
                for twitter_url in twitter_matches:
                    # Clean up the URL (remove trailing punctuation)
                    clean_twitter_url = re.sub(r'[.,;!?\'")\]]+$', '', twitter_url)
                    profile_url = convert_to_profile_url(clean_twitter_url)
                    print(f"✅ Found Twitter in content: {profile_url}")
                    return profile_url
        
        print(f"ℹ️ No Twitter profile found for {investor_name}")
        return None
        
    except Exception as e:
        print(f"Twitter search error: {e}")
        return None


def smart_find_crunchbase(investor_name: str) -> Optional[str]:
    """
    Simply search for "[investor name] Crunchbase" and use the first result
    """
    try:
        search = TavilySearch()
        
        # Simple search for Crunchbase profile
        query = f'"{investor_name}" Crunchbase'
        print(f"🔍 Searching: {query}")
        
        results = search.run(query)
        
        if isinstance(results, dict) and 'results' in results:
            # Just use the first result that contains a Crunchbase URL
            for result in results['results'][:1]:  # Only check first result
                url = result.get('url', '')
                content = result.get('content', '')
                
                # If it's a Crunchbase URL, use it
                if 'crunchbase.com/person/' in url:
                    print(f"✅ Found Crunchbase profile: {url}")
                    return url
                
                # Otherwise, check if there's a Crunchbase URL in the content
                cb_match = re.search(r'(https?://(?:www\.)?crunchbase\.com/person/[^\s]+)', content)
                if cb_match:
                    url = cb_match.group(1)
                    print(f"✅ Found Crunchbase in content: {url}")
                    return url
        
        print(f"ℹ️ No Crunchbase profile found for {investor_name}")
        return None
        
    except Exception as e:
        print(f"Crunchbase search error: {e}")
        return None


def find_firm_website(investor_name: str) -> Optional[str]:
    """
    Search for the investor's firm website
    """
    try:
        search = TavilySearch()
        
        # Search for firm information
        query = f'"{investor_name}" venture capital firm company website'
        print(f"🔍 Searching for firm: {query}")
        
        results = search.run(query)
        
        if isinstance(results, dict) and 'results' in results:
            for result in results['results'][:5]:
                content = result.get('content', '').lower()
                url = result.get('url', '')
                
                # Look for mentions of firms
                firm_keywords = ['ventures', 'capital', 'partners', 'fund', 'invest', 'companies']
                
                # Skip social media and news sites
                skip_domains = ['twitter.com', 'linkedin.com', 'facebook.com', 'wikipedia.org', 
                               'forbes.com', 'techcrunch.com', 'bloomberg.com', 'cnbc.com']
                
                if any(domain in url for domain in skip_domains):
                    continue
                
                # Check if this might be a firm website
                if any(keyword in content for keyword in firm_keywords):
                    # Extract the base domain
                    domain_match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9\-]+\.[a-zA-Z]+)', url)
                    if domain_match:
                        firm_url = f"https://{domain_match.group(1)}"
                        
                        # Verify it's not a generic platform
                        if not any(skip in firm_url for skip in skip_domains):
                            print(f"✅ Found potential firm website: {firm_url}")
                            return firm_url
        
        return None
        
    except Exception as e:
        print(f"Firm search error: {e}")
        return None


def smart_find_all_profiles(investor_name: str) -> Dict[str, str]:
    """
    Use intelligent search to find all profile URLs for an investor
    """
    print(f"\n🤖 Smart Profile Search for: {investor_name}")
    print("=" * 50)
    
    urls = {}
    
    # Search for each platform
    print("\n📱 Searching for Twitter/X...")
    twitter_url = smart_find_twitter(investor_name)
    if twitter_url:
        urls['twitter'] = twitter_url
    
    print("\n💼 Searching for LinkedIn...")
    linkedin_url = smart_find_linkedin(investor_name)
    if linkedin_url:
        urls['linkedin'] = linkedin_url
    
    print("\n📊 Searching for Crunchbase...")
    crunchbase_url = smart_find_crunchbase(investor_name)
    if crunchbase_url:
        urls['crunchbase'] = crunchbase_url
    
    print("\n🏢 Searching for firm website...")
    firm_url = find_firm_website(investor_name)
    if firm_url:
        urls['firm'] = firm_url
    
    # For Medium, we'll link to articles about them
    urls['medium'] = f"https://medium.com/search?q={investor_name.replace(' ', '%20')}"
    
    print(f"\n📊 Found {len(urls)} profile URLs")
    return urls


def test_smart_finder():
    """
    Test the smart profile finder
    """
    test_investors = [
        "Mark Cuban",
        "Cathie Wood",
        "Peter Thiel"
    ]
    
    print("🧪 Testing Smart Profile Finder")
    print("=" * 60)
    
    for investor in test_investors:
        urls = smart_find_all_profiles(investor)
        
        print(f"\n📋 Results for {investor}:")
        for platform, url in urls.items():
            print(f"  {platform}: {url}")
        print()


if __name__ == "__main__":
    test_smart_finder()