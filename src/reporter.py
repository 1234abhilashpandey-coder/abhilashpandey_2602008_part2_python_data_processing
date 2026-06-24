"""
reporter.py
-----------
Writes pipeline output files:
  - outputs/cleaned_orders.csv
  - outputs/rejected_records.csv
  - outputs/summary_report.txt
Uses only Python's built-in csv and os modules.
"""

import csv
import os

# Required column order for cleaned_orders.csv
CLEANED_COLUMNS = [
    "order_id",
    "customer_id",
    "customer_name",
    "city",
    "product_id",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "total_amount",
    "order_status",
    "payment_method",
    "order_date",
]

# Column order for rejected_records.csv
REJECTED_COLUMNS = [
    "order_id",
    "customer_id",
    "customer_name",
    "city",
    "product_id",
    "quantity",
    "unit_price",
    "order_status",
    "payment_method",
    "order_date",
    "rejection_reason",
]


def ensure_dir(path):
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def write_csv(filepath, records, fieldnames):
    """
    Write a list of dictionaries to a CSV file.

    Args:
        filepath (str): Output file path.
        records (list): List of record dicts.
        fieldnames (list): Column order for the CSV.
    """
    ensure_dir(os.path.dirname(filepath))
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)
        print(f"[REPORTER] Written {len(records)} records to '{filepath}'")
    except Exception as e:
        print(f"[ERROR] Could not write '{filepath}': {e}")


def write_cleaned_orders(cleaned_orders, output_dir="outputs"):
    """Write cleaned valid orders to cleaned_orders.csv."""
    filepath = os.path.join(output_dir, "cleaned_orders.csv")
    write_csv(filepath, cleaned_orders, CLEANED_COLUMNS)


def write_rejected_records(rejected_orders, output_dir="outputs"):
    """Write rejected invalid orders (with reasons) to rejected_records.csv."""
    filepath = os.path.join(output_dir, "rejected_records.csv")
    # Use REJECTED_COLUMNS; any missing columns default to empty
    write_csv(filepath, rejected_orders, REJECTED_COLUMNS)


def write_summary_report(raw_count, cleaned_count, rejected_count, stats, output_dir="outputs"):
    """
    Write a plain-text business summary report to summary_report.txt.

    Args:
        raw_count (int): Number of raw records.
        cleaned_count (int): Number of cleaned records.
        rejected_count (int): Number of rejected records.
        stats (dict): Analytics dictionary from analyzer.py.
        output_dir (str): Output directory path.
    """
    ensure_dir(output_dir)
    filepath = os.path.join(output_dir, "summary_report.txt")

    sep_thick = "=" * 65
    sep_thin = "-" * 45

    try:
        with open(filepath, "w", encoding="utf-8") as f:

            f.write(sep_thick + "\n")
            f.write("         BUSINESS SUMMARY REPORT\n")
            f.write("         Python Data Processing Pipeline\n")
            f.write(sep_thick + "\n\n")

            # 1. Overview
            f.write("1. RECORD OVERVIEW\n")
            f.write(sep_thin + "\n")
            f.write(f"   Total Raw Records          : {raw_count}\n")
            f.write(f"   Total Cleaned Records      : {cleaned_count}\n")
            f.write(f"   Total Rejected Records     : {rejected_count}\n\n")

            # 2. Total Revenue
            f.write("2. TOTAL REVENUE (Completed Orders)\n")
            f.write(sep_thin + "\n")
            f.write(f"   Rs. {stats['total_revenue']:>12,.2f}\n\n")

            # 3. Revenue by Category
            f.write("3. REVENUE BY CATEGORY\n")
            f.write(sep_thin + "\n")
            rev_cat = stats.get("revenue_by_category", {})
            if rev_cat:
                for cat, rev in rev_cat.items():
                    f.write(f"   {cat:<22} : Rs. {rev:>12,.2f}\n")
            else:
                f.write("   No data available.\n")
            f.write("\n")

            # 4. Revenue by City
            f.write("4. REVENUE BY CITY\n")
            f.write(sep_thin + "\n")
            rev_city = stats.get("revenue_by_city", {})
            if rev_city:
                for city, rev in rev_city.items():
                    f.write(f"   {city:<22} : Rs. {rev:>12,.2f}\n")
            else:
                f.write("   No data available.\n")
            f.write("\n")

            # 5. Orders by Payment Method
            f.write("5. NUMBER OF ORDERS BY PAYMENT METHOD\n")
            f.write(sep_thin + "\n")
            pay_counts = stats.get("payment_method_counts", {})
            if pay_counts:
                for method, count in pay_counts.items():
                    f.write(f"   {method:<22} : {count} orders\n")
            else:
                f.write("   No data available.\n")
            f.write("\n")

            # 6. Top 3 Customers by Total Spend
            f.write("6. TOP 3 CUSTOMERS BY TOTAL SPEND\n")
            f.write(sep_thin + "\n")
            top_customers = stats.get("top_customers", [])
            if top_customers:
                for i, (customer, spend) in enumerate(top_customers, 1):
                    f.write(f"   {i}. {customer:<35} Rs. {spend:>12,.2f}\n")
            else:
                f.write("   No data available.\n")
            f.write("\n")

            # 7. Product with Highest Quantity Sold
            f.write("7. PRODUCT WITH HIGHEST QUANTITY SOLD\n")
            f.write(sep_thin + "\n")
            top_prod, top_qty = stats.get("top_product", (None, 0))
            if top_prod:
                f.write(f"   {top_prod} — {top_qty} units sold\n\n")
            else:
                f.write("   No data available.\n\n")

            # 8. Category with Highest Revenue
            f.write("8. CATEGORY WITH HIGHEST REVENUE\n")
            f.write(sep_thin + "\n")
            top_cat, top_cat_rev = stats.get("top_category", (None, 0))
            if top_cat:
                f.write(f"   {top_cat} — Rs. {top_cat_rev:,.2f}\n\n")
            else:
                f.write("   No data available.\n\n")

            # 9. Rejection Counts by Reason
            f.write("9. COUNT OF REJECTED RECORDS BY REASON\n")
            f.write(sep_thin + "\n")
            rej_counts = stats.get("rejection_counts", {})
            if rej_counts:
                for reason, count in rej_counts.items():
                    f.write(f"   {reason:<38}: {count}\n")
            else:
                f.write("   No rejections.\n")
            f.write("\n")

            # 10. Business Insights
            f.write("10. KEY BUSINESS INSIGHTS\n")
            f.write(sep_thin + "\n")
            insights = stats.get("insights", [])
            if insights:
                for i, insight in enumerate(insights, 1):
                    # Word-wrap at ~60 chars
                    words = insight.split()
                    line = f"   {i}. "
                    indent = "      "
                    char_count = len(line)
                    f.write(line)
                    for word in words:
                        if char_count + len(word) + 1 > 70 and char_count > len(line):
                            f.write("\n" + indent)
                            char_count = len(indent)
                        f.write(word + " ")
                        char_count += len(word) + 1
                    f.write("\n\n")
            else:
                f.write("   No insights generated.\n\n")

            f.write(sep_thick + "\n")
            f.write("                  END OF REPORT\n")
            f.write(sep_thick + "\n")

        print(f"[REPORTER] Summary report written to '{filepath}'")

    except Exception as e:
        print(f"[ERROR] Could not write summary report: {e}")
