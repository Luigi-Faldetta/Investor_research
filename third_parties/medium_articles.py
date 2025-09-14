"""
Fetch Medium articles ABOUT an investor (not BY them)
"""
import requests
from typing import List, Dict, Optional
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import time
from datetime import datetime, timedelta

load_dotenv()


def parse_relative_date(date_text: str) -> Optional[str]:
    """
    Convert Medium's relative dates like '3 days ago', '2 weeks ago' to actual dates
    Returns formatted date string like 'Jan 15, 2024' or None if can't parse
    """
    try:
        date_text = date_text.lower().strip()
        now = datetime.now()
        
        # Extract number and unit
        parts = date_text.split()
        if len(parts) < 3 or parts[-1] != 'ago':
            return None
        
        # Try to find the number and time unit
        number_part = None
        unit_part = None
        
        for i, part in enumerate(parts):
            if part.isdigit():
                number_part = int(part)
                if i + 1 < len(parts):
                    unit_part = parts[i + 1].lower()
                break
            elif part in ['a', 'an']:
                number_part = 1
                if i + 1 < len(parts):
                    unit_part = parts[i + 1].lower()
                break
        
        if number_part is None or unit_part is None:
            return None
        
        # Calculate the date based on unit
        if unit_part.startswith('day'):
            target_date = now - timedelta(days=number_part)
        elif unit_part.startswith('week'):
            target_date = now - timedelta(weeks=number_part)
        elif unit_part.startswith('month'):
            # Approximate months as 30 days
            target_date = now - timedelta(days=number_part * 30)
        elif unit_part.startswith('year'):
            # Approximate years as 365 days
            target_date = now - timedelta(days=number_part * 365)
        elif unit_part.startswith('hour'):
            target_date = now - timedelta(hours=number_part)
        elif unit_part.startswith('minute'):
            target_date = now - timedelta(minutes=number_part)
        else:
            return None
        
        # Format as "Jan 15, 2025"
        return target_date.strftime('%b %d, %Y')
        
    except Exception as e:
        return None


def fetch_article_metadata(url: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Fetch actual article content and extract real publication date and reading time
    Returns: (date, read_time, content)
    """
    try:
        print(f"🔍 Fetching metadata from: {url[:60]}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract publication date
        date = None
        
        # Try various Medium date selectors
        date_selectors = [
            'time[datetime]',  # Standard datetime attribute
            '[data-testid="storyPublishDate"]',  # Medium specific
            'time',  # Generic time tag
            '[class*="publishedAt"]',  # Classes containing publishedAt
            '[class*="date"]',  # Classes containing date
            '[class*="publish"]'  # Classes containing publish
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                # Try datetime attribute first
                if date_element.get('datetime'):
                    date_str = date_element.get('datetime')
                    # Parse ISO format like "2023-01-15T10:30:00.000Z"
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date = dt.strftime('%b %d, %Y')
                        break
                    except:
                        pass
                
                # Try text content
                date_text = date_element.get_text(strip=True)
                if date_text and len(date_text) < 50:  # Reasonable date length
                    # Check if it's a relative date like "3 days ago"
                    if 'ago' in date_text.lower():
                        parsed_date = parse_relative_date(date_text)
                        if parsed_date:
                            date = parsed_date
                            break
                    else:
                        date = date_text
                        break
        
        # Fallback: search for any text containing relative dates in the entire page
        if not date:
            page_text = soup.get_text()
            
            # Look for patterns like "3 days ago", "2 weeks ago", etc.
            relative_date_patterns = [
                r'(\d+\s+days?\s+ago)',
                r'(\d+\s+weeks?\s+ago)', 
                r'(\d+\s+months?\s+ago)',
                r'(\d+\s+years?\s+ago)',
                r'(a\s+day\s+ago)',
                r'(a\s+week\s+ago)',
                r'(a\s+month\s+ago)',
                r'(a\s+year\s+ago)'
            ]
            
            for pattern in relative_date_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    # Take the first match and try to parse it
                    potential_date = matches[0]
                    parsed_date = parse_relative_date(potential_date)
                    if parsed_date:
                        date = parsed_date
                        break
        
        # Extract reading time
        read_time = None
        
        # Try various Medium reading time selectors
        read_time_selectors = [
            '[data-testid="storyReadTime"]',  # Medium specific
            '[class*="readingTime"]',  # Classes containing readingTime
            '[class*="read-time"]',  # Classes containing read-time
            '[aria-label*="min read"]',  # Aria labels
            'span:contains("min read")',  # Text content
        ]
        
        for selector in read_time_selectors:
            if 'contains' in selector:
                # Use a different approach for text-based selectors
                elements = soup.find_all('span')
                for elem in elements:
                    if 'min read' in elem.get_text().lower():
                        read_time = elem.get_text(strip=True)
                        break
            else:
                read_time_element = soup.select_one(selector)
                if read_time_element:
                    read_time = read_time_element.get_text(strip=True)
                    break
        
        # If no reading time found, extract article content and calculate
        if not read_time:
            # Get main content
            content_selectors = [
                'article',
                '[role="main"]',
                '.postArticle-content',
                '[class*="article"]',
                '[class*="story"]'
            ]
            
            content = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    content = content_element.get_text(strip=True)
                    break
            
            if content:
                # Calculate reading time from actual content
                word_count = len(content.split())
                minutes = max(1, round(word_count / 220))  # 220 words per minute
                read_time = f"{minutes} min read"
        
        print(f"✅ Extracted - Date: {date}, Reading time: {read_time}")
        # If still no date found, use a more recent default
        if not date:
            # Default to "Recent" instead of "2024"
            date = "Recent"
        
        return date, read_time, response.text
        
    except Exception as e:
        print(f"❌ Failed to fetch metadata from {url}: {e}")
        return None, None, None


def extract_title_for_url(soup: BeautifulSoup, url: str) -> Optional[str]:
    """
    Try to find the title for a given URL by looking for nearby text in the HTML
    """
    try:
        # Extract the article ID/slug from URL
        url_parts = url.split('/')
        article_id = url_parts[-1] if url_parts else ''
        
        # Look for text elements that might contain the title
        # Search for the URL or parts of it in the HTML and find nearby titles
        page_text = soup.get_text()
        
        # Simple approach: look for headings near the URL
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            if len(heading_text) > 15 and len(heading_text) < 200:  # Reasonable title length
                return heading_text
        
        return None
        
    except Exception:
        return None


def scrape_medium_search_page(search_url: str, limit: int = 5) -> List[Dict]:
    """
    Scrape Medium search page to get the exact same articles users see
    Uses multiple strategies to extract content from JavaScript-heavy page
    """
    try:
        # Enhanced headers to mimic real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://medium.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Create session for cookie handling
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(search_url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Strategy 1: Look for JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Article' and len(articles) < limit:
                            articles.append({
                                'title': item.get('headline', 'Untitled'),
                                'url': item.get('url', ''),
                                'excerpt': item.get('description', '')[:200],
                                'date': item.get('datePublished', 'Recent')[:10],
                                'read_time': '5 min read'
                            })
                elif data.get('@type') == 'Article' and len(articles) < limit:
                    articles.append({
                        'title': data.get('headline', 'Untitled'),
                        'url': data.get('url', ''),
                        'excerpt': data.get('description', '')[:200],
                        'date': data.get('datePublished', 'Recent')[:10],
                        'read_time': '5 min read'
                    })
            except json.JSONDecodeError:
                continue
        
        # Strategy 2: Look for Medium's data in script tags
        if not articles:
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'window.__APOLLO_STATE__' in script.string:
                    # Extract Apollo GraphQL state that Medium uses
                    try:
                        # Find the JSON data
                        start = script.string.find('{')
                        end = script.string.rfind('}') + 1
                        if start != -1 and end > start:
                            data_str = script.string[start:end]
                            data = json.loads(data_str)
                            
                            # Extract articles from Apollo state
                            for key, value in data.items():
                                if isinstance(value, dict) and value.get('__typename') == 'Post':
                                    if len(articles) < limit:
                                        title = value.get('title', 'Untitled')
                                        if title and len(title) > 5:  # Basic quality filter
                                            # Build proper Medium URL
                                            author_slug = value.get('creator', {}).get('username', '')
                                            unique_slug = value.get('uniqueSlug', '')
                                            
                                            # Try different URL patterns
                                            url = ''
                                            if author_slug and unique_slug:
                                                url = f"https://medium.com/@{author_slug}/{unique_slug}"
                                            elif unique_slug:
                                                url = f"https://medium.com/p/{unique_slug}"
                                            
                                            if url:
                                                # Format reading time properly
                                                reading_time = value.get('readingTime', 5)
                                                if isinstance(reading_time, (int, float)):
                                                    read_time_str = f"{int(reading_time)} min read"
                                                else:
                                                    read_time_str = "5 min read"
                                                
                                                articles.append({
                                                    'title': title,
                                                    'url': url,
                                                    'excerpt': value.get('previewContent', {}).get('subtitle', '')[:200],
                                                    'date': value.get('createdAt', 'Recent')[:10],
                                                    'read_time': read_time_str
                                                })
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # Strategy 3: Look for article URLs in different patterns  
        if not articles:
            # Find article URLs using multiple patterns
            all_text = soup.get_text()
            
            # Extract URLs that look like Medium articles
            url_patterns = [
                r'https://medium\.com/@[^/\s]+/[^/\s]+-[a-f0-9]+',  # @author/title-id
                r'https://[^/\s]+\.medium\.com/[^/\s]+-[a-f0-9]+',  # publication.medium.com/title-id
                r'https://medium\.com/[^/\s]+/[^/\s]+-[a-f0-9]+',   # medium.com/publication/title-id
                r'https://medium\.com/p/[a-f0-9\-]+'                # medium.com/p/id
            ]
            
            found_urls = set()
            for pattern in url_patterns:
                matches = re.findall(pattern, all_text)
                for match in matches:
                    if len(found_urls) < limit * 2:  # Get more to filter
                        found_urls.add(match)
            
            # For each URL, try to find its title in the HTML
            for url in list(found_urls)[:limit]:
                title = extract_title_for_url(soup, url)
                if title and len(title) > 10:
                    articles.append({
                        'title': title[:150],
                        'url': url,
                        'excerpt': 'Click to read full article on Medium',
                        'date': 'Recent',
                        'read_time': '5 min read'
                    })
            
            # Fallback: Look for any Medium links
            if not articles:
                links = soup.find_all('a', href=True)
                
                for link in links[:limit * 5]:
                    href = link.get('href')
                    
                    if not href:
                        continue
                    
                    # Make sure it's a full URL
                    if href.startswith('/'):
                        href = 'https://medium.com' + href
                    
                    # Check if it looks like a Medium article
                    if ('medium.com' in href and 
                        any(pattern in href for pattern in ['/@', '/p/', '-']) and
                        not any(skip in href for skip in ['/search', '/tag/', '/u/', '/users/', '?', '/m/', '/about'])):
                        
                        title = link.get_text(strip=True) or extract_title_for_url(soup, href)
                        
                        if title and len(title) > 10 and len(articles) < limit:
                            articles.append({
                                'title': title[:150],
                                'url': href,
                                'excerpt': 'Click to read full article on Medium',
                                'date': 'Recent',
                                'read_time': '5 min read'
                            })
        
        return articles[:limit]
        
    except Exception as e:
        print(f"Medium scraping error: {e}")
        return []


def fetch_medium_articles_about(investor_name: str, limit: int = 5) -> List[Dict]:
    """
    Fetch Medium articles written ABOUT an investor - try to get exact same results as Medium search URL
    Returns list of articles with title, link, excerpt, and date
    """
    try:
        # First, try to scrape the actual Medium search page that users see
        medium_search_url = f"https://medium.com/search?q={investor_name.replace(' ', '%20')}"
        print(f"🔍 Attempting to scrape Medium search page: {medium_search_url}")
        
        articles = scrape_medium_search_page(medium_search_url, limit)
        if articles:
            print(f"✅ Successfully scraped {len(articles)} articles from Medium search page")
            
            # Enhance articles with real metadata
            enhanced_articles = []
            for article in articles:
                if article.get('url') and 'medium.com' in article['url']:
                    # Try to get real publication date and reading time
                    date, read_time, _ = fetch_article_metadata(article['url'])
                    
                    enhanced_article = article.copy()
                    if date:
                        enhanced_article['date'] = date
                    if read_time:
                        enhanced_article['read_time'] = read_time
                    
                    enhanced_articles.append(enhanced_article)
                else:
                    enhanced_articles.append(article)
            
            return sort_articles_by_date(enhanced_articles)
        
        print("⚠️ Medium scraping failed, using Tavily search as fallback")
        
        # Fallback: Use Tavily to search with the same query pattern as Medium search URL
        search = TavilySearch()
        
        # Use a simplified search that matches what users would expect from the Medium URL
        query = f'site:medium.com "{investor_name}"'
        print(f"🔍 Searching for Medium articles with query: {query}")
        
        results = search.run(query)
        
        articles = []
        if isinstance(results, dict) and 'results' in results:
            for result in results['results'][:limit]:
                url = result.get('url', '')
                
                # Only include actual Medium articles
                if 'medium.com' in url and '/tag/' not in url and '/search' not in url:
                    content = result.get('content', '')
                    
                    # Fetch actual article content for accurate metadata
                    actual_date, actual_read_time, full_content = fetch_article_metadata(url)
                    
                    article = {
                        'title': result.get('title', ''),
                        'link': url,
                        'excerpt': content[:200] + '...' if content else '',
                        'date': actual_date or extract_date_from_content(content),
                        'read_time': actual_read_time or estimate_reading_time(content),
                        'url': url
                    }
                    
                    # Only add if it actually mentions the investor
                    if investor_name.lower() in article['title'].lower() or investor_name.lower() in article['excerpt'].lower():
                        articles.append(article)
                        print(f"📄 Found article: {article['title'][:50]}...")
        
        if articles:
            # Sort articles chronologically - most recent first
            articles = sort_articles_by_date(articles)
            print(f"✅ Found {len(articles)} Medium articles about {investor_name}")
        else:
            print(f"ℹ️ No Medium articles found about {investor_name}")
            
            # Return a placeholder article suggesting where to find more
            articles = [{
                'title': f"Search for articles about {investor_name}",
                'link': f"https://medium.com/search?q={investor_name.replace(' ', '%20')}",
                'excerpt': f"Click to search Medium for articles about {investor_name}",
                'date': ''
            }]
        
        return articles
        
    except Exception as e:
        print(f"Error fetching Medium articles: {e}")
        return []


def extract_date_from_content(content: str) -> str:
    """
    Try to extract a date from content using multiple patterns
    """
    import re
    from datetime import datetime
    
    if not content:
        return ''
    
    # Pattern for "Jan 1, 2024" or "January 1, 2024"
    date_pattern1 = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}'
    match = re.search(date_pattern1, content, re.IGNORECASE)
    if match:
        return match.group()
    
    # Pattern for "2024-01-01" format
    date_pattern2 = r'\d{4}-\d{2}-\d{2}'
    match2 = re.search(date_pattern2, content)
    if match2:
        return match2.group()
    
    # Pattern for "2024/01/01" format
    date_pattern3 = r'\d{4}/\d{2}/\d{2}'
    match3 = re.search(date_pattern3, content)
    if match3:
        return match3.group()
    
    # Look for "ago" patterns like "3 days ago", "2 weeks ago"
    ago_pattern = r'(\d+)\s+(day|week|month|year)s?\s+ago'
    ago_match = re.search(ago_pattern, content, re.IGNORECASE)
    if ago_match:
        return ago_match.group()
    
    # Look for "Published on" or "Published in" patterns
    pub_pattern = r'Published\s+(on|in)\s+([A-Za-z]+ \d{1,2}, \d{4})'
    pub_match = re.search(pub_pattern, content, re.IGNORECASE)
    if pub_match:
        return pub_match.group(2)
    
    # Default to current year if no date found
    return datetime.now().strftime('%Y')


def sort_articles_by_date(articles: List[Dict]) -> List[Dict]:
    """
    Sort articles by publication date - most recent first
    """
    from datetime import datetime
    import re
    
    def parse_date(date_str: str) -> datetime:
        """Parse various date formats and return datetime object"""
        if not date_str:
            return datetime.min
        
        try:
            # Handle "Dec 7, 2024" format
            month_day_year = r'([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})'
            match = re.search(month_day_year, date_str)
            if match:
                month_str, day, year = match.groups()
                month_map = {
                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                }
                month = month_map.get(month_str.lower(), 1)
                return datetime(int(year), month, int(day))
            
            # Handle "2024" format (year only)
            if date_str.isdigit() and len(date_str) == 4:
                return datetime(int(date_str), 1, 1)
            
            # Handle "YYYY-MM-DD" format
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                return datetime.strptime(date_str, '%Y-%m-%d')
            
            # Handle "YYYY/MM/DD" format
            if re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                return datetime.strptime(date_str, '%Y/%m/%d')
            
            # Default to minimum date if can't parse
            return datetime.min
            
        except Exception:
            return datetime.min
    
    # Sort articles by parsed date, most recent first
    try:
        sorted_articles = sorted(articles, key=lambda x: parse_date(x.get('date', '')), reverse=True)
        print(f"📅 Sorted {len(sorted_articles)} articles chronologically")
        return sorted_articles
    except Exception as e:
        print(f"Date sorting error: {e}")
        return articles


def estimate_reading_time(content: str) -> str:
    """
    Estimate reading time based on content length
    Average reading speed is about 200-250 words per minute
    """
    if not content:
        return '1 min'
    
    # Count words (rough estimate)
    word_count = len(content.split())
    
    # If content is very short (search results), estimate based on typical article length
    if word_count < 50:
        word_count = 500  # Assume typical Medium article length
    
    # Calculate reading time (using 220 words per minute average)
    minutes = max(1, round(word_count / 220))
    
    return f'{minutes} min'


def test_medium_articles():
    """
    Test fetching articles about investors
    """
    test_investors = [
        "Peter Thiel",
        "Marc Andreessen",
        "Cathie Wood"
    ]
    
    print("🧪 Testing Medium Articles Fetcher")
    print("=" * 50)
    
    for investor in test_investors:
        print(f"\n👤 Testing: {investor}")
        print("-" * 40)
        
        articles = fetch_medium_articles_about(investor, limit=3)
        
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title'][:60]}...")
            print(f"   Link: {article['link'][:60]}...")
            print(f"   Date: {article['date']}")
            print(f"   Excerpt: {article['excerpt'][:100]}...")


if __name__ == "__main__":
    test_medium_articles()