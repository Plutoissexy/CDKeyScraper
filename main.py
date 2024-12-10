from colorama import init, Fore, Back, Style
from scraper import CDKeysScraper
import logging

init(autoreset=True)

# Set up logging with colors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logging.addLevelName(logging.INFO, f"{Fore.CYAN}INFO{Style.RESET_ALL}")
logging.addLevelName(logging.WARNING, f"{Fore.YELLOW}WARNING{Style.RESET_ALL}")
logging.addLevelName(logging.ERROR, f"{Fore.RED}ERROR{Style.RESET_ALL}")

def main():
    print(f"{Back.BLACK}{Fore.CYAN}=== CDKeys Game Scraper ==={Style.RESET_ALL}")
    print(f"{Fore.GREEN}Created by Pluto ({Fore.BLUE}https://github.com/Plutoissexy{Fore.GREEN}){Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Enter the base URL {Fore.WHITE}(default: https://www.cdkeys.com/pc/games): ", end="")
    base_url = input().strip()
    if not base_url:
        base_url = "https://www.cdkeys.com/pc/games"
    
    print(f"{Fore.YELLOW}Enter maximum pages to scrape {Fore.WHITE}(default: 50): ", end="")
    max_pages = input().strip()
    max_pages = int(max_pages) if max_pages.isdigit() else 50
    
    print(f"{Fore.YELLOW}Enter number of threads {Fore.WHITE}(default: 12): ", end="")
    num_threads = input().strip()
    num_threads = int(num_threads) if num_threads.isdigit() else 12
    
    print(f"{Fore.YELLOW}Enter output JSON filename {Fore.WHITE}(default: game_deals.json): ", end="")
    output_file = input().strip()
    if not output_file:
        output_file = "game_deals.json"
    if not output_file.endswith('.json'):
        output_file += '.json'

    print(f"\n{Fore.CYAN}Starting scraper with following configuration:")
    print(f"{Fore.WHITE}Base URL: {Fore.GREEN}{base_url}")
    print(f"{Fore.WHITE}Max Pages: {Fore.GREEN}{max_pages}")
    print(f"{Fore.WHITE}Threads: {Fore.GREEN}{num_threads}")
    print(f"{Fore.WHITE}Output File: {Fore.GREEN}{output_file}\n")

    scraper = CDKeysScraper(base_url, max_pages=max_pages, num_threads=num_threads)
    print(f"{Fore.CYAN}Starting scraping process...{Style.RESET_ALL}")
    
    try:
        deals = scraper.scrape_all_pages()
        if deals:
            scraper.save_deals_to_json(deals, output_file)
            print(f"{Fore.GREEN}Successfully saved {len(deals)} deals to {output_file}")
        else:
            print(f"{Fore.RED}No deals found")
    except Exception as e:
        print(f"{Fore.RED}Error during scraping process: {str(e)}")
    
    print(f"\n{Back.GREEN}{Fore.BLACK} Scraping completed! {Style.RESET_ALL}")

if __name__ == "__main__":
    main()
