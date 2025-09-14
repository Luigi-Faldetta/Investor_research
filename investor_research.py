from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain_groq import ChatGroq
from typing import Tuple, List
import os
import time
import random
from output_parsers import InvestorProfile, PortfolioCompany, InvestmentInsights, insights_parser
from agents.investor_lookup_agent import lookup as investor_lookup_agent
from agents.portfolio_agent import discover_portfolio
from agents.content_agent import aggregate_content
from third_parties.twitter import fetch_recent_tweets
from third_parties.linkedin import fetch_linkedin_posts
from third_parties.medium import fetch_medium_articles
from third_parties.crunchbase import fetch_portfolio_data
from third_parties.news import fetch_investor_news


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


def search_investor_quotes(investor_name: str) -> List[dict]:
    """
    Search specifically for quotes from the investor.
    """
    try:
        from langchain_tavily import TavilySearch
        search = TavilySearch()
        
        # Search specifically for quotes
        search_queries = [
            f'"{investor_name}" "said" "investing" quote',
            f'"{investor_name}" interview quotes venture capital',
            f'"{investor_name}" famous quotes technology'
        ]
        
        quotes = []
        for query in search_queries[:2]:  # Limit to avoid API limits
            try:
                results = search.run(query)
                if isinstance(results, dict) and 'results' in results:
                    for item in results['results'][:3]:
                        content = item.get('content', '')
                        if content:
                            quotes.append({"text": content[:500], "source": "web"})
            except Exception as e:
                print(f"Quote search error: {e}")
                
        return quotes
    except Exception as e:
        print(f"Error searching for quotes: {e}")
        return []


def research_investor(name: str) -> Tuple[InvestorProfile, List[PortfolioCompany], InvestmentInsights, List[dict]]:
    """
    Main orchestration function that researches an investor and returns comprehensive insights.
    """
    
    # Quick access investors (mock data available)
    quick_access_investors = ["Marc Andreessen", "Mark Cuban", "Peter Thiel", "Paul Tudor Jones", "Cathie Wood"]
    use_mock_data = name in quick_access_investors
    
    # Step 1: Find investor profiles across platforms
    print(f"Searching for investor profiles for: {name}")
    investor_profiles = investor_lookup_agent(name=name, use_mock=use_mock_data)
    
    # Add delay between steps to prevent rate limiting
    time.sleep(1)
    
    # Step 2: Build investor profile
    profile = InvestorProfile(
        name=investor_profiles.get("name", name),
        firm=investor_profiles.get("firm", ""),
        title=investor_profiles.get("title", ""),
        bio=investor_profiles.get("bio", ""),
        profile_urls=investor_profiles.get("urls", {}),
        profile_image=investor_profiles.get("image", "")
    )
    
    # Step 3: Fetch portfolio companies
    print("Discovering portfolio companies...")
    time.sleep(1)  # Add delay before API-heavy operation
    portfolio_data = discover_portfolio(investor_profiles, use_mock=use_mock_data)
    portfolio = []
    
    for company_data in portfolio_data:
        # Ensure required fields have default values (empty strings)
        portfolio.append(PortfolioCompany(
            name=company_data.get("name", ""),
            sector=company_data.get("sector", ""),
            stage=company_data.get("stage") or "",  # Use 'or' to handle None
            investment_date=company_data.get("date") or company_data.get("investment_date") or "",  # Check both possible keys
            description=company_data.get("description", ""),
            investment_value=company_data.get("investment_value", 0),
            website=company_data.get("website", ""),
            stock_symbol=company_data.get("stock_symbol", ""),
            yahoo_finance_url=company_data.get("yahoo_finance_url", "")
        ))
    
    # Step 4: Aggregate recent content
    print("Aggregating recent social media content...")
    tweets = fetch_recent_tweets(investor_profiles.get("urls", {}).get("twitter", ""), mock=use_mock_data, investor_name=name)
    linkedin_posts = fetch_linkedin_posts(investor_profiles.get("urls", {}).get("linkedin", ""), mock=use_mock_data)
    # Pass investor name to get articles ABOUT them, not BY them
    medium_articles = fetch_medium_articles(
        investor_profiles.get("urls", {}).get("medium", ""), 
        mock=use_mock_data,
        investor_name=name
    )
    
    # Step 5: Fetch latest news
    print("Fetching latest news...")
    news = fetch_investor_news(name, limit=5, use_mock=use_mock_data)
    
    # Step 5b: Search for investor quotes if tweets are empty
    print("Searching for investor quotes...")
    investor_quotes = search_investor_quotes(name) if not tweets else []
    
    # Step 6: Generate AI insights
    print("Generating investment insights...")
    time.sleep(2)  # Longer delay before final AI processing
    # Combine tweets with quote search results if tweets are empty
    enhanced_tweets = tweets if tweets else investor_quotes
    insights = generate_investment_insights(
        profile=profile,
        portfolio=portfolio,
        tweets=enhanced_tweets,  # Use enhanced tweets
        linkedin_posts=linkedin_posts,
        medium_articles=medium_articles,
        news=news  # Pass news for quote extraction
    )
    
    return profile, portfolio, insights, news


def generate_investment_insights(
    profile: InvestorProfile,
    portfolio: List[PortfolioCompany],
    tweets: List[dict],
    linkedin_posts: List[dict],
    medium_articles: List[dict],
    news: List[dict] = None
) -> InvestmentInsights:
    """
    Use AI to analyze all data and generate investment insights.
    """
    
    # Prepare data for AI analysis
    portfolio_summary = "\n".join([
        f"- {company.name} ({company.sector}, {company.stage}): {company.description}"
        for company in portfolio[:10]  # Limit to recent 10
    ]) if portfolio else "No portfolio data available"
    
    tweets_summary = "\n".join([tweet.get("text", "") for tweet in tweets[:20]]) if tweets else "No recent tweets available"
    posts_summary = "\n".join([post.get("content", "") for post in linkedin_posts[:5]]) if linkedin_posts else "No LinkedIn posts available"
    articles_summary = "\n".join([
        f"{article.get('title', '')}: {article.get('excerpt', '')}"
        for article in medium_articles[:5]
    ]) if medium_articles else "No Medium articles available"
    
    # Add news summary for better quote extraction
    news_summary = ""
    if news:
        news_summary = "\n".join([
            f"{item.get('title', '')}: {item.get('content', '')}"
            for item in news[:5]
        ])
    
    insights_template = """
    Based on the following information about investor {investor_name} from {firm}:
    
    Portfolio Companies:
    {portfolio}
    
    Recent Tweets:
    {tweets}
    
    LinkedIn Posts:
    {posts}
    
    Medium Articles:
    {articles}
    
    Recent News:
    {news}
    
    Please generate:
    1. Investment themes (3-5 key themes)
    2. Sector focus areas
    3. Preferred investment stage
    4. Investment thesis summary
    5. Notable quotes - Look for actual quotes said BY {investor_name} in the provided content. 
       Return MAXIMUM 5 most meaningful quotes. These should be:
       - Direct quotes with quotation marks where {investor_name} is speaking
       - Statements that start with "{investor_name} said", "{investor_name} stated", "According to {investor_name}"
       - Tweets if they contain meaningful investment philosophy
       - Interview excerpts where {investor_name} is quoted
       Do NOT include: Headlines, article titles, descriptions ABOUT the investor, or paraphrased content.
       Prioritize quotes that reveal investment philosophy, strategy, or insights.
       If no direct quotes are found, return an empty list.
    6. 5 conversation icebreakers
    
    {format_instructions}
    """
    
    prompt_template = PromptTemplate(
        input_variables=["investor_name", "firm", "portfolio", "tweets", "posts", "articles", "news"],
        template=insights_template,
        partial_variables={"format_instructions": insights_parser.get_format_instructions()}
    )
    
    llm = ChatGroq(
        temperature=0,
        model="llama-3.3-70b-versatile",  # Current production model
        api_key=os.getenv("GROQ_API_KEY")
    )
    # Use rate-limited chain
    formatted_prompt = prompt_template.format(
        investor_name=profile.name,
        firm=profile.firm,
        portfolio=portfolio_summary,
        tweets=tweets_summary,
        posts=posts_summary,
        articles=articles_summary,
        news=news_summary
    )
    
    # Make rate-limited call
    response = rate_limited_llm_call(llm, formatted_prompt)
    insights = insights_parser.parse(response.content)
    
    return insights


if __name__ == "__main__":
    load_dotenv()
    
    print("Investor Research Assistant")
    profile, portfolio, insights, news = research_investor(name="Marc Andreessen")