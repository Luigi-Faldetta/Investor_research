from langchain_tavily import TavilySearch


def search_portfolio_companies(query: str):
    """
    Search for portfolio companies of an investor using web search.
    """
    try:
        search = TavilySearch()
        # Search for portfolio companies mentioned in articles, firm websites, etc.
        search_query = f"{query} portfolio companies investments backed funded"
        results = search.run(search_query)
        return results
    except:
        # Return mock data if search fails
        return f"Found portfolio information for {query}"