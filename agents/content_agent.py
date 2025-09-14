from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub


def aggregate_content(investor_profiles: dict) -> Dict[str, List]:
    """
    Aggregate recent content from various platforms.
    Returns dict with tweets, posts, articles.
    """
    
    # For mock mode, return sample content
    if True:  # Mock mode
        return {
            "tweets": [
                {"text": "AI will fundamentally transform every industry in the next decade", "date": "2024-01-15"},
                {"text": "The future of software is AI agents working together", "date": "2024-01-14"},
                {"text": "Crypto infrastructure is finally ready for mainstream adoption", "date": "2024-01-13"}
            ],
            "linkedin_posts": [
                {"content": "Thoughts on the current state of venture capital...", "date": "2024-01-10"}
            ],
            "medium_articles": [
                {"title": "Why Software Is Eating the World - 10 Years Later", "excerpt": "A decade ago..."}
            ]
        }
    
    # Real implementation would aggregate content from multiple sources
    return {}