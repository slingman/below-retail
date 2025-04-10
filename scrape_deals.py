from scrapers.sneakers.nike import scrape_nike_air_max_1

def main():
    deals = scrape_nike_air_max_1()

    print("\nFinal Nike Air Max 1 Deals:\n")
    for deal in deals:
        print(f"{deal['title']} ({deal['style_id']})")
        print(f"  Current Price: {deal['current_price']}")
        print(f"  Original Price: {deal['original_price']}")
        if "discount_percent" in deal:
            print(f"  Discount: {deal['discount_percent']}% off")
        print(f"  URL: {deal['url']}\n")

    print("Summary:")
    print(f"  Total unique products: {len(deals)}")
    on_sale = [d for d in deals if "discount_percent" in d]
    print(f"  Variants on sale: {len(on_sale)}")

if __name__ == "__main__":
    main()
