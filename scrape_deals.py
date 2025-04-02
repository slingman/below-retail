from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    print("Finding Nike Air Max 1 deals...\n")

    nike_deals = scrape_nike_air_max_1()

    if not nike_deals:
        print("No deals found.")
        return

    print("\nNike Air Max 1 Deals:\n")
    for deal in nike_deals:
        title = deal['title']
        url = deal['url']
        style_id = deal['style_id']
        full_price = deal['full_price']
        current_price = deal['current_price']
        discount = deal['discount_percent']

        price_line = f"${current_price:.2f}"
        if discount:
            price_line += f" (was ${full_price:.2f}, {discount}% off)"

        print(f"- {title} ({style_id}) — {price_line}")
        print(f"  {url}\n")

    print("Summary:")
    print(f"  Total products: {len(nike_deals)}")
    on_sale = sum(1 for d in nike_deals if d["discount_percent"])
    print(f"  On sale: {on_sale}")

if __name__ == "__main__":
    main()
