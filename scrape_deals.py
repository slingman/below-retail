from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")

    nike_results = scrape_nike_air_max_1()

    if not nike_results:
        print("No products found.")
        return

    total = len(nike_results)
    sale_count = sum(1 for p in nike_results if p["is_sale"])

    for product in nike_results:
        print(f"{product['title']} ({product['style_id']})")
        print(f"URL: {product['url']}")
        if product['is_sale']:
            discount = round(
                100 * (product["full_price"] - product["current_price"]) / product["full_price"]
            )
            print(f"SALE: ${product['current_price']} (was ${product['full_price']}, {discount}% off)")
        else:
            print(f"Price: ${product['current_price']}")
        print("-" * 60)

    print("\nSummary:")
    print(f"  Total products: {total}")
    print(f"  On sale: {sale_count}")

if __name__ == "__main__":
    main()
