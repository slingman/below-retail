from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding product links...")
    nike_results = scrape_nike_air_max_1()

    print("\nFinal Nike Air Max 1 Deals:\n")
    for product in nike_results:
        print(f"{product['title']}")
        print(f"  URL: {product['url']}")
        print(f"  Base Style ID: {product['style_id']}")
        print(f"  Price: ${product['regular_price']}")
        if product['sale_price']:
            print(f"  Sale Price: ${product['sale_price']} (-{round((1 - float(product['sale_price']) / float(product['regular_price'])) * 100)}%)")
        print(f"  Variants:")

        for variant in product["variants"]:
            if variant["sale_price"]:
                pct = round((1 - float(variant["sale_price"]) / float(variant["regular_price"])) * 100)
                print(f"    - {variant['style_id']}: ${variant['sale_price']} (was ${variant['regular_price']}, {pct}% off)")
            else:
                print(f"    - {variant['style_id']}: ${variant['regular_price']}")
        print()

    total_products = len(nike_results)
    total_variants = sum(len(p["variants"]) for p in nike_results)
    total_sales = sum(
        1 for p in nike_results for v in p["variants"] if v["sale_price"]
    )

    print("Summary:")
    print(f"  Total unique products: {total_products}")
    print(f"  Total colorway variants: {total_variants}")
    print(f"  Variants on sale: {total_sales}")

if __name__ == "__main__":
    main()
