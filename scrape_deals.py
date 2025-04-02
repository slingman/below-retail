from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")

    deals = scrape_nike_air_max_1()
    if not deals:
        print("No deals found.")
        return

    print("\nNike Air Max 1 Deals:\n")
    for deal in deals:
        print(f"- {deal['title']} ({deal['style_color']})")
        print(f"  Price: ${deal['price']} (was ${deal['full_price']})" if deal['discount'] else f"  Price: ${deal['price']}")
        if deal['discount']:
            print(f"  🔥 {deal['discount']}% OFF!")
        print(f"  URL: {deal['url']}\n")

    print("Summary:")
    print(f"  Total products found: {len(deals)}")
    print(f"  On sale: {sum(1 for d in deals if d['discount'])}")

if __name__ == "__main__":
    main()
