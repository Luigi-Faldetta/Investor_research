from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os

from investor_research import research_investor

load_dotenv()

app = Flask(__name__, static_folder='static')

# Serve static images (if needed for other images)
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('static/images', filename)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mock", methods=["GET"])
def mock_data():
    """Return mock data for testing the UI"""
    mock_response = {
        "success": True,
        "profile": {
            "name": "Marc Andreessen",
            "title": "Co-founder & General Partner",
            "firm": "Andreessen Horowitz",
            "bio": "Marc Andreessen is a prominent venture capitalist and co-founder of Andreessen Horowitz. He previously co-created the highly influential Mosaic Internet browser and co-founded Netscape. Known for his 'software is eating the world' thesis, he has invested in and advised many successful technology companies including Facebook, Twitter, GitHub, Pinterest, and Airbnb.",
            "profile_image": "https://res.cloudinary.com/doqmqgbym/image/upload/v1756815192/investors/investors/marc_andreessen.jpg",
            "profile_urls": {
                "twitter": "https://twitter.com/pmarca",
                "linkedin": "https://www.linkedin.com/in/pmarca",
                "crunchbase": "https://www.crunchbase.com/person/marc-andreessen",
                "medium": "https://medium.com/@pmarca",
                "firm": "https://a16z.com"
            }
        },
        "portfolio": [
            {
                "name": "Facebook",
                "sector": "Social Media",
                "stage": "Series B",
                "investment_date": "2007",
                "description": "Leading social networking platform connecting billions of users worldwide",
                "website": "https://www.facebook.com",
                "stock_symbol": "META",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/META"
            },
            {
                "name": "GitHub",
                "sector": "Developer Tools",
                "stage": "Series A",
                "investment_date": "2012",
                "description": "World's largest platform for software development and version control",
                "website": "https://github.com",
                "stock_symbol": "MSFT",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/MSFT"
            },
            {
                "name": "Airbnb",
                "sector": "Travel & Hospitality",
                "stage": "Series B",
                "investment_date": "2011",
                "description": "Online marketplace for lodging and tourism experiences",
                "website": "https://www.airbnb.com",
                "stock_symbol": "ABNB",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/ABNB"
            },
            {
                "name": "Coinbase",
                "sector": "Cryptocurrency",
                "stage": "Series C",
                "investment_date": "2013",
                "description": "Digital currency exchange platform",
                "website": "https://www.coinbase.com",
                "stock_symbol": "COIN",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/COIN"
            },
            {
                "name": "Slack",
                "sector": "Enterprise Software",
                "stage": "Series A",
                "investment_date": "2014",
                "description": "Business communication platform",
                "website": "https://slack.com",
                "stock_symbol": "CRM",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/CRM"
            },
            {
                "name": "Instacart",
                "sector": "E-commerce",
                "stage": "Series A",
                "investment_date": "2013",
                "description": "Online grocery delivery and pickup service",
                "website": "https://www.instacart.com",
                "stock_symbol": "CART",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/CART"
            },
            {
                "name": "Pinterest",
                "sector": "Social Media",
                "stage": "Series C",
                "investment_date": "2012",
                "description": "Visual discovery and idea platform",
                "website": "https://www.pinterest.com",
                "stock_symbol": "PINS",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/PINS"
            },
            {
                "name": "Okta",
                "sector": "Enterprise Software",
                "stage": "Series B",
                "investment_date": "2011",
                "description": "Identity and access management platform",
                "website": "https://www.okta.com",
                "stock_symbol": "OKTA",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/OKTA"
            },
            {
                "name": "Roblox",
                "sector": "Gaming",
                "stage": "Series D",
                "investment_date": "2018",
                "description": "Online gaming platform and game creation system",
                "website": "https://www.roblox.com",
                "stock_symbol": "RBLX",
                "yahoo_finance_url": "https://finance.yahoo.com/quote/RBLX"
            },
            {
                "name": "Clubhouse",
                "sector": "Social Media",
                "stage": "Series B",
                "investment_date": "2021",
                "description": "Audio-based social networking app",
                "website": "https://www.clubhouse.com",
                "stock_symbol": None,
                "yahoo_finance_url": None
            }
        ],
        "insights": {
            "investment_themes": [
                "Software is Eating the World",
                "Consumer Internet Platforms",
                "Enterprise SaaS",
                "Crypto & Web3",
                "AI & Machine Learning"
            ],
            "investment_thesis": "Marc Andreessen focuses on transformative technology companies that have the potential to disrupt traditional industries. His investment philosophy centers on the belief that software companies can achieve massive scale with minimal marginal costs, leading to unprecedented market opportunities.",
            "sector_focus": [
                "Enterprise Software (30%)",
                "Social Media & Consumer (25%)",
                "Cryptocurrency & Blockchain (20%)",
                "Developer Tools & Infrastructure (15%)",
                "E-commerce & Marketplaces (10%)"
            ],
            "notable_quotes": [
                "Software is eating the world, and we're only at the beginning of this transformation.",
                "The spread of computers and the Internet will put jobs in two categories: people who tell computers what to do, and people who are told by computers what to do.",
                "In the startup world, you're either a genius or an idiot. You're never just an ordinary guy trying to get through the day.",
                "The biggest risk is not taking any risk. In a world that's changing really quickly, the only strategy that is guaranteed to fail is not taking risks."
            ],
            "icebreakers": []
        },
        "medium_articles": [
            {
                "title": "Why Software Is Eating the World",
                "excerpt": "More and more major businesses and industries are being run on software and delivered as online services...",
                "date": "Aug 20, 2011",
                "read_time": "12 min read",
                "url": "https://a16z.com/2011/08/20/why-software-is-eating-the-world/",
                "claps": 15000
            },
            {
                "title": "The Future of AI and Its Impact on Society",
                "excerpt": "Artificial intelligence is poised to transform every industry and aspect of human life...",
                "date": "Mar 15, 2024",
                "read_time": "8 min read",
                "url": "#",
                "claps": 8500
            },
            {
                "title": "Building the Next Generation of Tech Companies",
                "excerpt": "Lessons learned from investing in hundreds of startups over the past decade...",
                "date": "Jan 10, 2024",
                "read_time": "15 min read",
                "url": "#",
                "claps": 12000
            }
        ],
        "news": [
            {
                "title": "Andreessen Horowitz Raises $7.2B for New Funds",
                "excerpt": "The venture capital firm announces its largest fundraise to date, with plans to invest in AI, biotech, and crypto startups...",
                "source": "TechCrunch",
                "date": "Today",
                "url": "https://techcrunch.com"
            },
            {
                "title": "Marc Andreessen on the AI Revolution",
                "excerpt": "In an exclusive interview, the prominent investor shares his thoughts on artificial intelligence and its potential impact...",
                "source": "Forbes",
                "date": "Yesterday",
                "url": "https://forbes.com"
            },
            {
                "title": "a16z Portfolio Company Goes Public at $10B Valuation",
                "excerpt": "Another successful exit for Andreessen Horowitz as their portfolio company debuts on NASDAQ...",
                "source": "Wall Street Journal",
                "date": "2 days ago",
                "url": "https://wsj.com"
            },
            {
                "title": "Breaking: Marc Andreessen Joins Board of AI Unicorn",
                "excerpt": "The respected investor brings decades of experience to fast-growing artificial intelligence company...",
                "source": "Bloomberg",
                "date": "3 days ago",
                "url": "https://bloomberg.com"
            },
            {
                "title": "Andreessen Predicts Major Shifts in Tech Landscape",
                "excerpt": "Speaking at a recent conference, Marc Andreessen outlined key trends that will shape venture capital...",
                "source": "VentureBeat",
                "date": "5 days ago",
                "url": "https://venturebeat.com"
            }
        ]
    }
    
    return jsonify(mock_response)


@app.route("/research", methods=["POST"])
def research():
    investor_name = request.form["investor_name"]
    
    try:
        profile, portfolio, insights, news = research_investor(name=investor_name)
        
        # Also fetch Medium articles separately to include in response
        from third_parties.medium import fetch_medium_articles
        medium_url = profile.profile_urls.get("medium", "")
        # Pass investor name to get articles ABOUT them
        medium_articles = fetch_medium_articles(medium_url, mock=False, investor_name=investor_name) if medium_url else []
        
        return jsonify({
            "success": True,
            "profile": profile.to_dict(),
            "portfolio": [company.to_dict() for company in portfolio],
            "insights": insights.to_dict(),
            "medium_articles": medium_articles,
            "news": news
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)