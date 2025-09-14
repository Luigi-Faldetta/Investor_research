"""
Alternative portfolio data fetching using free sources.
No Crunchbase API required.
"""
import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()


def fetch_portfolio_from_web(investor_name: str, firm_name: str = None) -> List[Dict]:
    """
    Fetch portfolio data using web search and public sources.
    This is a free alternative to Crunchbase API.
    """
    try:
        search = TavilySearch()
        portfolio_companies = []
        
        # Search strategies:
        # 1. Search the VC firm's website for portfolio page
        if firm_name:
            firm_query = f'"{firm_name}" portfolio companies'
            firm_results = search.run(firm_query)
            # Parse results to extract company names
            
        # 2. Search for investor + portfolio mentions
        investor_query = f'"{investor_name}" invested in backed funded portfolio'
        investor_results = search.run(investor_query)
        
        # 3. Search news articles for recent investments
        news_query = f'"{investor_name}" leads investment round funding'
        news_results = search.run(news_query)
        
        # 4. Check AngelList (often has public data)
        angellist_query = f'site:angel.co "{investor_name}" investments'
        angellist_results = search.run(angellist_query)
        
        # Parse and combine results
        # In production, you would parse these results to extract:
        # - Company names
        # - Investment dates
        # - Funding amounts
        # - Sectors
        
        return portfolio_companies
        
    except Exception as e:
        print(f"Error fetching portfolio from web: {e}")
        return []


def fetch_from_sec_edgar(investor_name: str) -> List[Dict]:
    """
    Fetch investment data from SEC EDGAR database (free).
    Useful for funds that file Form D or Form ADV.
    """
    # SEC EDGAR API is completely free
    # Would implement actual EDGAR search here
    # Form D: Private placement investments
    # Form ADV: Investment advisor disclosures
    
    return []


def fetch_from_wikipedia(investor_name: str) -> List[Dict]:
    """
    Many prominent VCs have Wikipedia pages with portfolio lists.
    """
    try:
        search = TavilySearch()
        wiki_query = f'site:wikipedia.org "{investor_name}" investments portfolio'
        results = search.run(wiki_query)
        # Parse Wikipedia content for portfolio companies
        return []
    except:
        return []


def aggregate_portfolio_data(investor_name: str, firm_name: str = None) -> List[Dict]:
    """
    Aggregate portfolio data from multiple free sources.
    """
    all_companies = []
    
    # Try multiple sources
    web_portfolio = fetch_portfolio_from_web(investor_name, firm_name)
    sec_portfolio = fetch_from_sec_edgar(investor_name)
    wiki_portfolio = fetch_from_wikipedia(investor_name)
    
    # Combine and deduplicate
    all_companies.extend(web_portfolio)
    all_companies.extend(sec_portfolio)
    all_companies.extend(wiki_portfolio)
    
    # Remove duplicates based on company name
    seen = set()
    unique_companies = []
    for company in all_companies:
        if company.get('name') not in seen:
            seen.add(company.get('name'))
            unique_companies.append(company)
    
    return unique_companies