# scrape_deals.py

from scrapers.sneakers.nike import scrape_nike_air_max_1

if __name__ == "__main__":
    deals = scrape_nike_air_max_1()

    print("\nFinal Nike Air Max 1 Deals:")
    for deal in deals:
        print(f"{deal['style_id']} - {deal['title']}")
        if deal['price'] != deal['sale_price']:
            discount = round((deal['price'] - deal['sale_price']) / deal['price'] * 100)
            print(f"  SALE: ${deal['sale_price']} (was ${deal['price']}, {discount}% off)")
        else:
            print(f"  Price: ${deal['price']}")

    total_products = len(deals)
    total_variants = sum(len(product.get("variants", [])) for product in deals)
    total_sale = sum(
        1 for product in deals
        for variant in product.get("variants", [])
        if variant["price"] != variant["sale_price"]
    )

    print(f"\nSummary:")
    print(f"  Total unique products: {total_products}")
    print(f"  Total colorway variants: {total_variants}")
    print(f"  Variants on sale: {total_sale}")
