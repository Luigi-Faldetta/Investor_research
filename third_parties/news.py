"""
Fetch latest news about an investor using Tavily Search API
"""
from langchain_tavily import TavilySearch
from typing import List, Dict
from datetime import datetime
import re


def fetch_investor_news(investor_name: str, limit: int = 5, use_mock: bool = True) -> List[Dict]:
    """
    Fetch latest news articles about an investor
    
    Args:
        investor_name: Name of the investor to search news for
        limit: Maximum number of news articles to return (default 5)
        use_mock: Whether to use mock data instead of real API calls
        
    Returns:
        List of news articles with title, excerpt, source, date, and url
    """
    # Return mock data if requested
    if use_mock:
        return get_mock_news(investor_name)[:limit]
    
    try:
        search = TavilySearch()
        
        # Search for recent news about the investor
        query = f'"{investor_name}" news latest announcements investments'
        print(f"🔍 Searching for latest news about {investor_name}...")
        
        results = search.run(query)
        
        news_articles = []
        
        if isinstance(results, dict) and 'results' in results:
            search_results = results['results'][:limit * 2]  # Get more to filter
            
            for result in search_results:
                # Extract article information
                title = result.get('title', '')
                content = result.get('content', '')
                url = result.get('url', '')
                
                # Skip if it's not a news article (e.g., social media, directories)
                skip_domains = ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 
                               'instagram.com', 'youtube.com', 'wikipedia.org', 
                               'crunchbase.com', 'github.com', 'reddit.com']
                
                if any(domain in url.lower() for domain in skip_domains):
                    continue
                
                # Extract source from URL
                source = extract_source_from_url(url)
                
                # Try to extract date from content or use a placeholder
                date = extract_date_from_content(content) or "Recent"
                
                # Clean and truncate excerpt
                excerpt = clean_excerpt(content, max_length=200)
                
                news_article = {
                    'title': title,
                    'excerpt': excerpt,
                    'source': source,
                    'date': date,
                    'url': url
                }
                
                news_articles.append(news_article)
                
                if len(news_articles) >= limit:
                    break
            
            print(f"✅ Found {len(news_articles)} news articles")
        else:
            print("❌ No news results found")
        
        return news_articles
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def extract_source_from_url(url: str) -> str:
    """
    Extract the source name from a URL
    """
    try:
        # Remove protocol
        domain = url.replace('https://', '').replace('http://', '').replace('www.', '')
        # Get domain name
        domain = domain.split('/')[0]
        # Clean up common patterns
        source = domain.split('.')[0]
        # Capitalize
        source = source.capitalize()
        
        # Map common sources to better names
        source_mapping = {
            'Techcrunch': 'TechCrunch',
            'Wsj': 'Wall Street Journal',
            'Nytimes': 'New York Times',
            'Forbes': 'Forbes',
            'Bloomberg': 'Bloomberg',
            'Reuters': 'Reuters',
            'Cnbc': 'CNBC',
            'Theverge': 'The Verge',
            'Wired': 'Wired',
            'Venturebeat': 'VentureBeat',
            'Axios': 'Axios',
            'Businessinsider': 'Business Insider',
            'Fortune': 'Fortune',
            'Marketwatch': 'MarketWatch',
            'Seekingalpha': 'Seeking Alpha',
            'Benzinga': 'Benzinga',
            'Techradar': 'TechRadar',
            'Engadget': 'Engadget',
            'Arstechnica': 'Ars Technica',
            'Theinformation': 'The Information'
        }
        
        return source_mapping.get(source, source)
        
    except:
        return "News Source"


def extract_date_from_content(content: str) -> str:
    """
    Try to extract a date from the content
    """
    try:
        # Look for common date patterns
        date_patterns = [
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Try to parse and reformat
                try:
                    # Simple formatting - just return the matched date
                    return date_str
                except:
                    return date_str
        
        # Look for relative dates
        today_match = re.search(r'\btoday\b', content, re.IGNORECASE)
        if today_match:
            return "Today"
        
        yesterday_match = re.search(r'\byesterday\b', content, re.IGNORECASE)
        if yesterday_match:
            return "Yesterday"
        
        # Look for "X days ago" pattern
        days_ago = re.search(r'(\d+)\s+days?\s+ago', content, re.IGNORECASE)
        if days_ago:
            return f"{days_ago.group(1)} days ago"
        
        # Look for "X hours ago" pattern
        hours_ago = re.search(r'(\d+)\s+hours?\s+ago', content, re.IGNORECASE)
        if hours_ago:
            return f"{hours_ago.group(1)} hours ago"
        
        return None
        
    except:
        return None


def clean_excerpt(text: str, max_length: int = 200) -> str:
    """
    Clean and truncate text to create an excerpt
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Truncate if needed
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text


def get_mock_news(investor_name: str) -> List[Dict]:
    """
    Return mock news data for testing or when API is unavailable
    """
    if "Mark Cuban" in investor_name:
        return [
            {
                'title': "Mark Cuban Launches Cost Plus Drugs Expansion to Mental Health Medications",
                'excerpt': "The Shark Tank star announced his pharmacy platform will now offer affordable mental health drugs. Cuban stated: 'Mental health is healthcare, and healthcare should be affordable for everyone.'",
                'source': 'Forbes',
                'date': 'Today',
                'url': 'https://www.costplusdrugs.com/medications/categories/mental-health/',
                'content': "Mark Cuban announced: 'Our mission at Cost Plus Drugs is simple - make medications affordable. Now we're extending that to mental health because no one should choose between paying rent and getting the medication they need.'"
            },
            {
                'title': "Cuban Invests $10M in AI-Powered Sports Analytics Startup",
                'excerpt': "The Dallas Mavericks owner backs new technology that promises to revolutionize player performance analysis and fan engagement.",
                'source': 'TechCrunch',
                'date': 'Yesterday',
                'url': 'https://www.mobihealthnews.com/news/mark-cuban-cost-plus-drug-company-9amhealth-partner-obesity-meds',
                'content': "Cuban told reporters: 'Sports and technology are converging in ways we never imagined. This AI platform will change how teams scout, train, and engage with fans forever.'"
            },
            {
                'title': "Mark Cuban: 'Entrepreneurship is About Solving Problems, Not Making Money'",
                'excerpt': "In a new interview, the billionaire investor emphasizes purpose-driven business as the key to lasting success.",
                'source': 'CNBC',
                'date': '2 days ago',
                'url': 'https://gradstudies.musc.edu/about/blog/2024/09/easier-pill-to-swallow',
                'content': "According to Cuban: 'The best businesses solve real problems for real people. Money is just the scorecard - the game is about making people's lives better.'"
            }
        ]
    elif "Peter Thiel" in investor_name:
        return [
            {
                'title': "Peter Thiel's Founders Fund Leads $200M Round in AI Defense Startup",
                'excerpt': "The venture capital firm backs autonomous defense technology, continuing Thiel's focus on breakthrough innovations that secure America's technological edge.",
                'source': 'Wall Street Journal',
                'date': 'Today',
                'url': 'https://siliconangle.com/2020/07/01/peter-thiel-backed-defense-tech-startup-anduril-raises-200m/',
                'content': "Thiel commented: 'The future of national security depends on our ability to develop autonomous systems faster than our adversaries. This investment represents our commitment to maintaining American technological superiority.'"
            },
            {
                'title': "Thiel: 'Universities Have Become Conformity Factories'",
                'excerpt': "Speaking at Stanford, the PayPal co-founder criticized higher education for stifling independent thinking and innovation.",
                'source': 'The Information',
                'date': 'Yesterday',
                'url': 'https://vocal.media/journal/exploring-peter-thiel-s-impact-on-ai-through-founders-fund-s-investments',
                'content': "Peter Thiel stated: 'Universities today teach students what to think, not how to think. The most successful entrepreneurs I know are those who escaped the conformity trap early.'"
            },
            {
                'title': "Palantir Stock Surges as Government Contracts Expand",
                'excerpt': "The data analytics company co-founded by Thiel sees massive growth in government and enterprise sectors.",
                'source': 'Bloomberg',
                'date': '3 days ago',
                'url': 'https://www.benzinga.com/markets/cryptocurrency/24/10/41616040/peter-thiels-founders-fund-leads-500m-fundraise-in-waste-gas-powered-ai-cloud-start-up',
                'content': "Regarding Palantir's success, Thiel noted: 'We built Palantir to solve the world's hardest problems. The growth we're seeing validates our belief that data and algorithms can make institutions more effective.'"
            }
        ]
    elif "Paul Tudor Jones" in investor_name:
        return [
            {
                'title': "Paul Tudor Jones Pledges $500M for Climate Investment Initiative",
                'excerpt': "The legendary trader announces major commitment to environmental solutions through his Tudor Investment Corporation.",
                'source': 'Financial Times',
                'date': 'Today',
                'url': 'https://www.bloomberg.com/news/articles/2025-08-26/crowdsourcing-hedge-fund-gets-500-million-jpmorgan-commitment',
                'content': "Jones declared: 'Climate change is the defining macro trade of our generation. We have an obligation to deploy capital toward solutions that benefit both the planet and our portfolios.'"
            },
            {
                'title': "Tudor Jones: 'Inequality is the Biggest Risk to Markets'",
                'excerpt': "The hedge fund manager warns that growing wealth disparity poses systemic risks to economic stability.",
                'source': 'CNBC',
                'date': 'Yesterday',
                'url': 'https://www.cnbc.com/video/2024/10/22/watch-cnbcs-full-interview-with-tudor-investment-founder-paul-tudor-jones.html',
                'content': "Paul Tudor Jones warned: 'We cannot have a functioning democracy or healthy markets when the gap between rich and poor continues to widen. This is not just a social issue - it's an existential economic risk.'"
            },
            {
                'title': "Robin Hood Foundation Announces $100M Education Initiative",
                'excerpt': "The anti-poverty organization founded by Tudor Jones launches ambitious program to transform education in underserved communities.",
                'source': 'New York Times',
                'date': '2 days ago',
                'url': 'https://www.insidephilanthropy.com/wall-street-donors/paul-tudor-jones.html',
                'content': "Tudor Jones reflected: 'Education is the ultimate equalizer. Through Robin Hood, we've learned that targeted investments in teaching and learning can break generational cycles of poverty.'"
            }
        ]
    elif "Cathie Wood" in investor_name:
        return [
            {
                'title': "Cathie Wood: 'AI and Genomics Convergence Will Create $50 Trillion Market'",
                'excerpt': "The ARK Invest founder predicts unprecedented value creation as artificial intelligence transforms healthcare and biotechnology.",
                'source': 'Bloomberg',
                'date': 'Today',
                'url': 'https://ark-invest.com/articles/analyst-research/ai-genomics-convergence/',
                'content': "Wood proclaimed: 'We're witnessing the convergence of artificial intelligence and genomic sequencing. This intersection will unlock personalized medicine and create the largest market opportunity in human history.'"
            },
            {
                'title': "ARK Invest Doubles Down on Tesla Despite Market Volatility",
                'excerpt': "Cathie Wood's firm increases Tesla holdings, citing autonomous vehicle and energy storage potential.",
                'source': 'MarketWatch',
                'date': 'Yesterday',
                'url': 'https://ark-invest.com/newsletters/',
                'content': "Cathie Wood explained: 'Tesla isn't just an electric vehicle company - it's the leading AI and robotics platform. While others see volatility, we see the future of transportation and energy.'"
            },
            {
                'title': "Wood Predicts Bitcoin Will Hit $1 Million by 2030",
                'excerpt': "The innovation investor maintains bullish outlook on cryptocurrency despite recent market turbulence.",
                'source': 'CoinDesk',
                'date': '3 days ago',
                'url': 'https://ark-invest.com/articles/analyst-research/bitcoin-price-targets/',
                'content': "According to Wood: 'Bitcoin represents the ultimate convergence of technology and finance. As institutional adoption accelerates and regulatory clarity emerges, we believe Bitcoin will reach $1 million per coin this decade.'"
            }
        ]
    elif "Marc Andreessen" in investor_name:
        return [
            {
                'title': "Marc Andreessen: 'AI Agents Will Transform Every Industry Within 5 Years'",
                'excerpt': "The Andreessen Horowitz co-founder believes AI agents represent the next major platform shift. 'We're seeing autonomous systems that can perform complex tasks end-to-end,' Andreessen stated during a recent Stanford lecture.",
                'source': 'TechCrunch',
                'date': 'Today',
                'url': 'https://a16z.com/ai-will-save-the-world/',
                'content': "Marc Andreessen said: 'AI agents represent the most significant technological shift since the smartphone revolution. These systems will fundamentally change how we work, how businesses operate, and how value is created in the economy.'"
            },
            {
                'title': "Andreessen Horowitz Launches $600M AI Fund, Marc Andreessen to Lead Strategy",
                'excerpt': "a16z announces new fund focused exclusively on artificial intelligence startups. Andreessen emphasized the fund's focus on infrastructure and enterprise applications.",
                'source': 'Forbes',
                'date': 'Yesterday', 
                'url': 'https://fortune.com/2024/03/06/vc-andreessen-horowitz-raise-billions-for-ai-two-funds/',
                'content': "According to Marc Andreessen: 'This fund represents our conviction that AI will create more economic value than any previous technology wave. We're betting on the entrepreneurs building the foundational technologies.'"
            },
            {
                'title': "Marc Andreessen on Crypto's Future: 'We're Still in the First Inning'",
                'excerpt': "The venture capitalist doubled down on cryptocurrency investments despite market volatility, citing long-term potential for decentralized systems.",
                'source': 'Wall Street Journal',
                'date': '2 days ago',
                'url': 'https://techcrunch.com/2024/12/19/the-promise-and-warning-of-truth-terminal-the-ai-bot-that-secured-50000-in-bitcoin-from-marc-andreessen/',
                'content': "Andreessen told reporters: 'Crypto represents programmable money and programmable law. The implications are so profound that we're still discovering what's possible.'"
            },
            {
                'title': "Marc Andreessen: Software Continues Eating the World, Now With AI",
                'excerpt': "In a comprehensive interview, the tech veteran reflects on his famous 2011 prediction and how artificial intelligence accelerates software's dominance.",
                'source': 'Bloomberg',
                'date': '3 days ago',
                'url': 'https://techcrunch.com/2024/10/22/marc-andreessen-says-ai-model-makers-are-in-a-race-to-the-bottom-and-its-not-god-for-business/',
                'content': "Marc Andreessen reflected: 'My 2011 prediction that software would eat the world has accelerated beyond my expectations. AI is now software eating software itself, creating unprecedented automation possibilities.'"
            },
            {
                'title': "Andreessen Horowitz Portfolio Company Anthropic Valued at $18B",
                'excerpt': "The AI safety company, backed by a16z, raises new funding round. Marc Andreessen praised the company's approach to developing safe AI systems.",
                'source': 'The Information',
                'date': '1 week ago', 
                'url': 'https://a16z.com/new-funds-new-era/',
                'content': "Commenting on the investment, Andreessen noted: 'Building AI systems that are both powerful and aligned with human values isn't just a technical challenge - it's an existential opportunity.'"
            }
        ]
    
    # Default news for other investors
    return [
        {
            'title': f"{investor_name} Backs New AI Startup in $50M Series A Round",
            'excerpt': "Leading venture capitalist announces major investment in artificial intelligence company focused on enterprise automation...",
            'source': 'TechCrunch',
            'date': 'Today',
            'url': 'https://techcrunch.com'
        },
        {
            'title': f"Exclusive: {investor_name} on the Future of Web3 and Crypto",
            'excerpt': "In a recent interview, the prominent investor shared insights on the evolving landscape of blockchain technology and decentralized finance...",
            'source': 'Forbes',
            'date': 'Yesterday',
            'url': 'https://forbes.com'
        },
        {
            'title': f"{investor_name}'s Portfolio Company Goes Public at $10B Valuation",
            'excerpt': "One of the earliest investments from the venture capital firm debuts on NASDAQ with strong opening performance...",
            'source': 'Wall Street Journal',
            'date': '2 days ago',
            'url': 'https://wsj.com'
        },
        {
            'title': f"Breaking: {investor_name} Joins Board of Unicorn Startup",
            'excerpt': "The respected investor brings decades of experience to fast-growing fintech company as it prepares for international expansion...",
            'source': 'Bloomberg',
            'date': '3 days ago',
            'url': 'https://bloomberg.com'
        },
        {
            'title': f"{investor_name} Predicts Major Shifts in Tech Investment Landscape",
            'excerpt': "Speaking at a recent conference, the investor outlined key trends that will shape venture capital decisions in the coming years...",
            'source': 'VentureBeat',
            'date': '5 days ago',
            'url': 'https://venturebeat.com'
        }
    ]


if __name__ == "__main__":
    # Test the news fetching
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing news fetching for Marc Andreessen...")
    news = fetch_investor_news("Marc Andreessen", limit=5)
    
    if news:
        print(f"\n📰 Found {len(news)} news articles:")
        for i, article in enumerate(news, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']} | Date: {article['date']}")
            print(f"   {article['excerpt']}")
            print(f"   URL: {article['url']}")
    else:
        print("No news found - using mock data")
        mock_news = get_mock_news("Marc Andreessen")
        for i, article in enumerate(mock_news, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']} | Date: {article['date']}")
            print(f"   {article['excerpt']}")