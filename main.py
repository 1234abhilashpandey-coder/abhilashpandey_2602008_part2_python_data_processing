"""
main.py
-------
Entry point for the Python Data Processing Pipeline.
Orchestrates all pipeline tasks by calling functions from the src/ package.

Usage:
    python main.py
"""

import os
import sys

# Ensure project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.loader import load_orders, load_product_master
from src.cleaner import process_orders
from src.analyzer import (
    get_total_revenue,
    get_revenue_by_category,
    get_revenue_by_city,
    get_orders_by_payment_method,
    get_top_customers,
    get_product_highest_quantity,
    get_category_highest_revenue,
    get_rejection_reason_counts,
    generate_business_insights,
)
from src.reporter import (
    write_cleaned_orders,
    write_rejected_records,
    write_summary_report,
)


def run_pipeline(data_dir="data", output_dir="outputs"):
    """
    Execute the complete data processing pipeline.

    Steps:
        1. Load raw data files
        2. Clean orders and validate records
        3. Save rejected records with reasons
        4. Save cleaned valid orders
        5. Compute analytics and generate summary report
    """
    print("\n" + "=" * 60)
    print("       PYTHON DATA PROCESSING PIPELINE")
    print("=" * 60)

    # ── TASK 1: Load Data ──────────────────────────────────────────
    print("\n[TASK 1] Loading data files...")
    raw_orders = load_orders(data_dir)
    product_master = load_product_master(data_dir)

    if not raw_orders:
        print("[FATAL] No orders to process. Exiting.")
        sys.exit(1)
    if not product_master:
        print("[FATAL] Product master is empty. Exiting.")
        sys.exit(1)

    print(f"         Raw orders    : {len(raw_orders)}")
    print(f"         Products      : {len(product_master)}")

    # ── TASK 2 & 3: Clean + Reject ─────────────────────────────────
    print("\n[TASK 2] Applying cleaning and validation rules...")
    cleaned_orders, rejected_orders = process_orders(raw_orders, product_master)
    print(f"         Cleaned orders  : {len(cleaned_orders)}")
    print(f"         Rejected records: {len(rejected_orders)}")

    # ── TASK 3: Save Rejected Records ─────────────────────────────
    print("\n[TASK 3] Writing rejected records...")
    write_rejected_records(rejected_orders, output_dir)

    # ── TASK 4: Save Cleaned Dataset ──────────────────────────────
    print("\n[TASK 4] Writing cleaned orders...")
    write_cleaned_orders(cleaned_orders, output_dir)

    # ── TASK 5: Business Summary Report ───────────────────────────
    print("\n[TASK 5] Computing analytics and writing summary report...")

    total_revenue = get_total_revenue(cleaned_orders)
    rev_by_cat = get_revenue_by_category(cleaned_orders)
    rev_by_city = get_revenue_by_city(cleaned_orders)
    pay_counts = get_orders_by_payment_method(cleaned_orders)
    top_customers = get_top_customers(cleaned_orders, n=3)
    top_product = get_product_highest_quantity(cleaned_orders)
    top_category = get_category_highest_revenue(cleaned_orders)
    rej_counts = get_rejection_reason_counts(rejected_orders)

    stats = {
        "total_revenue": total_revenue,
        "revenue_by_category": rev_by_cat,
        "revenue_by_city": rev_by_city,
        "payment_method_counts": pay_counts,
        "top_customers": top_customers,
        "top_product": top_product,
        "top_category": top_category,
        "rejection_counts": rej_counts,
    }

    # Add plain-English insights
    stats["insights"] = generate_business_insights(
        stats,
        raw_count=len(raw_orders),
        rejected_count=len(rejected_orders),
        cleaned_count=len(cleaned_orders),
    )

    write_summary_report(
        raw_count=len(raw_orders),
        cleaned_count=len(cleaned_orders),
        rejected_count=len(rejected_orders),
        stats=stats,
        output_dir=output_dir,
    )

    # ── Summary ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("       PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"\n  Raw records      : {len(raw_orders)}")
    print(f"  Cleaned records  : {len(cleaned_orders)}")
    print(f"  Rejected records : {len(rejected_orders)}")
    print(f"  Total Revenue    : Rs. {total_revenue:,.2f}")
    print(f"\n  Output files saved to: {output_dir}/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_pipeline()
