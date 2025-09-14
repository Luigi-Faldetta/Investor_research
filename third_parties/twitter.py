import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def get_mock_tweets(investor_name: str) -> List[Dict]:
    """
    Return mock tweet data when API is not available or for testing
    """
    if "Mark Cuban" in investor_name:
        return [
            {
                "text": "The biggest mistake entrepreneurs make is thinking they need to have all the answers. Smart questions are more valuable than quick answers.",
                "date": "2024-01-15",
                "likes": 15234,
                "retweets": 3421
            },
            {
                "text": "Every 'no' gets you closer to a 'yes.' Every mistake gets you closer to success. Every rejection gets you closer to acceptance.",
                "date": "2024-01-10",
                "likes": 24567,
                "retweets": 5234
            },
            {
                "text": "Starting a business is like jumping out of an airplane and assembling a parachute on the way down. Cost Plus Drugs is proof that when you land safely, you can help millions of people.",
                "date": "2024-01-05",
                "likes": 18943,
                "retweets": 4123
            },
            {
                "text": "The best businesses are created to solve problems that affect you personally. That's why I created Cost Plus Drugs - healthcare costs were crushing American families.",
                "date": "2023-12-28",
                "likes": 31245,
                "retweets": 7865
            },
            {
                "text": "AI will transform every industry, but human creativity and empathy will become MORE valuable, not less. Invest in both technology and humanity.",
                "date": "2023-12-20",
                "likes": 22134,
                "retweets": 5432
            }
        ]
    elif "Peter Thiel" in investor_name:
        return [
            {
                "text": "Competition is for losers. Monopoly is for winners. Build something so good that no one else can compete.",
                "date": "2024-01-18",
                "likes": 12453,
                "retweets": 2876
            },
            {
                "text": "The most contrarian thing of all is not to oppose the crowd but to think for yourself.",
                "date": "2024-01-12",
                "likes": 18976,
                "retweets": 4321
            },
            {
                "text": "Every moment in business happens only once. The next Bill Gates will not build an operating system. The next Larry Page won't make a search engine.",
                "date": "2024-01-08",
                "likes": 25134,
                "retweets": 6789
            },
            {
                "text": "What important truth do very few people agree with you on? This is still the most important question for any entrepreneur or investor.",
                "date": "2023-12-30",
                "likes": 16843,
                "retweets": 3952
            },
            {
                "text": "We wanted flying cars, instead we got 140 characters. But perhaps that's changing - SpaceX and breakthrough technologies are making the future we imagined possible.",
                "date": "2023-12-22",
                "likes": 28765,
                "retweets": 8234
            }
        ]
    elif "Paul Tudor Jones" in investor_name:
        return [
            {
                "text": "The secret to being a good trader is to have humility. The markets will humble you if you don't humble yourself first.",
                "date": "2024-01-20",
                "likes": 8765,
                "retweets": 1987
            },
            {
                "text": "Intellectual capital will always trump financial capital in the long run. Invest in learning, invest in people.",
                "date": "2024-01-14",
                "likes": 12456,
                "retweets": 2834
            },
            {
                "text": "The greatest trade I ever made wasn't about money - it was founding Robin Hood Foundation and seeing poverty decline in NYC.",
                "date": "2024-01-09",
                "likes": 15623,
                "retweets": 4123
            },
            {
                "text": "Climate change is the ultimate macro trade. We must deploy capital toward solutions that benefit both planet and profit.",
                "date": "2023-12-31",
                "likes": 19234,
                "retweets": 5432
            },
            {
                "text": "In trading and in life: Plan your trades, trade your plan. But be humble enough to change when the facts change.",
                "date": "2023-12-25",
                "likes": 11876,
                "retweets": 2765
            }
        ]
    elif "Cathie Wood" in investor_name:
        return [
            {
                "text": "We are in the early stages of the most powerful convergence in history: AI, energy storage, robotics, blockchain, and genomics will transform everything.",
                "date": "2024-01-22",
                "likes": 23456,
                "retweets": 6789
            },
            {
                "text": "Tesla isn't just a car company - it's an AI, robotics, and energy storage company that happens to make the world's best electric vehicles.",
                "date": "2024-01-16",
                "likes": 34567,
                "retweets": 9876
            },
            {
                "text": "Innovation is deflationary. While traditional investors fear deflation, we see it as the natural result of exponential technological progress.",
                "date": "2024-01-11",
                "likes": 18765,
                "retweets": 4321
            },
            {
                "text": "The genomics revolution will be bigger than the internet. We're moving from one-size-fits-all medicine to personalized precision treatments.",
                "date": "2024-01-06",
                "likes": 15432,
                "retweets": 3876
            },
            {
                "text": "Disruptive innovation creates new markets and destroys old ones. Traditional valuation methods can't capture the exponential nature of breakthrough technologies.",
                "date": "2023-12-29",
                "likes": 21098,
                "retweets": 5234
            }
        ]
    elif "Marc Andreessen" in investor_name:
        return [
            {
                "text": "Software is eating the world. Every industry that can be transformed by software will be.",
                "date": "2024-01-20",
                "likes": 8523,
                "retweets": 2134
            },
            {
                "text": "The spread of computers and the Internet will put jobs in two categories: people who tell computers what to do, and people who are told by computers what to do.",
                "date": "2024-01-19",
                "likes": 6421,
                "retweets": 1567
            },
            {
                "text": "In the next 10 years, I expect many more industries to be disrupted by software, with new world-beating Silicon Valley companies doing the disruption in more cases than not.",
                "date": "2024-01-18",
                "likes": 4892,
                "retweets": 923
            },
            {
                "text": "The smartphone revolution is under-hyped, more wild stuff happening than most realize. AI agents will be the next platform shift.",
                "date": "2024-01-17",
                "likes": 5134,
                "retweets": 1245
            },
            {
                "text": "Entrepreneurship is essentially an act of faith. You have to believe something that most people don't believe.",
                "date": "2024-01-16",
                "likes": 3678,
                "retweets": 789
            },
            {
                "text": "The best entrepreneurs are missionaries, not mercenaries. They're driven by a desire to change the world.",
                "date": "2024-01-15",
                "likes": 4123,
                "retweets": 892
            },
            {
                "text": "We are in the middle of a dramatic and broad technological and economic shift in which software companies are poised to take over large swathes of the economy.",
                "date": "2024-01-14",
                "likes": 2987,
                "retweets": 654
            },
            {
                "text": "The venture capital business is 100% about outliers. You're looking for the one company out of the portfolio that becomes a Google or Facebook.",
                "date": "2024-01-13",
                "likes": 3456,
                "retweets": 723
            }
        ]
    
    # Default tweets for unknown investors
    return [
        {
            "text": "Investing in early-stage companies requires patience, conviction, and the ability to see potential where others see risk.",
            "date": "2024-01-20",
            "likes": 1245,
            "retweets": 234
        },
        {
            "text": "The best entrepreneurs solve problems they deeply understand. Personal pain points often lead to the biggest opportunities.",
            "date": "2024-01-18",
            "likes": 856,
            "retweets": 167
        },
        {
            "text": "Technology trends move faster than ever. The companies that win will be those that adapt quickest to change.",
            "date": "2024-01-15",
            "likes": 634,
            "retweets": 89
        }
    ]


def fetch_recent_tweets(twitter_url: str, mock: bool = False, investor_name: str = "") -> List[Dict]:
    """
    Fetch recent tweets from a Twitter profile.
    """
    if mock:
        return get_mock_tweets(investor_name)
    
    # Real implementation - for now return empty list if no API key
    # To implement: use Twitter API v2 or scraping
    print(f"Twitter API not configured, returning empty tweets for {twitter_url}")
    return []