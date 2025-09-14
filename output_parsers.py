from typing import List, Dict, Any
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class InvestorProfile(BaseModel):
    name: str = Field(description="Full name of the investor")
    firm: str = Field(description="Venture capital firm or company")
    title: str = Field(description="Current position/title")
    bio: str = Field(description="Professional biography")
    profile_urls: Dict[str, str] = Field(description="URLs for different platforms")
    profile_image: str = Field(description="Profile image URL")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "firm": self.firm,
            "title": self.title,
            "bio": self.bio,
            "profile_urls": self.profile_urls,
            "profile_image": self.profile_image
        }


class PortfolioCompany(BaseModel):
    name: str = Field(description="Company name")
    sector: str = Field(description="Industry sector")
    stage: str = Field(description="Investment stage (Seed, Series A, etc.)")
    investment_date: str = Field(description="Date of investment")
    description: str = Field(description="Brief company description")
    investment_value: float = Field(description="Investment amount in USD", default=0)
    website: str = Field(description="Company website URL", default="")
    stock_symbol: str = Field(description="Stock ticker symbol if public", default="")
    yahoo_finance_url: str = Field(description="Yahoo Finance page URL if public", default="")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "sector": self.sector,
            "stage": self.stage,
            "investment_date": self.investment_date,
            "description": self.description,
            "investment_value": self.investment_value,
            "website": self.website,
            "stock_symbol": self.stock_symbol,
            "yahoo_finance_url": self.yahoo_finance_url
        }


class InvestmentInsights(BaseModel):
    investment_themes: List[str] = Field(description="3-5 key investment themes")
    sector_focus: List[str] = Field(description="Top sectors of interest")
    stage_preference: str = Field(description="Preferred investment stage")
    recent_deals: List[Dict[str, str]] = Field(description="Last 3-5 notable investments")
    investment_thesis: str = Field(description="Summary of investment philosophy")
    notable_quotes: List[str] = Field(description="Direct quotes spoken or written BY the investor (not about them)")
    icebreakers: List[str] = Field(description="5 conversation starters")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "investment_themes": self.investment_themes,
            "sector_focus": self.sector_focus,
            "stage_preference": self.stage_preference,
            "recent_deals": self.recent_deals,
            "investment_thesis": self.investment_thesis,
            "notable_quotes": self.notable_quotes,
            "icebreakers": self.icebreakers
        }


# Create parsers for structured output
insights_parser = PydanticOutputParser(pydantic_object=InvestmentInsights)