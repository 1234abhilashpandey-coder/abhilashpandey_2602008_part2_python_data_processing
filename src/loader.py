"""
loader.py
---------
Handles loading of CSV data files into Python lists and dictionaries.
No pandas is used — only Python's built-in csv module.
"""

import csv
import os


def load_csv(filepath):
    """
    Load a CSV file and return a list of dictionaries.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        list: List of row dictionaries. Empty list on failure.
    """
    records = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        print(f"[LOADER] Loaded {len(records)} records from '{filepath}'")
        return records
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return []
    except PermissionError:
        print(f"[ERROR] Permission denied reading: {filepath}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to load '{filepath}': {e}")
        return []


def load_orders(data_dir="data"):
    """
    Load raw_orders.csv from the data directory.

    Args:
        data_dir (str): Directory containing data files.

    Returns:
        list: List of raw order dictionaries.
    """
    filepath = os.path.join(data_dir, "raw_orders.csv")
    orders = load_csv(filepath)
    if not orders:
        print("[WARNING] No orders loaded. Check raw_orders.csv exists in data/")
    return orders


def load_product_master(data_dir="data"):
    """
    Load product_master.csv and return as a dictionary keyed by product_id.

    Args:
        data_dir (str): Directory containing data files.

    Returns:
        dict: Dictionary mapping product_id -> product record dict.
    """
    filepath = os.path.join(data_dir, "product_master.csv")
    records = load_csv(filepath)
    product_dict = {}
    for record in records:
        pid = record.get("product_id", "").strip()
        if pid:
            product_dict[pid] = record
    if not product_dict:
        print("[WARNING] No products loaded. Check product_master.csv exists in data/")
    return product_dict
