# CDKeys Game Scraper 🎮

A fast, multi-threaded Python web scraper that monitors game deals on CDKeys.com, saving results to JSON format.

## 🌟 Features
- Multi-threaded scraping for optimal performance
- Customizable scraping parameters
- Clean JSON output format
- Colorful CLI interface
- Rate limiting and retry mechanisms
- Error handling and logging

## 📋 Requirements
- Python 3.8+
- Required packages listed in `requirements.txt`

## 🚀 Quick Start

1. Clone the repository
   git clone https://github.com/Plutoissexy/CDKeyScraper.git
   cd cdkeys-scraper

## 2. Install dependencies

pip install -r requirements.txt


## 3. Run the scraper

python main.py

## ⚙️ Configuration Options

Parameter Default Description
Base URL https://www.cdkeys.com/pc/games Main scraping target
Max Pages 600 Maximum pages to scrape
Threads 12 Number of concurrent threads
Output game_deals.json Output file name

## 📄 Output Format

{
  "Title": "Game Name",
  "Price": 29.99,
  "Discount": "50%",
  "Link": "https://...",
  "last_updated": "2024-01-..."
}

## 🛠️ Development

Written in Python 3.12+
Uses BeautifulSoup4 for parsing
Implements threading for performance
Includes rate limiting for reliability

⚠️ Disclaimer

This tool is for educational purposes only. Please respect CDKeys.com's terms of service and robots.txt.

👨‍💻 Author

Created by Pluto