#!/usr/bin/env python3
"""
6YARD STORE — MongoDB / API to Shopify Products CSV Exporter
Exports all 95 live products into official Shopify Product Import CSV format
and generates a 301 Redirects mapping file.
"""

import json
import csv
import re
import urllib.request
import os

API_URL = "https://6yardjersey.com/api/products"
OUTPUT_CSV = "/Users/mac/6yard-shopify/6yard_shopify_products_import.csv"
REDIRECTS_CSV = "/Users/mac/6yard-shopify/6yard_url_redirects.csv"

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def fetch_products():
    print(f"Fetching products from {API_URL}...")
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode('utf-8'))

def main():
    try:
        products = fetch_products()
        print(f"Successfully fetched {len(products)} products.")
    except Exception as e:
        print(f"Error fetching products: {e}")
        return

    fieldnames = [
        "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type",
        "Tags", "Published", "Option1 Name", "Option1 Value", "Option2 Name",
        "Option2 Value", "Option3 Name", "Option3 Value", "Variant SKU",
        "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty",
        "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price",
        "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable",
        "Variant Barcode", "Image Src", "Image Position", "Image Alt Text",
        "Gift Card", "SEO Title", "SEO Description", "Status"
    ]

    redirects = []
    seen_handles = {}

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for prod in products:
            prod_id = prod.get("_id") or prod.get("id", "")
            raw_name = prod.get("name", "Football Jersey").strip()
            handle = slugify(raw_name)

            if handle in seen_handles:
                seen_handles[handle] += 1
                handle = f"{handle}-{seen_handles[handle]}"
            else:
                seen_handles[handle] = 1

            if prod_id:
                redirects.append({
                    "Redirect from": f"/product/{prod_id}",
                    "Redirect to": f"/products/{handle}"
                })

            description = prod.get("description", "")
            # Convert newlines to HTML paragraphs/breaks
            body_html = "<p>" + description.replace("\r\n", "<br>").replace("\n", "<br>") + "</p>"

            vendor = "6YARD"
            category_tags = prod.get("category", [])
            if isinstance(category_tags, str):
                category_tags = [category_tags]

            tag_list = ["6YARD", "Football Jersey"]
            for cat in category_tags:
                if cat and cat.strip():
                    tag_list.append(f"Category:{cat.strip()}")

            sales_tag = prod.get("salesTag")
            if sales_tag and sales_tag.strip():
                tag_list.append(f"Sales:{sales_tag.strip()}")

            if prod.get("customNameNumber"):
                tag_list.append("Customizable")

            tags_str = ", ".join(tag_list)

            # Pricing
            raw_price = prod.get("price") or 499
            discount_price = prod.get("discount_price")
            if discount_price and float(discount_price) < float(raw_price):
                selling_price = float(discount_price)
                compare_price = float(raw_price)
            else:
                selling_price = float(raw_price)
                compare_price = ""

            images = prod.get("images", [])
            if not images and prod.get("image"):
                images = [prod.get("image")]

            # Sizes / Variants
            size_stocks = prod.get("sizeStocks", [])
            if not size_stocks:
                available_sizes = prod.get("sizes", [])
                if available_sizes:
                    size_stocks = [{"size": s, "stock": prod.get("stock", 5)} for s in available_sizes]
                else:
                    size_stocks = [{"size": "Standard", "stock": prod.get("stock", 5)}]

            # Map rows: 1 row per variant, pairing images as available
            max_rows = max(len(size_stocks), len(images))

            for row_idx in range(max_rows):
                is_first_row = (row_idx == 0)
                row_data = {
                    "Handle": handle,
                    "Title": raw_name if is_first_row else "",
                    "Body (HTML)": body_html if is_first_row else "",
                    "Vendor": vendor if is_first_row else "",
                    "Product Category": "Apparel & Accessories > Clothing > Shirts & Tops" if is_first_row else "",
                    "Type": "Football Jersey" if is_first_row else "",
                    "Tags": tags_str if is_first_row else "",
                    "Published": "TRUE" if is_first_row else "",
                    "Option1 Name": "Size" if is_first_row else "",
                    "Option1 Value": "",
                    "Option2 Name": "",
                    "Option2 Value": "",
                    "Option3 Name": "",
                    "Option3 Value": "",
                    "Variant SKU": "",
                    "Variant Grams": "250" if row_idx < len(size_stocks) else "",
                    "Variant Inventory Tracker": "shopify" if row_idx < len(size_stocks) else "",
                    "Variant Inventory Qty": "",
                    "Variant Inventory Policy": "deny" if row_idx < len(size_stocks) else "",
                    "Variant Fulfillment Service": "manual" if row_idx < len(size_stocks) else "",
                    "Variant Price": "",
                    "Variant Compare At Price": "",
                    "Variant Requires Shipping": "TRUE" if row_idx < len(size_stocks) else "",
                    "Variant Taxable": "FALSE" if row_idx < len(size_stocks) else "",
                    "Variant Barcode": "",
                    "Image Src": "",
                    "Image Position": "",
                    "Image Alt Text": "",
                    "Gift Card": "FALSE" if is_first_row else "",
                    "SEO Title": raw_name if is_first_row else "",
                    "SEO Description": description[:160] if is_first_row else "",
                    "Status": "active" if is_first_row else ""
                }

                if row_idx < len(size_stocks):
                    variant_info = size_stocks[row_idx]
                    size_name = variant_info.get("size", "M").strip()
                    stock_qty = variant_info.get("stock", 0)

                    row_data["Option1 Value"] = size_name
                    clean_sku = f"6YD-{slugify(raw_name)[:15]}-{size_name}".upper()
                    row_data["Variant SKU"] = clean_sku
                    row_data["Variant Inventory Qty"] = stock_qty
                    row_data["Variant Price"] = f"{selling_price:.2f}"
                    if compare_price:
                        row_data["Variant Compare At Price"] = f"{compare_price:.2f}"

                if row_idx < len(images):
                    row_data["Image Src"] = images[row_idx]
                    row_data["Image Position"] = str(row_idx + 1)
                    row_data["Image Alt Text"] = f"{raw_name} - View {row_idx + 1}"

                writer.writerow(row_data)

    print(f"Exported {len(products)} products to {OUTPUT_CSV}")

    with open(REDIRECTS_CSV, mode="w", newline="", encoding="utf-8") as rfile:
        rwriter = csv.DictWriter(rfile, fieldnames=["Redirect from", "Redirect to"])
        rwriter.writeheader()
        rwriter.writerows(redirects)

    print(f"Exported {len(redirects)} 301 redirects to {REDIRECTS_CSV}")

if __name__ == "__main__":
    main()
