from typing import List, Dict
import os
import time
import random
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.portfolio_tools import search_portfolio_companies
from third_parties.company_links import enhance_portfolio_companies


def rate_limited_llm_call(llm, prompt, max_retries=3):
    """
    Make a rate-limited LLM call with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            # Add a small delay before each call
            time.sleep(random.uniform(0.5, 1.5))
            return llm.invoke(prompt)
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit, waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    print("Max retries exceeded, skipping this request")
                    raise e
            else:
                raise e
    return None


def get_mock_portfolio_for_investor(investor_name: str) -> List[Dict]:
    """
    Get mock portfolio data for investors when API limits are hit
    """
    if "Peter Thiel" in investor_name:
        return [
            {"name": "PayPal", "sector": "Fintech", "stage": "Co-founder", "date": "1998", "description": "Digital payments platform"},
            {"name": "Palantir", "sector": "Software", "stage": "Co-founder", "date": "2003", "description": "Big data analytics"},
            {"name": "Meta", "sector": "Social Media", "stage": "Series A", "date": "2004", "description": "Social networking platform"},
            {"name": "SpaceX", "sector": "Aerospace", "stage": "Series A", "date": "2008", "description": "Space exploration company"},
            {"name": "Stripe", "sector": "Fintech", "stage": "Series B", "date": "2011", "description": "Online payments infrastructure"}
        ]
    elif "Marc Andreessen" in investor_name:
        return [
            {"name": "Facebook", "sector": "Social Media", "stage": "Series A", "date": "2004", "description": "Social networking platform"},
            {"name": "Twitter", "sector": "Social Media", "stage": "Series A", "date": "2009", "description": "Microblogging platform"},
            {"name": "GitHub", "sector": "Software", "stage": "Series A", "date": "2012", "description": "Code hosting platform"},
            {"name": "Pinterest", "sector": "Social Media", "stage": "Series A", "date": "2011", "description": "Visual discovery platform"},
            {"name": "Coinbase", "sector": "Cryptocurrency", "stage": "Series B", "date": "2013", "description": "Cryptocurrency exchange"}
        ]
    else:
        return [
            {"name": "TechCorp", "sector": "Technology", "stage": "Series A", "date": "2023", "description": "AI-powered solutions"},
            {"name": "DataFlow", "sector": "Software", "stage": "Series B", "date": "2022", "description": "Data analytics platform"},
            {"name": "CloudNet", "sector": "Cloud Services", "stage": "Seed", "date": "2024", "description": "Cloud infrastructure"}
        ]


def discover_portfolio(investor_profiles: dict, use_mock: bool = True) -> List[Dict]:
    """
    Discover portfolio companies for the given investor.
    Returns a list of portfolio companies with details.
    Can use web search instead of Crunchbase API.
    """
    
    # For mock mode or when Crunchbase is not available
    if use_mock:
        if "Mark Cuban" in investor_profiles.get("name", ""):
            return [
                {
                    "name": "Magnolia Pictures",
                    "sector": "Entertainment",
                    "stage": "Acquisition",
                    "date": "2003",
                    "description": "Independent film production and distribution company",
                    "investment_value": 30000000,
                    "website": "https://magpictures.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "AXS TV",
                    "sector": "Media & Broadcasting",
                    "stage": "Investment",
                    "date": "2012",
                    "description": "Music and entertainment television network",
                    "investment_value": 25000000,
                    "website": "https://axs.tv",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Cost Plus Drugs",
                    "sector": "Healthcare",
                    "stage": "Founder",
                    "date": "2022",
                    "description": "Online pharmacy offering prescription drugs at cost plus 15%",
                    "investment_value": 50000000,
                    "website": "https://costplusdrugs.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Sharespost (Forge Global)",
                    "sector": "Fintech",
                    "stage": "Series B",
                    "date": "2010",
                    "description": "Private company stock trading platform, now part of Forge Global",
                    "investment_value": 5000000,
                    "website": "https://forgeglobal.com",
                    "stock_symbol": "FRGE",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/FRGE"
                },
                {
                    "name": "Appriss",
                    "sector": "Software",
                    "stage": "Series A",
                    "date": "2008",
                    "description": "Data analytics and information services",
                    "investment_value": 3000000,
                    "website": "https://appriss.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Cyberdust",
                    "sector": "Social Media",
                    "stage": "Seed",
                    "date": "2014",
                    "description": "Ephemeral messaging application",
                    "investment_value": 2000000,
                    "website": "https://cyberdust.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Netflix (Early Investment)",
                    "sector": "Streaming Media",
                    "stage": "Early Investment",
                    "date": "2004",
                    "description": "DVD-by-mail service transitioning to streaming",
                    "investment_value": 1000000,
                    "website": "https://netflix.com",
                    "stock_symbol": "NFLX",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/NFLX"
                }
            ]
        elif "Peter Thiel" in investor_profiles.get("name", ""):
            return [
                {
                    "name": "Facebook (Meta)",
                    "sector": "Social Media",
                    "stage": "Series A",
                    "date": "2004",
                    "description": "Global social networking platform and metaverse company",
                    "investment_value": 500000,
                    "website": "https://meta.com",
                    "stock_symbol": "META",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/META"
                },
                {
                    "name": "SpaceX",
                    "sector": "Aerospace",
                    "stage": "Series A",
                    "date": "2008",
                    "description": "Private space exploration and satellite internet company",
                    "investment_value": 20000000,
                    "website": "https://spacex.com",
                    "stock_symbol": "SPAX.PVT",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/SPAX.PVT/"
                },
                {
                    "name": "Stripe",
                    "sector": "Fintech",
                    "stage": "Series B",
                    "date": "2012",
                    "description": "Online payment processing platform",
                    "investment_value": 10000000,
                    "website": "https://stripe.com",
                    "stock_symbol": "STRI.PVT",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/STRI.PVT/"
                },
                {
                    "name": "Airbnb",
                    "sector": "Travel & Hospitality",
                    "stage": "Series A",
                    "date": "2009",
                    "description": "Home-sharing and accommodation marketplace",
                    "investment_value": 7000000,
                    "website": "https://airbnb.com",
                    "stock_symbol": "ABNB",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/ABNB"
                },
                {
                    "name": "LinkedIn",
                    "sector": "Professional Networking",
                    "stage": "Series A",
                    "date": "2004",
                    "description": "Professional networking and career development platform",
                    "investment_value": 1000000,
                    "website": "https://linkedin.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Palantir",
                    "sector": "Data Analytics",
                    "stage": "Co-founder",
                    "date": "2003",
                    "description": "Big data analytics platform for government and enterprises",
                    "investment_value": 200000000,
                    "website": "https://palantir.com",
                    "stock_symbol": "PLTR",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/PLTR"
                },
                {
                    "name": "Anduril",
                    "sector": "Defense Technology",
                    "stage": "Series A",
                    "date": "2017",
                    "description": "Autonomous defense systems and military technology",
                    "investment_value": 50000000,
                    "website": "https://anduril.com",
                    "stock_symbol": "ANIN.PVT",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/ANIN.PVT/"
                },
                {
                    "name": "Roblox",
                    "sector": "Gaming",
                    "stage": "Pre-IPO",
                    "date": "2020",
                    "description": "Online game platform and game creation system",
                    "investment_value": 25000000,
                    "website": "https://roblox.com",
                    "stock_symbol": "RBLX",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/RBLX"
                }
            ]
        elif "Paul Tudor Jones" in investor_profiles.get("name", ""):
            return [
                {
                    "name": "Robin Hood Foundation",
                    "sector": "Non-profit",
                    "stage": "Founder",
                    "date": "1988",
                    "description": "Anti-poverty non-profit organization",
                    "investment_value": 100000000,
                    "website": "https://robinhood.org",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "JUST Capital",
                    "sector": "ESG Research",
                    "stage": "Founder",
                    "date": "2013",
                    "description": "Research organization ranking companies on stakeholder performance",
                    "investment_value": 50000000,
                    "website": "https://justcapital.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Teach for America",
                    "sector": "Education",
                    "stage": "Major Donor",
                    "date": "1990",
                    "description": "Educational leadership program placing teachers in high-need schools",
                    "investment_value": 25000000,
                    "website": "https://teachforamerica.org",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Malaria No More",
                    "sector": "Healthcare/Non-profit",
                    "stage": "Major Donor",
                    "date": "2006",
                    "description": "Global malaria eradication initiative",
                    "investment_value": 15000000,
                    "website": "https://malarianomore.org",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Sustainable Fisheries Partnership",
                    "sector": "Environmental",
                    "stage": "Donor",
                    "date": "2006",
                    "description": "Ocean conservation and sustainable fishing practices",
                    "investment_value": 10000000,
                    "website": "https://sustainablefish.org",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Gold ETF Holdings",
                    "sector": "Commodities",
                    "stage": "Public Investment",
                    "date": "2020",
                    "description": "Gold exchange-traded fund for inflation hedge",
                    "investment_value": 200000000,
                    "website": "https://spdrgoldshares.com",
                    "stock_symbol": "GLD",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/GLD"
                },
                {
                    "name": "Bitcoin Holdings",
                    "sector": "Cryptocurrency",
                    "stage": "Direct Investment",
                    "date": "2021",
                    "description": "Bitcoin allocation for portfolio diversification",
                    "investment_value": 150000000,
                    "website": "https://bitcoin.org",
                    "stock_symbol": "BTC-USD",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/BTC-USD"
                }
            ]
        elif "Cathie Wood" in investor_profiles.get("name", ""):
            return [
                {
                    "name": "Tesla",
                    "sector": "Electric Vehicles",
                    "stage": "Public Investment",
                    "date": "2016",
                    "description": "Electric vehicle and clean energy company",
                    "investment_value": 2000000000,
                    "website": "https://tesla.com",
                    "stock_symbol": "TSLA",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/TSLA"
                },
                {
                    "name": "Zoom",
                    "sector": "Communication Technology",
                    "stage": "Public Investment",
                    "date": "2019",
                    "description": "Video conferencing and communications platform",
                    "investment_value": 500000000,
                    "website": "https://zoom.us",
                    "stock_symbol": "ZM",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/ZM"
                },
                {
                    "name": "Square (Block)",
                    "sector": "Fintech",
                    "stage": "Public Investment",
                    "date": "2018",
                    "description": "Digital payments and financial services platform",
                    "investment_value": 800000000,
                    "website": "https://block.xyz",
                    "stock_symbol": "SQ",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/SQ"
                },
                {
                    "name": "Roku",
                    "sector": "Streaming Media",
                    "stage": "Public Investment",
                    "date": "2017",
                    "description": "Streaming platform and connected TV operating system",
                    "investment_value": 400000000,
                    "website": "https://roku.com",
                    "stock_symbol": "ROKU",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/ROKU"
                },
                {
                    "name": "Coinbase",
                    "sector": "Cryptocurrency",
                    "stage": "Pre-IPO/Public",
                    "date": "2020",
                    "description": "Cryptocurrency exchange and trading platform",
                    "investment_value": 600000000,
                    "website": "https://coinbase.com",
                    "stock_symbol": "COIN",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/COIN"
                },
                {
                    "name": "Unity Software",
                    "sector": "Gaming Technology",
                    "stage": "Public Investment",
                    "date": "2020",
                    "description": "Real-time 3D development platform",
                    "investment_value": 300000000,
                    "website": "https://unity.com",
                    "stock_symbol": "U",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/U"
                },
                {
                    "name": "10x Genomics",
                    "sector": "Biotechnology",
                    "stage": "Public Investment",
                    "date": "2019",
                    "description": "Life sciences technology company",
                    "investment_value": 250000000,
                    "website": "https://10xgenomics.com",
                    "stock_symbol": "TXG",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/TXG"
                },
                {
                    "name": "UiPath",
                    "sector": "Automation Software",
                    "stage": "Public Investment",
                    "date": "2021",
                    "description": "Robotic process automation platform",
                    "investment_value": 180000000,
                    "website": "https://uipath.com",
                    "stock_symbol": "PATH",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/PATH"
                },
                {
                    "name": "Teladoc Health",
                    "sector": "Telemedicine",
                    "stage": "Public Investment",
                    "date": "2020",
                    "description": "Virtual healthcare and telemedicine platform",
                    "investment_value": 320000000,
                    "website": "https://teladoc.com",
                    "stock_symbol": "TDOC",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/TDOC"
                }
            ]
        elif "Marc Andreessen" in investor_profiles.get("name", ""):
            return [
                {
                    "name": "Meta (Facebook)",
                    "sector": "Social Media",
                    "stage": "Series A",
                    "date": "2004",
                    "description": "Global social networking platform connecting billions of users worldwide",
                    "investment_value": 500000,  # $500K seed investment
                    "website": "https://meta.com",
                    "stock_symbol": "META",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/META"
                },
                {
                    "name": "Twitter",
                    "sector": "Social Media", 
                    "stage": "Series A",
                    "date": "2009",
                    "description": "Real-time microblogging and social networking service",
                    "investment_value": 50000000,  # $50M
                    "website": "https://twitter.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Coinbase",
                    "sector": "Cryptocurrency",
                    "stage": "Series B",
                    "date": "2013",
                    "description": "Leading cryptocurrency exchange and digital wallet platform",
                    "investment_value": 75000000,  # $75M
                    "website": "https://coinbase.com",
                    "stock_symbol": "COIN",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/COIN"
                },
                {
                    "name": "GitHub",
                    "sector": "Software Development",
                    "stage": "Series A",
                    "date": "2012",
                    "description": "World's largest code hosting platform for version control and collaboration",
                    "investment_value": 100000000,  # $100M
                    "website": "https://github.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Airbnb",
                    "sector": "Travel & Hospitality",
                    "stage": "Series A",
                    "date": "2009",
                    "description": "Global marketplace for unique accommodations and experiences",
                    "investment_value": 7200000,  # $7.2M
                    "website": "https://airbnb.com",
                    "stock_symbol": "ABNB",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/ABNB"
                },
                {
                    "name": "Lyft",
                    "sector": "Transportation",
                    "stage": "Series C",
                    "date": "2013",
                    "description": "Ridesharing platform transforming urban transportation",
                    "investment_value": 60000000,  # $60M
                    "website": "https://lyft.com",
                    "stock_symbol": "LYFT", 
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/LYFT"
                },
                {
                    "name": "Pinterest",
                    "sector": "Social Media",
                    "stage": "Series A",
                    "date": "2011",
                    "description": "Visual discovery platform for ideas and inspiration",
                    "investment_value": 45000000,  # $45M
                    "website": "https://pinterest.com",
                    "stock_symbol": "PINS",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/PINS"
                },
                {
                    "name": "Instacart",
                    "sector": "E-commerce",
                    "stage": "Series A",
                    "date": "2012",
                    "description": "On-demand grocery delivery and pickup service",
                    "investment_value": 44000000,  # $44M
                    "website": "https://instacart.com",
                    "stock_symbol": "CART",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/CART"
                },
                {
                    "name": "Slack",
                    "sector": "Enterprise Software",
                    "stage": "Series A",
                    "date": "2014",
                    "description": "Business communication platform revolutionizing workplace collaboration",
                    "investment_value": 50000000,  # $50M
                    "website": "https://slack.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                },
                {
                    "name": "Okta",
                    "sector": "Cybersecurity",
                    "stage": "Series A",
                    "date": "2011",
                    "description": "Identity and access management platform for enterprises",
                    "investment_value": 25000000,  # $25M
                    "website": "https://okta.com",
                    "stock_symbol": "OKTA",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/OKTA"
                },
                {
                    "name": "Box",
                    "sector": "Cloud Storage",
                    "stage": "Series A",
                    "date": "2010",
                    "description": "Cloud content management platform for businesses",
                    "investment_value": 48000000,  # $48M
                    "website": "https://box.com",
                    "stock_symbol": "BOX",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/BOX"
                },
                {
                    "name": "Databricks",
                    "sector": "Data Analytics",
                    "stage": "Series B",
                    "date": "2017",
                    "description": "Unified data analytics platform for big data and machine learning",
                    "investment_value": 120000000,  # $120M
                    "website": "https://databricks.com",
                    "stock_symbol": "DATB.PVT",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/DATB.PVT/"
                },
                {
                    "name": "Stripe",
                    "sector": "Fintech",
                    "stage": "Series A",
                    "date": "2012",
                    "description": "Online payment processing platform for internet businesses",
                    "investment_value": 70000000,  # $70M
                    "website": "https://stripe.com",
                    "stock_symbol": "STRI.PVT",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/STRI.PVT/"
                },
                {
                    "name": "Clubhouse Media Group",
                    "sector": "Social Audio",
                    "stage": "Series B",
                    "date": "2021",
                    "description": "Audio-based social networking platform for live conversations",
                    "investment_value": 35000000,  # $35M
                    "website": "https://clubhouse.com",
                    "stock_symbol": "CMGR",
                    "yahoo_finance_url": "https://finance.yahoo.com/quote/CMGR/"
                },
                {
                    "name": "OpenAI", 
                    "sector": "Artificial Intelligence",
                    "stage": "Investment",
                    "date": "2019",
                    "description": "AI research company developing GPT models and ChatGPT",
                    "investment_value": 300000000,  # $300M
                    "website": "https://openai.com",
                    "stock_symbol": "",
                    "yahoo_finance_url": ""
                }
            ]
        
        # Default portfolio for other investors
        return [
            {
                "name": "TechStartup Inc",
                "sector": "SaaS",
                "stage": "Series A",
                "date": "2023",
                "description": "B2B software platform"
            },
            {
                "name": "AI Solutions",
                "sector": "Artificial Intelligence",
                "stage": "Seed",
                "date": "2024",
                "description": "Machine learning infrastructure"
            },
            {
                "name": "FinTech Pro",
                "sector": "Financial Technology",
                "stage": "Series B",
                "date": "2023",
                "description": "Digital payments platform"
            }
        ]
    
    # Real implementation using web search and AI extraction
    llm = ChatGoogleGenerativeAI(
        temperature=0, 
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    investor_name = investor_profiles.get("name", "")
    firm = investor_profiles.get("firm", "")
    
    print(f"Searching for portfolio companies for {investor_name} from {firm}")
    
    # Use multiple targeted searches
    from langchain_tavily import TavilySearch
    search = TavilySearch()
    
    portfolio_companies = []
    all_search_results = []
    
    # Targeted search strategies
    search_queries = [
        f'"{investor_name}" invested in funded backed companies',
        f'"{firm}" portfolio companies list',
        f'{investor_name} investments startup companies',
        f'site:crunchbase.com "{investor_name}" investments',
        f'"{firm}" recent investments 2023 2024'
    ]
    
    # Perform searches and collect results
    for query in search_queries:
        try:
            print(f"Searching: {query}")
            results = search.run(query)
            
            # Tavily returns a dict with 'results' key containing search results
            if isinstance(results, dict) and 'results' in results:
                search_items = results['results']
                if search_items and len(search_items) > 0:
                    # Extract content from search results
                    content_pieces = []
                    for item in search_items[:5]:  # Use top 5 results per query
                        title = item.get('title', '')
                        content = item.get('content', '')
                        url = item.get('url', '')
                        if content:
                            content_pieces.append(f"Title: {title}\nContent: {content}\nURL: {url}\n")
                    
                    if content_pieces:
                        combined_content = "\n".join(content_pieces)
                        all_search_results.append(combined_content)
                        print(f"Found {len(combined_content)} characters from {len(search_items)} results")
                    else:
                        print("No content found in search results")
                else:
                    print("No search results returned")
            else:
                print(f"Unexpected results format: {type(results)}")
                # Check if it's a Tavily API limit error
                if isinstance(results, dict) and 'error' in results:
                    error_msg = str(results.get('error', ''))
                    if 'usage limit' in error_msg.lower() or '432' in error_msg:
                        print("⚠️ Tavily API limit reached - falling back to mock data")
                        return get_mock_portfolio_for_investor(investor_name)
                
        except Exception as e:
            print(f"Search error for '{query}': {e}")
            # If we get consistent errors, fall back to mock data
            if 'usage limit' in str(e).lower():
                print("⚠️ Tavily API limit reached - falling back to mock data")
                return get_mock_portfolio_for_investor(investor_name)
    
    if all_search_results:
        # Combine search results for analysis
        combined_results = "\n\n".join(all_search_results[:2])  # Use top 2 queries
        
        # Use structured prompt for better extraction
        extraction_prompt = f"""
        You are analyzing search results about {investor_name}'s investment portfolio. 
        Extract REAL company names and investment details from these search results:

        SEARCH RESULTS:
        {combined_results[:4000]}  # Limit to prevent token overflow
        
        Please extract portfolio companies in this EXACT JSON format:
        [
            {{
                "name": "Actual Company Name",
                "sector": "Industry sector",
                "stage": "Investment stage or round (Seed, Series A, B, C, etc.)",
                "date": "Year of investment",
                "description": "Brief company description",
                "investment_value": 0
            }}
        ]
        
        IMPORTANT INSTRUCTIONS:
        1. Only extract REAL companies mentioned in the search results
        2. For investment_value, look for:
           - Dollar amounts like "$10 million", "$50M", "raised $100 million"
           - Funding round sizes like "Series B of $75 million"
           - Terms like "led a $X investment", "participated in $X round"
           - Convert text amounts to numbers: "$10 million" = 10000000, "$2.5B" = 2500000000
           - If no amount found, use 0
        3. Common patterns to look for:
           - "{investor_name} led/participated in a $X [round/investment]"
           - "raised $X from investors including {investor_name}"
           - "{firm} invested $X in [company]"
           - "funding round of $X"
        4. Do not make up or invent companies or amounts
        5. If no clear companies are found, return an empty list []
        6. Focus on the most prominent/recent investments
        7. Limit to maximum 15 companies
        
        Example extraction:
        If text says "Andreessen Horowitz led a $150 million Series C round in Clubhouse"
        Return: {{"name": "Clubhouse", "sector": "Social Media", "stage": "Series C", "date": "2021", "description": "Audio social platform", "investment_value": 150000000}}
        """
        
        try:
            print("Using AI to extract portfolio companies...")
            response = rate_limited_llm_call(llm, extraction_prompt)
            
            # Try to parse JSON response
            import json
            import re
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Find JSON in the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    parsed_companies = json.loads(json_str)
                    
                    # Validate and clean the data
                    for company in parsed_companies:
                        if (company.get('name') and 
                            company['name'] != "Actual Company Name" and
                            len(company['name']) > 2):
                            # Ensure all required fields are present, use empty string only if None or missing
                            portfolio_companies.append({
                                "name": company.get('name', ''),
                                "sector": company.get('sector', '') or '',  # Empty string only if None or missing
                                "stage": company.get('stage', '') or '',
                                "date": company.get('date', '') or '',
                                "description": (company.get('description', '') or '')[:200],
                                "investment_value": company.get('investment_value', 0)
                            })
                    
                    print(f"Successfully extracted {len(portfolio_companies)} companies")
                    
                except json.JSONDecodeError:
                    print("Could not parse JSON response, trying text parsing...")
                    # Fallback: parse as text
                    lines = response_text.split('\n')
                    current_company = {}
                    
                    for line in lines:
                        if 'name' in line.lower() and ':' in line:
                            if current_company and current_company.get('name'):
                                # Only set empty string if field doesn't exist or is None
                                current_company.setdefault('sector', '')
                                current_company.setdefault('stage', '')
                                current_company.setdefault('date', '')
                                current_company.setdefault('description', '')
                                current_company.setdefault('investment_value', 0)
                                # Handle None values
                                for key in ['sector', 'stage', 'date', 'description']:
                                    if current_company[key] is None:
                                        current_company[key] = ''
                                portfolio_companies.append(current_company)
                            current_company = {'name': line.split(':')[-1].strip().strip('"')}
                        elif 'sector' in line.lower() and ':' in line:
                            current_company['sector'] = line.split(':')[-1].strip().strip('"')
                        elif 'stage' in line.lower() and ':' in line:
                            current_company['stage'] = line.split(':')[-1].strip().strip('"')
                        elif 'date' in line.lower() and ':' in line:
                            current_company['date'] = line.split(':')[-1].strip().strip('"')
                        elif 'description' in line.lower() and ':' in line:
                            current_company['description'] = line.split(':')[-1].strip().strip('"')
                        elif 'investment_value' in line.lower() and ':' in line:
                            value_str = line.split(':')[-1].strip().strip('"')
                            try:
                                current_company['investment_value'] = float(value_str)
                            except:
                                current_company['investment_value'] = 0
                    
                    if current_company and current_company.get('name'):
                        # Only set empty string if field doesn't exist or is None
                        current_company.setdefault('sector', '')
                        current_company.setdefault('stage', '')
                        current_company.setdefault('date', '')
                        current_company.setdefault('description', '')
                        current_company.setdefault('investment_value', 0)
                        # Handle None values
                        for key in ['sector', 'stage', 'date', 'description']:
                            if current_company[key] is None:
                                current_company[key] = ''
                        portfolio_companies.append(current_company)
                        
            print(f"Final portfolio count: {len(portfolio_companies)}")
            for company in portfolio_companies[:3]:  # Show first 3
                investment_val = company.get('investment_value', 0)
                if investment_val > 0:
                    print(f"  - {company.get('name', 'Unknown')} ({company.get('sector', 'Unknown')}): ${investment_val/1000000:.1f}M")
                else:
                    print(f"  - {company.get('name', 'Unknown')} ({company.get('sector', 'Unknown')}): No amount found")
                        
        except Exception as e:
            print(f"Error in AI extraction: {e}")
    
    else:
        print("No substantial search results found - using mock data as fallback")
        portfolio_companies = get_mock_portfolio_for_investor(investor_profiles.get("name", ""))
    
    # Enhance companies with website and stock links
    if portfolio_companies:
        try:
            print(f"\n🔗 Enhancing {len(portfolio_companies)} companies with website and stock links...")
            enhanced_companies = enhance_portfolio_companies(portfolio_companies)
            return enhanced_companies
        except Exception as e:
            print(f"Error enhancing companies: {e}")
            return portfolio_companies
    
    return portfolio_companies