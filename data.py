import requests
from bs4 import BeautifulSoup
import json
import time
import os

CATEGORY_URLS = [
    "https://www.mega.pk/mobiles/4/",
    "https://www.mega.pk/bluetoothhandfree/",
    "https://www.mega.pk/watches/",
    "https://www.mega.pk/trimmer/",
    "https://www.mega.pk/powerbank/",
    "https://www.mega.pk/mobilecables/",
    "https://www.mega.pk/mobilespeakers/",
    "https://www.mega.pk/multimediatablets/",
    "https://www.mega.pk/laptop-price-pakistan/"
]

# Category mapping to match the filename format in your image
CATEGORY_FILENAME_MAP = {
    "mobiles": "mobiles.json",
    "bluetoothhandfree": "bluetooth-speakers.json",
    "watches": "smart-watches.json",
    "trimmer": "trimmers-shaver.json",
    "powerbank": "power-banks.json",
    "mobilecables": "mobile-chargers.json",
    "mobilespeakers": "wireless-earbuds.json",
    "multimediatablets": "tablets.json",
    "laptop-price-pakistan": "laptops.json"
}

def get_category_from_url(url):
    parts = url.strip("/").split("/")
    for part in reversed(parts):
        if not part.isdigit() and part != "":
            return part
    return "unknown"

def save_category_data(category, products):
    """Save products for a specific category to its JSON file"""
    filename = CATEGORY_FILENAME_MAP.get(category, f"{category}.json")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=4, ensure_ascii=False)
        print(f"   ✓ Saved {len(products)} products to {filename}")
    except Exception as e:
        print(f"   ✗ Error saving {filename}: {e}")

def scrape_megaPK_all_categories(max_pages=2):
    # Dictionary to store products by category
    products_by_category = {}

    for base_url in CATEGORY_URLS:
        category = get_category_from_url(base_url)
        print(f"\n📱 Scraping category: {category}")
        
        # Initialize list for this category
        products_by_category[category] = []

        # Set max pages based on category
        if category == "mobiles":
            max_pages = 4
        elif category == "bluetoothhandfree":
            max_pages = 2
        elif category == "watches":
            max_pages = 2
        elif category == "mobilecables":
            max_pages = 2
        elif category == "multimediatablets":
            max_pages = 3
        elif category == "laptop-price-pakistan":
            max_pages = 8
        elif category == "powerbank":
            max_pages = 1
        elif category == "trimmer":
            max_pages = 1
        else:
            max_pages = 1    

        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}"
            print(f"   📄 Page {page}: {url}")
            
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"   ❌ Failed to load page {page} (Status: {response.status_code})")
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                product_cards = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-4 col-lg-3')

                if not product_cards:
                    print("   ⚠️  No more products found. Moving to next category.")
                    break

                page_products = 0
                for card in product_cards:
                    try:
                        img_tag = card.find('img')
                        image_url = img_tag.get('data-original') if img_tag and img_tag.has_attr('data-original') else (
                            img_tag.get('src') if img_tag else None
                        )

                        title_div = card.find('div', id='lap_name_div')
                        title_tag = title_div.find('a') if title_div else None
                        title = title_tag.text.strip() if title_tag else "N/A"
                        product_url = title_tag['href'] if title_tag and title_tag.has_attr('href') else None

                        price_tag = card.find('div', class_='cat_price')
                        price_text = price_tag.get_text(strip=True).replace("Rs", "").replace(",", "") if price_tag else "N/A"

                        product_data = {
                            "category": category,
                            "title": title,
                            "price": price_text,
                            "image_url": image_url,
                            "product_url": product_url
                        }
                        
                        products_by_category[category].append(product_data)
                        page_products += 1

                    except Exception as e:
                        print(f"   ⚠️  Error parsing product: {e}")

                print(f"   ✓ Scraped {page_products} products from page {page}")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"   ❌ Error scraping page {page}: {e}")
                break

        # Save data for this category immediately after scraping
        if products_by_category[category]:
            save_category_data(category, products_by_category[category])
        else:
            print(f"   ⚠️  No products found for category: {category}")

    # Print summary
    print(f"\n📊 SCRAPING SUMMARY:")
    print("=" * 50)
    total_products = 0
    for category, products in products_by_category.items():
        filename = CATEGORY_FILENAME_MAP.get(category, f"{category}.json")
        count = len(products)
        total_products += count
        print(f"📁 {filename}: {count} products")
    
    print("=" * 50)
    print(f"🎯 Total products scraped: {total_products}")
    print(f"📁 Files created: {len([cat for cat, products in products_by_category.items() if products])}")

    # Show sample data from first category with products
    for category, products in products_by_category.items():
        if products:
            print(f"\n📋 Sample data from {CATEGORY_FILENAME_MAP.get(category, f'{category}.json')}:")
            for product in products[:2]:  # Show only first 2 products
                print(json.dumps(product, indent=2, ensure_ascii=False))
            break

if __name__ == "__main__":
    print("🚀 Starting MegaPK scraper...")
    print("📁 Data will be saved in separate JSON files by category")
    scrape_megaPK_all_categories()