from scrapers.sneakers.nike import scrape_nike_air_max_1

print("Finding Nike Air Max 1 deals...\n")

nike_products = scrape_nike_air_max_1()

if not nike_products:
    print("No deals found.")
else:
    print(f"\nFound {len(nike_products)} products:\n")

    for product in nike_products:
        print(f"- {product['title']} ({product['style_id']})")
        print(f"  Price: ${product['sale_price']:.2f}", end="")
        if product["discount"]:
            print(f" (was ${product['full_price']:.2f}, {product['discount']}% off)")
        else:
            print()
        print(f"  Link: {product['url']}\n")
