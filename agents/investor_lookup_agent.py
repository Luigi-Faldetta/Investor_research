from dotenv import load_dotenv
load_dotenv()

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
from tools.search_tools import search_investor_profiles
from tools.smart_profile_finder import smart_find_all_profiles


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


def lookup(name: str, use_mock: bool = False) -> dict:
    """
    Find investor profiles across multiple platforms.
    Returns a dict with profile URLs and basic information.
    """
    
    if use_mock:
        mock_profiles = {
            "Marc Andreessen": {
                "name": "Marc Andreessen",
                "firm": "Andreessen Horowitz (a16z)",
                "title": "Co-founder and General Partner",
                "bio": "Co-founder of Netscape and Andreessen Horowitz, one of Silicon Valley's most influential venture capitalists. Pioneer of the web browser revolution and leading voice in software, crypto, and AI investments. Known for the famous quote 'Software is eating the world.'",
                "urls": {
                    "twitter": "https://twitter.com/pmarca",
                    "linkedin": "https://www.linkedin.com/in/marcandreessen",
                    "crunchbase": "https://www.crunchbase.com/person/marc-andreessen",
                    "medium": "https://pmarca.medium.com",
                    "firm": "https://a16z.com"
                },
                "image": "https://res.cloudinary.com/doqmqgbym/image/upload/v1757154244/investors/dynamic/investors/dynamic/marc_andreessen.jpg"
            },
            "Mark Cuban": {
                "name": "Mark Cuban",
                "firm": "Mark Cuban Companies",
                "title": "Owner and Principal Investor",
                "bio": "Serial entrepreneur, investor, and owner of the Dallas Mavericks. Built and sold Broadcast.com to Yahoo for $5.7 billion. Known for his appearances on Shark Tank and investments in early-stage startups across technology, media, and consumer products.",
                "urls": {
                    "twitter": "https://twitter.com/mcuban",
                    "linkedin": "https://www.linkedin.com/in/markcuban",
                    "crunchbase": "https://www.crunchbase.com/person/mark-cuban",
                    "medium": "https://markcuban.medium.com",
                    "firm": "https://markcubancompanies.com"
                },
                "image": "https://res.cloudinary.com/doqmqgbym/image/upload/v1756815654/investors/dynamic/investors/dynamic/mark_cuban.jpg"
            },
            "Peter Thiel": {
                "name": "Peter Thiel",
                "firm": "Founders Fund",
                "title": "Co-founder and Managing Partner",
                "bio": "Co-founder of PayPal and Palantir, and founding partner of Founders Fund. Early Facebook investor and author of 'Zero to One'. Known for contrarian thinking and investments in breakthrough technologies including SpaceX, Airbnb, and Stripe.",
                "urls": {
                    "twitter": "https://twitter.com/peterthiel",
                    "linkedin": "https://www.linkedin.com/in/peterthiel",
                    "crunchbase": "https://www.crunchbase.com/person/peter-thiel",
                    "medium": "https://peterthiel.medium.com",
                    "firm": "https://foundersfund.com"
                },
                "image": "https://res.cloudinary.com/doqmqgbym/image/upload/v1757155912/investors/dynamic/investors/dynamic/peter_thiel.jpg"
            },
            "Paul Tudor Jones": {
                "name": "Paul Tudor Jones",
                "firm": "Tudor Investment Corporation",
                "title": "Founder and Chief Investment Officer",
                "bio": "Legendary macro trader and hedge fund manager who founded Tudor Investment Corporation. Known for predicting and profiting from the 1987 stock market crash. Increasingly active in venture capital and impact investing, particularly in education and environmental initiatives.",
                "urls": {
                    "twitter": "https://twitter.com/paultudorjones",
                    "linkedin": "https://www.linkedin.com/in/paultudorjones",
                    "crunchbase": "https://www.crunchbase.com/person/paul-tudor-jones-ii",
                    "medium": "https://paultudorjones.medium.com",
                    "firm": "https://tudorinvestment.com"
                },
                "image": "https://res.cloudinary.com/doqmqgbym/image/upload/v1756826796/investors/dynamic/investors/dynamic/paul_tudor_jones.jpg"
            },
            "Cathie Wood": {
                "name": "Cathie Wood",
                "firm": "ARK Invest",
                "title": "Founder and CEO",
                "bio": "Founder and CEO of ARK Invest, focused on disruptive innovation investing. Known for bold predictions and concentrated bets on transformative technologies including genomics, artificial intelligence, energy storage, and space exploration. Strong advocate for Tesla and cryptocurrency.",
                "urls": {
                    "twitter": "https://twitter.com/cathiedwood",
                    "linkedin": "https://www.linkedin.com/in/cathie-wood-ark-invest",
                    "crunchbase": "https://www.crunchbase.com/person/cathie-wood",
                    "medium": "https://cathiewood.medium.com",
                    "firm": "https://ark-invest.com"
                },
                "image": "https://res.cloudinary.com/doqmqgbym/image/upload/v1756815661/investors/dynamic/investors/dynamic/cathie_wood.jpg"
            },
            "default": {
                "name": name,
                "firm": "Sample Ventures",
                "title": "General Partner",
                "bio": "Experienced investor focusing on early-stage startups",
                "urls": {
                    "twitter": "https://twitter.com/sample",
                    "linkedin": "https://www.linkedin.com/in/sample",
                    "crunchbase": "https://www.crunchbase.com/person/sample",
                    "firm": "https://sampleventures.com"
                },
                "image": ""
            }
        }
        
        return mock_profiles.get(name, mock_profiles["default"])
    
    # Real implementation
    llm = ChatGoogleGenerativeAI(
        temperature=0, 
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    template = """Given the investor name {investor_name}, find their profiles across different platforms.
    Look for:
    1. Their Twitter/X profile
    2. LinkedIn profile
    3. Crunchbase profile
    4. Medium profile (if they write)
    5. Their venture firm website
    
    Return the information in this exact format:
    - name: Full name
    - firm: Their venture capital firm
    - title: Their position
    - bio: Brief bio
    - urls: Dictionary with keys: twitter, linkedin, crunchbase, medium, firm
    - image: Profile image URL if found
    """
    
    prompt_template = PromptTemplate(
        template=template, 
        input_variables=["investor_name"]
    )
    
    tools_for_agent = [
        Tool(
            name="Search investor profiles",
            func=search_investor_profiles,
            description="Search for investor profiles across platforms"
        )
    ]
    
    react_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True)
    
    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(investor_name=name)}
    )
    
    # Parse the output and structure it properly
    output_text = result["output"]
    
    # Create structured data from the agent's response
    profile_data = {
        "name": name,
        "firm": "",
        "title": "",
        "bio": f"Investor and entrepreneur",
        "urls": {
            "twitter": "",
            "linkedin": "",
            "crunchbase": "",
            "medium": "",
            "firm": ""
        },
        "image": ""
    }
    
    # Use the smart profile finder to get URLs from internet search
    print(f"🔍 Searching internet for profile URLs for {name}...")
    try:
        real_urls = smart_find_all_profiles(name)
        
        # Update profile data with real URLs
        for platform, url in real_urls.items():
            profile_data["urls"][platform] = url
        
        print(f"✅ Found {len(real_urls)} profile URLs via internet search")
        
    except Exception as e:
        print(f"Error finding profile URLs: {e}")
        
        # Fallback: Try to extract from agent response
        import re
        twitter_match = re.search(r'twitter\.com/[\w-]+', output_text.lower())
        if twitter_match:
            profile_data["urls"]["twitter"] = f"https://{twitter_match.group()}"
        
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', output_text.lower())
        if linkedin_match:
            profile_data["urls"]["linkedin"] = f"https://{linkedin_match.group()}"
        
        crunchbase_match = re.search(r'crunchbase\.com/person/[\w-]+', output_text.lower())
        if crunchbase_match:
            profile_data["urls"]["crunchbase"] = f"https://{crunchbase_match.group()}"
        
        medium_match = re.search(r'medium\.com/@[\w-]+', output_text.lower())
        if medium_match:
            profile_data["urls"]["medium"] = f"https://{medium_match.group()}"
    
    # Use improved image search for all investors
    try:
        from third_parties.image_search import search_investor_image
        profile_data["image"] = search_investor_image(name, profile_data.get("firm", ""))
    except Exception as e:
        print(f"Image search error: {e}")
        profile_data["image"] = f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=300&background=4A90E2&color=fff&bold=true"
    
    # Try to extract firm information
    if "andreessen horowitz" in output_text.lower() or "a16z" in output_text.lower():
        profile_data["firm"] = "Andreessen Horowitz (a16z)"
        profile_data["urls"]["firm"] = "https://a16z.com"
    elif "mark cuban" in output_text.lower() or "cuban companies" in output_text.lower():
        profile_data["firm"] = "Mark Cuban Companies"  
        profile_data["urls"]["firm"] = "https://markcubancompanies.com"
    elif "founders fund" in output_text.lower() or "peter thiel" in output_text.lower():
        profile_data["firm"] = "Founders Fund"
        profile_data["urls"]["firm"] = "https://foundersfund.com"
    
    # Extract title if mentioned
    if "co-founder" in output_text.lower():
        profile_data["title"] = "Co-founder and General Partner"
    elif "founder" in output_text.lower():
        profile_data["title"] = "Founder"  
    elif "partner" in output_text.lower():
        profile_data["title"] = "Partner"
    elif "owner" in output_text.lower():
        profile_data["title"] = "Owner and Investor"
    else:
        profile_data["title"] = "Investor"
    
    # Use a default professional image if none found
    if not profile_data["image"]:
        profile_data["image"] = "https://via.placeholder.com/300x300/4A90E2/ffffff?text=" + name.replace(" ", "+")
    
    return profile_data