# scrape_deals.py

from nike import scrape_nike_air_max_1

def main():
    print("=== Below Retail Deals: Nike Air Max 1 ===\n")

    nike_products = scrape_nike_air_max_1()

    total_products = len(nike_products)
    total_variants = sum(len(p['variants']) for p in nike_products)
    total_discounted = sum(
        1 for p in nike_products for v in p['variants'] if v.get('discount_percent', 0) > 0
    )

    print("\n=== Summary ===")
    print(f"Total unique Nike products: {total_products}")
    print(f"Total colorway variants found: {total_variants}")
    print(f"Variants currently on sale: {total_discounted}")

if __name__ == "__main__":
    main()
