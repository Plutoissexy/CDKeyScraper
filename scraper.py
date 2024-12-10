import json
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import threading
from typing import Set, List, Dict, Optional, Any
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
from datetime import datetime
from config import CDKeysScraperConfig

class CDKeysScraper:
    def __init__(self, base_url: str, max_pages: int = 600, num_threads: int = 12):
        self.base_url = base_url
        self.max_pages = max_pages
        self.num_threads = num_threads
        self.lock = threading.Lock()
        self.seen_titles: Set[str] = set()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=CDKeysScraperConfig.MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def scrape_all_pages(self) -> List[Dict[str, Any]]:
        """Scrape all pages using thread pool"""
        all_deals = []
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            future_to_page = {
                executor.submit(self.scrape_page, page): page
                for page in range(1, self.max_pages + 1)
            }

            for future in future_to_page:
                try:
                    deals = future.result()
                    if deals:
                        with self.lock:
                            all_deals.extend(deals)
                except Exception as e:
                    logging.error(f"Error processing page {future_to_page[future]}: {str(e)}")
        return all_deals

    def scrape_page(self, page_number: int) -> List[Dict[str, Any]]:
        """Scrape a single page of products"""
        url = f"{self.base_url}?p={page_number}&platforms=Steam"
        response = self._make_request(url)
        if not response:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        deals = []

        for card in soup.find_all('div', class_='product-item-info'):
            try:
                deal = self._process_deal_card(card)
                if deal:
                    deals.append(deal)
            except Exception as e:
                logging.error(f"Error processing deal card on page {page_number}: {str(e)}")
        return deals

    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make a request with rate limiting and error handling"""
        try:
            time.sleep(random.uniform(0.5, 1.5))  # Random delay between requests
            response = self.session.get(
                url,
                headers=CDKeysScraperConfig.HEADERS,
                timeout=CDKeysScraperConfig.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Request failed for {url}: {str(e)}")
            return None

    def clean_price(self, price_string: str) -> Optional[float]:
        """Clean price string and convert to float"""
        try:
            price_string = ''.join(filter(
                lambda x: x.isdigit() or x == '.',
                price_string
            ))
            return float(price_string) if price_string else None
        except ValueError as e:
            logging.error(f"Error cleaning price {price_string}: {str(e)}")
            return None

    def clean_discount(self, discount_string: str) -> float:
        """Clean discount string and convert to float"""
        if not discount_string or discount_string == "No Discount":
            return 0.0
        try:
            return float(''.join(filter(str.isdigit, discount_string)))
        except ValueError as e:
            logging.error(f"Error cleaning discount {discount_string}: {str(e)}")
            return 0.0

    def _process_deal_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Process individual deal card"""
        title_elem = card.find('a', class_='product-item-link')
        if not title_elem:
            return None

        title = title_elem.text.strip()
        link = title_elem['href']

        with self.lock:
            if title.lower() in self.seen_titles:
                return None
            self.seen_titles.add(title.lower())

        price_elem = card.find('span', class_='price')
        price = self.clean_price(price_elem.text) if price_elem else None
        if not price:
            return None

        discount_elem = card.find('span', class_='product-item-discount')
        discount = discount_elem.text.strip() if discount_elem else "No Discount"

        return {
            'Title': title,
            'Price': price,
            'Discount': discount,
            'Link': link
        }

    def save_deals_to_json(self, deals: List[Dict[str, Any]], filename: str) -> None:
        if not deals:
            logging.warning("No deals to save")
            return

        try:
            sorted_deals = sorted(
                deals,
                key=lambda x: self.clean_discount(x['Discount']),
                reverse=True
            )

            timestamp = datetime.utcnow().isoformat()
            for deal in sorted_deals:
                deal['last_updated'] = timestamp

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(sorted_deals, f, indent=4, ensure_ascii=False)

            logging.info(f"Successfully saved {len(deals)} deals to {filename}")
        except Exception as e:
            logging.error(f"Error saving deals to JSON: {str(e)}")
