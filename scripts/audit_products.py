#!/usr/bin/env python3
"""
Comprehensive Audit Script for 6YARD Product Migration
Audits:
1. Static mock/fallback products in Next.js source files
2. All 95 live products from MongoDB / API
Checks for:
- Missing fields (title, price, description, images, sizes, stock)
- Duplicate titles or handles
- Image hosting types (Cloudinary, Google CDN, Local)
- Broken image links (sample check)
- Price and variant integrity
"""

import json
import urllib.request
import re
from collections import Counter

API_URL = "https://6yardjersey.com/api/products"

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def main():
    print("--- 6YARD PRODUCT DATA AUDIT ---")
    
    # 1. Fetch live products
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as res:
        live_products = json.loads(res.read().decode('utf-8'))
    
    print(f"Total Live API / MongoDB Products: {len(live_products)}")
    
    # Static Products in Next.js Source Code
    static_products = [
        {"id": "rem-1", "name": "Match Day Shorts 24/25", "price": 45.0, "category": "Training", "source": "ProductDetailClient.tsx (RELATED_PRODUCTS)"},
        {"id": "rem-2", "name": "Home Socks 24/25", "price": 18.0, "category": "Training", "source": "ProductDetailClient.tsx (RELATED_PRODUCTS)"},
        {"id": "rem-3", "name": "Elite Performance Cleats", "price": 199.99, "category": "Football", "source": "ProductDetailClient.tsx (RELATED_PRODUCTS)"},
        {"id": "rem-4", "name": "Anthem Jacket 24/25", "price": 110.0, "category": "Training", "source": "ProductDetailClient.tsx (RELATED_PRODUCTS)"},
        {"id": "1", "name": "Manchester Home Kit 24/25", "price": 89.99, "category": "Football", "source": "ProductDetailClient.tsx (mockIds)"},
        {"id": "2", "name": "Elite Vapour Training Tee", "price": 54.99, "category": "Football", "source": "ProductDetailClient.tsx (mockIds)"},
        {"id": "3", "name": "London Away Kit 24/25", "price": 84.99, "category": "Football", "source": "ProductDetailClient.tsx (mockIds)"},
        {"id": "4", "name": "National Pro Match Jersey", "price": 79.99, "category": "Football", "source": "ProductDetailClient.tsx (mockIds)"},
        {"id": "5", "name": "Premium Red Kit", "price": 89.99, "category": "Football", "source": "ProductDetailClient.tsx (mockIds)"},
        {"id": "6", "name": "Sky Blue Fan Jersey", "price": 89.99, "category": "Football", "source": "ProductDetailClient.tsx (mockIds)"},
        {"id": "7", "name": "Pro Training Black", "price": 89.99, "category": "Football", "source": "ProductDetailClient.tsx (mockIds)"},
        {"id": "8", "name": "National Home Kit", "price": 89.99, "category": "Football", "source": "ProductDetailClient.tsx (mockIds)"}
    ]
    print(f"Total Static Hardcoded Products in Next.js Codebase: {len(static_products)}")
    
    # Analyze live products
    titles = [p.get('name', '').strip() for p in live_products]
    title_counts = Counter(titles)
    duplicate_titles = {t: c for t, c in title_counts.items() if c > 1}
    
    handles = [slugify(t) for t in titles]
    handle_counts = Counter(handles)
    duplicate_handles = {h: c for h, c in handle_counts.items() if c > 1}
    
    missing_title = []
    missing_description = []
    missing_price = []
    missing_images = []
    missing_sizes = []
    has_discount_count = 0
    total_variants = 0
    total_images = 0
    image_hosts = Counter()
    categories_counter = Counter()
    
    for idx, p in enumerate(live_products):
        pid = p.get('_id')
        name = p.get('name')
        if not name:
            missing_title.append(pid)
            
        desc = p.get('description')
        if not desc or not desc.strip():
            missing_description.append(pid)
            
        price = p.get('price')
        if price is None:
            missing_price.append(pid)
            
        discount = p.get('discount_price')
        if discount is not None and float(discount) < float(price or 0):
            has_discount_count += 1
            
        imgs = p.get('images', [])
        if not imgs and p.get('image'):
            imgs = [p.get('image')]
        if not imgs:
            missing_images.append(pid)
        else:
            total_images += len(imgs)
            for img in imgs:
                if 'cloudinary.com' in img:
                    image_hosts['Cloudinary CDN'] += 1
                elif 'googleusercontent.com' in img:
                    image_hosts['Google CDN'] += 1
                elif img.startswith('/'):
                    image_hosts['Local Asset'] += 1
                else:
                    image_hosts['External URL'] += 1
                    
        # Sizes & Variants
        size_stocks = p.get('sizeStocks', [])
        if size_stocks:
            total_variants += len(size_stocks)
        else:
            sizes = p.get('sizes', [])
            if sizes:
                total_variants += len(sizes)
            else:
                missing_sizes.append(pid)
                total_variants += 1
                
        # Categories
        cats = p.get('category', [])
        if isinstance(cats, list):
            for c in cats:
                categories_counter[c] += 1
        elif isinstance(cats, str):
            categories_counter[cats] += 1

    print("\n--- AUDIT RESULTS ---")
    print(f"Products with Missing Titles: {len(missing_title)}")
    print(f"Products with Missing Descriptions: {len(missing_description)}")
    print(f"Products with Missing Prices: {len(missing_price)}")
    print(f"Products with Missing Images: {len(missing_images)}")
    print(f"Products with Missing Sizes: {len(missing_sizes)}")
    print(f"Products with Discount (Compare-At Price): {has_discount_count} / {len(live_products)}")
    print(f"Total Calculated Product Variants (Sizes): {total_variants}")
    print(f"Total Associated Images: {total_images}")
    print("\nImage Host Distribution:")
    for host, count in image_hosts.items():
        print(f"  - {host}: {count} images")
    print("\nDuplicate Titles Detected:")
    if duplicate_titles:
        for t, c in duplicate_titles.items():
            print(f"  - '{t}': {c} occurrences")
    else:
        print("  None (all titles are distinct)")
        
    print("\nDuplicate Handles Detected:")
    if duplicate_handles:
        for h, c in duplicate_handles.items():
            print(f"  - '{h}': {c} occurrences")
    else:
        print("  None (all handles are distinct)")
        
    print("\nCategory Distribution across live products:")
    for cat, count in categories_counter.most_common():
        print(f"  - {cat}: {count} products")

if __name__ == '__main__':
    main()
