from langchain_tavily import TavilySearch


def search_investor_profiles(query: str):
    """
    Search for investor profiles across platforms.
    """
    # For mock mode, return placeholder
    if True:  # Mock mode
        return f"Found profiles for {query}"
    
    search = TavilySearch()
    res = search.run(query)
    return res