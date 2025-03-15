from scrapers.sneakers.nike import scrape_nike
from scrapers.sneakers.adidas import scrape_adidas
from scrapers.sneakers.footlocker import scrape_footlocker
from scrapers.sneakers.goat import scrape_goat
from scrapers.sneakers.stockx import scrape_stockx
from scrapers.tech.bestbuy import scrape_bestbuy
from scrapers.tech.amazon import scrape_amazon
from scrapers.tech.walmart import scrape_walmart
from utils.file_manager import save_deals_to_json

def main():
    """Main function that runs all scrapers and saves the results."""
    price_comparison = {}

    # ✅ Sneakers Scrapers
    price_comparison.update(scrape_nike())
    price_comparison.update(scrape_adidas())
    price_comparison.update(scrape_footlocker())
    price_comparison.update(scrape_goat())
    price_comparison.update(scrape_stockx())

    # ✅ Tech Scrapers
    price_comparison.update(scrape_bestbuy())
    price_comparison.update(scrape_amazon())
    price_comparison.update(scrape_walmart())

    # ✅ Save results
    save_deals_to_json(price_comparison)

if __name__ == "__main__":
    main()

