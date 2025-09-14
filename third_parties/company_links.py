"""
Company website and stock information enhancement
"""
import requests
import re
from typing import Optional, Dict, Tuple
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import time

load_dotenv()


def get_company_website(company_name: str) -> Optional[str]:
    """
    Find company website using simple internet search - use first search result
    """
    try:
        search = TavilySearch()
        
        # Clean company name for better search
        clean_name = company_name.replace(' Inc.', '').replace(' LLC', '').replace(' Corp.', '').replace(' Ltd.', '')
        
        # Try multiple search strategies - prioritize finding the main corporate site
        # Special handling for common company name conflicts
        if 'tesla' in clean_name.lower():
            queries = [
                f'"Tesla" electric car official website',
                f'"Tesla Motors" official website', 
                f'"Tesla Inc" corporate website',
            ]
        else:
            queries = [
                f'"{clean_name}" official website',  # Try official website first
                f'"{clean_name}" corporate website',
                f'site:{clean_name.lower().replace(" ", "")}.com',  # Try company domain
                f'"{company_name}" company website',
                f'"{company_name}"',  # Fallback to general search
            ]
        
        for query in queries:
            print(f"🔍 Searching: {query}")
            results = search.run(query)
            
            if isinstance(results, dict) and 'results' in results:
                # Check first few results for actual company website
                for result in results['results'][:5]:
                    url = result.get('url', '')
                    title = result.get('title', '').lower()
                    
                    # Skip obvious non-company sites and financial/info sites
                    skip_domains = ['wikipedia.org', 'linkedin.com', 'twitter.com', 'x.com', 'youtube.com', 
                                   'reddit.com', 'gov', 'edu', 'yahoo.com', 'finance.yahoo.com', 
                                   'bloomberg.com', 'marketwatch.com', 'sec.gov', 'crunchbase.com',
                                   'instagram.com', 'facebook.com', 'tiktok.com', 'westfield.com',
                                   'directory.', 'yellowpages.', 'yelp.com', 'britannica.com',
                                   'whitepinecounty.net', 'cityoflavista.org', '.org/', '.au/', '.eu/',
                                   'foursquare-europe.org']
                    
                    # Also skip common subpages and store sites - prefer main corporate sites
                    skip_paths = ['/careers', '/about-us', '/jobs', '/investor', '/news', '/quote/', 
                                 'store.', 'shop.', '/store', '/shop', '/retail', '/search', '/app/',
                                 '/facebook-app', '/productUniverse', '?srsltid=', '?sort=']
                    
                    # Skip if it's obviously not the right company (band, directory listing, etc.)
                    skip_titles = ['band', 'music', 'mall', 'directory', 'listing', 'store location',
                                  'city of', 'county', 'government']
                    
                    if (not any(domain in url.lower() for domain in skip_domains) and
                        not any(path in url.lower() for path in skip_paths) and
                        not any(skip_word in title for skip_word in skip_titles)):
                        
                        # Prefer URLs that look like corporate domains
                        if ('.com' in url or '.org' in url or '.net' in url):
                            print(f"✅ Found website for {company_name}: {url}")
                            return url
                
            # Small delay between searches
            import time
            time.sleep(0.5)
        
        print(f"ℹ️ No website found for {company_name}")
        return get_fallback_website(company_name)
        
    except Exception as e:
        print(f"Website search error for {company_name}: {e}")
        # Check if it's an API limit error
        if 'usage limit' in str(e).lower() or '432' in str(e):
            print(f"⚠️ API limit reached - using fallback for {company_name}")
            return get_fallback_website(company_name)
        return None


def get_fallback_website(company_name: str) -> Optional[str]:
    """
    Fallback website URLs for well-known companies when API limits are hit
    """
    fallbacks = {
        'paypal': 'https://www.paypal.com',
        'palantir': 'https://www.palantir.com',
        'meta': 'https://www.meta.com',
        'facebook': 'https://www.facebook.com',
        'spacex': 'https://www.spacex.com',
        'stripe': 'https://stripe.com',
        'twitter': 'https://twitter.com',
        'github': 'https://github.com',
        'pinterest': 'https://www.pinterest.com',
        'coinbase': 'https://www.coinbase.com',
        'tesla': 'https://www.tesla.com',
        'netflix': 'https://www.netflix.com',
        'uber': 'https://www.uber.com',
        'airbnb': 'https://www.airbnb.com',
        'linkedin': 'https://www.linkedin.com',
        'microsoft': 'https://www.microsoft.com',
        'google': 'https://www.google.com',
        'apple': 'https://www.apple.com',
        'amazon': 'https://www.amazon.com'
    }
    
    name_lower = company_name.lower().strip()
    for key, url in fallbacks.items():
        if key in name_lower:
            print(f"✅ Using fallback website for {company_name}: {url}")
            return url
    
    return None




def get_stock_info(company_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get stock ticker symbol and Yahoo Finance URL if company is public using internet search
    Returns (ticker_symbol, yahoo_finance_url)
    """
    try:
        search = TavilySearch()
        
        # Search specifically for stock ticker information
        queries = [
            f'"{company_name}" NYSE NASDAQ stock ticker',
            f'"{company_name}" stock symbol ticker',
        ]
        
        for query in queries:
            print(f"🔍 Searching stock info: {query}")
            results = search.run(query)
            
            if isinstance(results, dict) and 'results' in results:
                for result in results['results'][:5]:
                    content = result.get('content', '')
                    title = result.get('title', '')
                    url = result.get('url', '')
                    
                    # Look for stock ticker patterns in content and title
                    ticker = extract_ticker_from_content(content + " " + title, company_name)
                    
                    if ticker:
                        yahoo_url = f"https://finance.yahoo.com/quote/{ticker}"
                        print(f"📈 Found stock info for {company_name}: {ticker}")
                        return ticker, yahoo_url
            
            # Small delay between queries
            import time
            time.sleep(0.5)
        
        print(f"ℹ️ No stock info found for {company_name}")
        return get_fallback_stock_info(company_name)
        
    except Exception as e:
        print(f"Stock search error for {company_name}: {e}")
        # Check if it's an API limit error
        if 'usage limit' in str(e).lower() or '432' in str(e):
            print(f"⚠️ API limit reached - using fallback stock info for {company_name}")
            return get_fallback_stock_info(company_name)
        return None, None


def get_fallback_stock_info(company_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fallback stock tickers for well-known public companies when API limits are hit
    """
    stock_fallbacks = {
        'paypal': 'PYPL',
        'palantir': 'PLTR',
        'meta': 'META',
        'facebook': 'META',
        'stripe': None,  # Private
        'twitter': 'TWTR',  # Delisted but still reference
        'github': 'MSFT',  # Owned by Microsoft
        'pinterest': 'PINS',
        'coinbase': 'COIN',
        'tesla': 'TSLA',
        'netflix': 'NFLX',
        'uber': 'UBER',
        'airbnb': 'ABNB',
        'linkedin': 'MSFT',  # Owned by Microsoft
        'microsoft': 'MSFT',
        'google': 'GOOGL',
        'apple': 'AAPL',
        'amazon': 'AMZN'
    }
    
    name_lower = company_name.lower().strip()
    for key, ticker in stock_fallbacks.items():
        if key in name_lower:
            if ticker:
                yahoo_url = f"https://finance.yahoo.com/quote/{ticker}"
                print(f"✅ Using fallback stock info for {company_name}: {ticker}")
                return ticker, yahoo_url
            else:
                print(f"ℹ️ {company_name} is private (no stock ticker)")
                return None, None
    
    return None, None


def extract_ticker_from_content(content: str, company_name: str) -> Optional[str]:
    """
    Extract stock ticker symbol from text content
    """
    # Look for ticker patterns - prioritize more reliable patterns
    ticker_patterns = [
        r'\(([A-Z]{1,5})\)',  # (AAPL) - most reliable
        r'NYSE:\s*([A-Z]{1,5})',  # NYSE: AAPL
        r'NASDAQ:\s*([A-Z]{1,5})',  # NASDAQ: AAPL  
        r'Ticker:\s*([A-Z]{1,5})',  # Ticker: AAPL
        r'Symbol:\s*([A-Z]{1,5})',  # Symbol: AAPL
        r'quote/([A-Z]{1,5})',  # quote/AAPL (from Yahoo Finance URLs)
        r'trades\s+as\s+([A-Z]{1,5})',  # trades as AAPL
        r'ticker\s+symbol\s+([A-Z]{1,5})',  # ticker symbol AAPL
        r'stock\s+symbol\s+([A-Z]{1,5})',  # stock symbol AAPL
    ]
    
    found_tickers = []
    
    for pattern in ticker_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            ticker = match.upper()
            # Validate ticker (reasonable length, not common words, not exchange names)
            if (2 <= len(ticker) <= 5 and 
                ticker not in ['THE', 'AND', 'FOR', 'ARE', 'WITH', 'ALSO', 'THIS', 'THAT', 'FROM', 'WILL', 'CAN', 'HAS', 'BUT', 'NOT', 'ALL', 'ANY', 'ITS', 'WAS', 'HER', 'HIS', 'OUR', 'YOU', 'SHE', 'HIM', 'NYSE', 'NASDAQ', 'SEARC', 'XFLT'] and
                not ticker.startswith('HTTP')):
                found_tickers.append(ticker)
    
    # Return the most common ticker found, or the first one
    if found_tickers:
        # Count occurrences and return most frequent
        from collections import Counter
        most_common = Counter(found_tickers).most_common(1)
        return most_common[0][0]
    
    return None


def test_yahoo_finance_page(ticker: str) -> bool:
    """
    Test if a ticker exists on Yahoo Finance
    """
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}"
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False




def enhance_company_with_links(company_name: str) -> Dict[str, str]:
    """
    Get both website and stock information for a company
    Returns dict with 'website', 'stock_symbol', 'yahoo_finance_url'
    """
    print(f"🔍 Enhancing links for: {company_name}")
    
    # Get website
    website = get_company_website(company_name)
    
    # Small delay to be respectful to APIs
    time.sleep(0.5)
    
    # Get stock info
    stock_symbol, yahoo_url = get_stock_info(company_name)
    
    result = {
        'website': website or '',
        'stock_symbol': stock_symbol or '',
        'yahoo_finance_url': yahoo_url or ''
    }
    
    print(f"✅ Enhanced {company_name}:")
    if website:
        print(f"   🌐 Website: {website}")
    if stock_symbol:
        print(f"   📈 Stock: {stock_symbol} -> {yahoo_url}")
    
    return result


def enhance_portfolio_companies(companies: list) -> list:
    """
    Enhance a list of portfolio companies with website and stock links
    """
    enhanced_companies = []
    
    print(f"🚀 Enhancing {len(companies)} companies with links...")
    print("=" * 50)
    
    for i, company in enumerate(companies, 1):
        company_name = company.get('name', '')
        if not company_name:
            enhanced_companies.append(company)
            continue
        
        print(f"\n[{i}/{len(companies)}] Processing: {company_name}")
        print("-" * 30)
        
        # Get enhanced links
        links = enhance_company_with_links(company_name)
        
        # Add to company data
        enhanced_company = company.copy()
        enhanced_company.update(links)
        enhanced_companies.append(enhanced_company)
        
        # Rate limiting
        time.sleep(1)
    
    print(f"\n🎉 Enhanced {len(enhanced_companies)} companies!")
    return enhanced_companies


if __name__ == "__main__":
    # Test the enhancement system
    test_companies = [
        {'name': 'Facebook', 'sector': 'Social Media'},
        {'name': 'Uber', 'sector': 'Transportation'},
        {'name': 'Airbnb', 'sector': 'Travel'},
        {'name': 'Some Unknown Startup', 'sector': 'AI'}
    ]
    
    enhanced = enhance_portfolio_companies(test_companies)
    
    print("\n📊 Final Results:")
    print("=" * 50)
    for company in enhanced:
        print(f"\n🏢 {company['name']}")
        print(f"   🌐 Website: {company.get('website', 'None')}")
        print(f"   📈 Stock: {company.get('stock_symbol', 'None')}")
        if company.get('yahoo_finance_url'):
            print(f"   💹 Yahoo: {company['yahoo_finance_url']}")