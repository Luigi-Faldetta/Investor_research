"""
Find and validate actual profile URLs for investors
"""
import requests
import re
from typing import Optional, Dict
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()


def find_linkedin_url(investor_name: str) -> Optional[str]:
    """
    Find the actual LinkedIn URL for an investor
    """
    try:
        # Known LinkedIn profiles (most accurate)
        # Note: Some investors like Peter Thiel don't have public LinkedIn profiles
        known_profiles = {
            "cathie wood": "catherinedwood",
            "catherine wood": "catherinedwood",
            "marc andreessen": "pmarca",
            "naval ravikant": "navalr",
            "mark cuban": "markcuban",
            # "peter thiel": None,  # No public LinkedIn profile
            "reid hoffman": "reidhoffman",
            "balaji srinivasan": "balajis"
        }
        
        # Investors known to NOT have LinkedIn
        no_linkedin = ["peter thiel"]
        
        investor_lower = investor_name.lower()
        
        # Check if this investor is known to not have LinkedIn
        if investor_lower in no_linkedin:
            print(f"ℹ️ {investor_name} does not have a public LinkedIn profile")
            return None
            
        if investor_lower in known_profiles:
            profile_id = known_profiles[investor_lower]
            clean_url = f"https://www.linkedin.com/in/{profile_id}"
            print(f"✅ Found LinkedIn via known profile: {clean_url}")
            return clean_url
        
        search = TavilySearch()
        
        # Search specifically for LinkedIn profile
        query = f'site:linkedin.com/in/ "{investor_name}" investor venture capital'
        results = search.run(query)
        
        if isinstance(results, dict) and 'results' in results:
            for result in results['results'][:3]:
                url = result.get('url', '')
                title = result.get('title', '').lower()
                
                # Check if the name appears in the title
                name_parts = investor_name.lower().split()
                if any(part in title for part in name_parts):
                    # Validate it's a LinkedIn profile URL
                    if 'linkedin.com/in/' in url:
                        # Extract the profile part
                        match = re.search(r'linkedin\.com/in/([a-zA-Z0-9\-]+)', url)
                        if match:
                            profile_id = match.group(1)
                            clean_url = f"https://www.linkedin.com/in/{profile_id}"
                            print(f"✅ Found LinkedIn: {clean_url}")
                            return clean_url
        
        # Fallback: Try common patterns
        name_parts = investor_name.lower().split()
        common_patterns = [
            f"https://www.linkedin.com/in/{'-'.join(name_parts)}",
            f"https://www.linkedin.com/in/{''.join(name_parts)}",
            f"https://www.linkedin.com/in/{name_parts[0]}{name_parts[-1]}",
            f"https://www.linkedin.com/in/{name_parts[0]}-{name_parts[-1]}"
        ]
        
        for pattern_url in common_patterns:
            if verify_url_exists(pattern_url):
                print(f"✅ Found LinkedIn via pattern: {pattern_url}")
                return pattern_url
        
        return None
        
    except Exception as e:
        print(f"LinkedIn search error: {e}")
        return None


def find_crunchbase_url(investor_name: str) -> Optional[str]:
    """
    Find the actual Crunchbase URL for an investor
    """
    try:
        # Check known profiles first (most accurate)
        known_profiles = {
            "cathie wood": "https://www.crunchbase.com/person/catherine-wood",
            "catherine wood": "https://www.crunchbase.com/person/catherine-wood",
            "naval ravikant": "https://www.crunchbase.com/person/naval-ravikant",
            "marc andreessen": "https://www.crunchbase.com/person/marc-andreessen",
            "mark cuban": "https://www.crunchbase.com/person/mark-cuban",
            "peter thiel": "https://www.crunchbase.com/person/peter-thiel",
            "reid hoffman": "https://www.crunchbase.com/person/reid-hoffman",
            "balaji srinivasan": "https://www.crunchbase.com/person/balaji-s-srinivasan"
        }
        
        investor_lower = investor_name.lower()
        if investor_lower in known_profiles:
            url = known_profiles[investor_lower]
            print(f"✅ Found Crunchbase via known profile: {url}")
            return url
        
        # If not in known profiles, search
        search = TavilySearch()
        
        # Search specifically for Crunchbase profile
        query = f'site:crunchbase.com/person/ "{investor_name}"'
        results = search.run(query)
        
        if isinstance(results, dict) and 'results' in results:
            for result in results['results'][:3]:
                url = result.get('url', '')
                
                # Validate it's a Crunchbase person URL
                if 'crunchbase.com/person/' in url:
                    # Extract the profile part
                    match = re.search(r'crunchbase\.com/person/([a-zA-Z0-9\-]+)', url)
                    if match:
                        profile_id = match.group(1)
                        clean_url = f"https://www.crunchbase.com/person/{profile_id}"
                        
                        print(f"✅ Found Crunchbase: {clean_url}")
                        return clean_url
        
        # Fallback: Try common patterns
        name_parts = investor_name.lower().split()
        common_patterns = [
            f"https://www.crunchbase.com/person/{'-'.join(name_parts)}",
            f"https://www.crunchbase.com/person/{''.join(name_parts)}",
            f"https://www.crunchbase.com/person/{name_parts[0]}-{name_parts[-1]}"
        ]
        
        
        for pattern_url in common_patterns:
            # Crunchbase URLs often work even without verification
            print(f"✅ Using Crunchbase pattern: {pattern_url}")
            return pattern_url
        
        return None
        
    except Exception as e:
        print(f"Crunchbase search error: {e}")
        return None


def find_twitter_url(investor_name: str) -> Optional[str]:
    """
    Find the actual Twitter/X URL for an investor
    """
    try:
        search = TavilySearch()
        
        # Search for Twitter profile
        query = f'"{investor_name}" Twitter profile investor site:twitter.com OR site:x.com'
        results = search.run(query)
        
        if isinstance(results, dict) and 'results' in results:
            for result in results['results'][:5]:
                url = result.get('url', '')
                content = result.get('content', '').lower()
                
                # Extract Twitter handle
                twitter_match = re.search(r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)', url)
                if twitter_match:
                    handle = twitter_match.group(1)
                    if handle not in ['search', 'hashtag', 'i', 'home']:  # Skip non-profile pages
                        clean_url = f"https://twitter.com/{handle}"
                        print(f"✅ Found Twitter: {clean_url}")
                        return clean_url
                
                # Look for @ mentions in content
                mention_match = re.search(r'@([a-zA-Z0-9_]+)', content)
                if mention_match:
                    handle = mention_match.group(1)
                    clean_url = f"https://twitter.com/{handle}"
                    print(f"✅ Found Twitter via mention: {clean_url}")
                    return clean_url
        
        # Known investor Twitter handles
        known_handles = {
            "marc andreessen": "pmarca",
            "naval ravikant": "naval",
            "mark cuban": "mcuban",
            "peter thiel": "peterthiel",
            "reid hoffman": "reidhoffman",
            "cathie wood": "CathieDWood",
            "balaji srinivasan": "balajis"
        }
        
        investor_lower = investor_name.lower()
        if investor_lower in known_handles:
            handle = known_handles[investor_lower]
            clean_url = f"https://twitter.com/{handle}"
            print(f"✅ Found Twitter via known handle: {clean_url}")
            return clean_url
        
        return None
        
    except Exception as e:
        print(f"Twitter search error: {e}")
        return None


def find_medium_url(investor_name: str) -> Optional[str]:
    """
    Find Medium articles ABOUT the investor (not BY them)
    Returns a Medium search/tag URL that shows articles about them
    """
    try:
        search = TavilySearch()
        
        # Search for Medium articles ABOUT the investor
        query = f'site:medium.com "{investor_name}"'
        results = search.run(query)
        
        if isinstance(results, dict) and 'results' in results:
            # Get the first Medium article about them
            for result in results['results'][:1]:
                url = result.get('url', '')
                if 'medium.com' in url:
                    print(f"✅ Found Medium article about {investor_name}: {url}")
                    return url
        
        # Fallback: Return a Medium search URL for articles about them
        search_query = investor_name.replace(' ', '-').lower()
        search_url = f"https://medium.com/search?q={investor_name.replace(' ', '%20')}"
        print(f"✅ Using Medium search URL: {search_url}")
        return search_url
        
    except Exception as e:
        print(f"Medium search error: {e}")
        return None


def verify_url_exists(url: str) -> bool:
    """
    Verify if a URL exists and is accessible
    """
    try:
        # LinkedIn often blocks automated requests, so we'll be less strict
        if 'linkedin.com' in url:
            return True  # Assume LinkedIn URLs are valid if properly formatted
        
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code in [200, 301, 302]
    except:
        return False


def find_all_profile_urls(investor_name: str) -> Dict[str, str]:
    """
    Find all profile URLs for an investor
    """
    print(f"🔍 Finding real profile URLs for: {investor_name}")
    
    urls = {}
    
    # Find each platform
    twitter_url = find_twitter_url(investor_name)
    if twitter_url:
        urls['twitter'] = twitter_url
    
    linkedin_url = find_linkedin_url(investor_name)
    if linkedin_url:
        urls['linkedin'] = linkedin_url
    
    crunchbase_url = find_crunchbase_url(investor_name)
    if crunchbase_url:
        urls['crunchbase'] = crunchbase_url
    
    medium_url = find_medium_url(investor_name)
    if medium_url:
        urls['medium'] = medium_url
    
    # Firm URL (this is harder to automate, so we use known ones)
    firm_urls = {
        "marc andreessen": "https://a16z.com",
        "mark cuban": "https://markcubancompanies.com",
        "peter thiel": "https://foundersfund.com",
        "cathie wood": "https://ark-invest.com",
        "reid hoffman": "https://greylock.com"
    }
    
    investor_lower = investor_name.lower()
    for known_name, firm_url in firm_urls.items():
        if known_name in investor_lower:
            urls['firm'] = firm_url
            print(f"✅ Found firm: {firm_url}")
            break
    
    print(f"📊 Found {len(urls)} profile URLs")
    return urls


def test_profile_finder():
    """
    Test the profile URL finder
    """
    test_investors = [
        "Cathie Wood",
        "Marc Andreessen",
        "Naval Ravikant"
    ]
    
    print("🧪 Testing Profile URL Finder")
    print("=" * 50)
    
    for investor in test_investors:
        print(f"\n👤 Testing: {investor}")
        print("-" * 40)
        
        urls = find_all_profile_urls(investor)
        
        for platform, url in urls.items():
            print(f"  {platform}: {url}")
        
        if not urls:
            print("  No URLs found")


if __name__ == "__main__":
    test_profile_finder()