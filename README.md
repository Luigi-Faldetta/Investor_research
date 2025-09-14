# Investor Research Assistant

An AI-powered tool for researching venture capitalists and startup investors, providing comprehensive insights on their portfolio, investment themes, and recent activity.

## Features

- **Multi-Platform Profile Discovery**: Automatically finds investor profiles across Twitter, LinkedIn, Crunchbase, and Medium
- **Portfolio Analysis**: Discovers and analyzes portfolio companies with sector and stage information
- **Content Aggregation**: Fetches recent tweets, LinkedIn posts, and Medium articles
- **AI-Generated Insights**: 
  - Investment themes and patterns
  - Sector focus areas
  - Investment thesis summary
  - Notable quotes from their content
  - Personalized conversation icebreakers

## Setup

1. **Install dependencies**:
   ```bash
   pip install pipenv
   pipenv install
   ```

2. **Configure API keys**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

   **Required API keys:**
   - `OPENAI_API_KEY`: For AI analysis (GPT-4)
   - `TAVILY_API_KEY`: For web search and portfolio discovery

   **Optional API keys (for enhanced features):**
   - Twitter API credentials (for real tweets)
   - Scrapin.io API key (for LinkedIn posts)
   - ~~Crunchbase API key~~ (NOT needed - we use free alternatives!)

   **Note:** The app works great with just OpenAI and Tavily!

3. **Run the application**:
   ```bash
   pipenv run python app.py
   ```

4. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5001`

## Usage

1. Enter an investor's name in the search box (e.g., "Marc Andreessen")
2. Click "Research Investor"
3. The system will:
   - Search for the investor's profiles across platforms
   - Fetch their portfolio companies
   - Aggregate recent social media content
   - Generate AI-powered insights
4. Review the comprehensive report with:
   - Investor profile and links
   - Portfolio companies grid
   - Investment themes and thesis
   - Conversation starters

## Project Structure

```
investor_research/
├── app.py                     # Flask web server
├── investor_research.py       # Main orchestration logic
├── output_parsers.py         # Data models
├── agents/                   # LangChain agents
│   ├── investor_lookup_agent.py
│   ├── portfolio_agent.py
│   └── content_agent.py
├── tools/                    # Search and data tools
├── third_parties/           # External API integrations
└── templates/               # HTML interface
```

## Mock Mode

The application currently runs in mock mode with sample data for testing. To use real data:
1. Add your API keys to `.env`
2. Update the `mock=False` flags in the code
3. Implement the actual API calls in the third_parties modules

## Future Enhancements

- Real-time data fetching from all platforms
- Export reports to PDF/Markdown
- Historical investment tracking
- Co-investor network analysis
- Investment success metrics
- Email alerts for new investments