# scrape_deals.py

from scrapers.sneakers.nike import get_nike_deals

def main():
    print("📦 Fetching Nike deals...")
    nike_deals = get_nike_deals()

    print("\n✅ Nike scraping complete.")
    print(f"\nSUMMARY RESULTS:")
    print(f"Total unique Nike products: {len(nike_deals)}")

    for idx, deal in enumerate(nike_deals, start=1):
        print(f"{idx}. {deal.get('product_title')} ({deal.get('style_id')})")
        if deal.get('sale_price') and deal.get('price'):
            discount = 100 * (1 - deal['sale_price'] / deal['price'])
            print(f"   🔥 ${deal['sale_price']} → ${deal['price']} ({round(discount)}% off)")
        elif deal.get('price'):
            print(f"   💵 ${deal['price']}")

if __name__ == "__main__":
    main()
