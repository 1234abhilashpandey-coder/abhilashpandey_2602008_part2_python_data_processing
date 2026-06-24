from datetime import datetime

# --- Constants ---
VALID_STATUSES = {"Completed", "Pending", "Cancelled", "Shipped"}
VALID_PAYMENT_METHODS = {"Credit Card", "Debit Card", "UPI", "Cash", "Net Banking"}
DATE_FORMAT = "%Y-%m-%d"
PRICE_TOLERANCE = 0.50  # Allow up to 0.50 difference for floating-point safety

# --- String Utilities ---

def trim_spaces(value):
    """Remove leading, trailing, and extra internal spaces from a string."""
    if value is None:
        return ""
    return " ".join(str(value).split())


def standardize_name(name):
    """Standardize customer name: trim spaces and apply title case."""
    return trim_spaces(name).title()


def standardize_city(city):
    """Standardize city name: trim spaces and apply title case."""
    return trim_spaces(city).title()


def standardize_status(status):
    """
    Standardize order status value.
    Maps known variants to canonical values.
    """
    cleaned = trim_spaces(status).title()
    status_map = {
        "Complete": "Completed",
        "Completed": "Completed",
        "Pending": "Pending",
        "Cancelled": "Cancelled",
        "Canceled": "Cancelled",
        "Shipped": "Shipped",
        "Dispatched": "Shipped",
    }
    return status_map.get(cleaned, cleaned)


def standardize_payment(method):
    """
    Standardize payment method value.
    Maps known variants to canonical values.
    """
    cleaned = trim_spaces(method).title()
    payment_map = {
        "Credit Card": "Credit Card",
        "Creditcard": "Credit Card",
        "Debit Card": "Debit Card",
        "Debitcard": "Debit Card",
        "Upi": "UPI",
        "Cash": "Cash",
        "Net Banking": "Net Banking",
        "Netbanking": "Net Banking",
        "Net-Banking": "Net Banking",
    }
    return payment_map.get(cleaned, cleaned)


# --- Validation Functions ---

def validate_quantity(quantity_str):
    """
    Validate that quantity is a positive integer.

    Returns:
        tuple: (int quantity, None) on success, (None, error_str) on failure.
    """
    try:
        qty = int(float(trim_spaces(str(quantity_str))))
        if qty <= 0:
            return None, f"Invalid quantity: {quantity_str} (must be > 0)"
        return qty, None
    except (ValueError, TypeError):
        return None, f"Invalid quantity format: '{quantity_str}'"


def validate_date(date_str):
    """
    Validate that order_date is in YYYY-MM-DD format.

    Returns:
        tuple: (date_str, None) on success, (None, error_str) on failure.
    """
    try:
        cleaned = trim_spaces(str(date_str))
        datetime.strptime(cleaned, DATE_FORMAT)
        return cleaned, None
    except ValueError:
        return None, f"Invalid date format: '{date_str}' (expected YYYY-MM-DD)"


def validate_product_id(product_id, product_master):
    """
    Validate that product_id exists in the product master.

    Returns:
        tuple: (True, None) if valid, (False, error_str) if not.
    """
    if product_id in product_master:
        return True, None
    return False, f"Product ID not found in master: '{product_id}'"


def validate_unit_price(unit_price_str, product_id, product_master):
    """
    Validate unit_price against the standard_price in product master.

    Returns:
        tuple: (float price, None) on success, (float price, error_str) on mismatch,
               (None, error_str) on parse failure.
    """
    try:
        unit_price = float(trim_spaces(str(unit_price_str)))
        if product_id in product_master:
            standard_price = float(product_master[product_id]["standard_price"])
            if abs(unit_price - standard_price) > PRICE_TOLERANCE:
                return unit_price, (
                    f"Unit price mismatch: order has {unit_price:.2f}, "
                    f"standard is {standard_price:.2f}"
                )
        return unit_price, None
    except (ValueError, TypeError):
        return None, f"Invalid unit price: '{unit_price_str}'"


# --- Record-Level Cleaning ---

def clean_record(record, product_master, seen_order_ids):
    """
    Clean and validate a single order record.

    Applies all standardization rules and checks all validation conditions.
    Collects ALL rejection reasons (does not stop at first error).

    Args:
        record (dict): Raw order row.
        product_master (dict): Dict of product_id -> product info.
        seen_order_ids (set): Set of already-processed order IDs (for duplicate detection).

    Returns:
        tuple: (cleaned_dict, list_of_rejection_reasons)
               If list_of_rejection_reasons is empty, the record is valid.
    """
    rejection_reasons = []
    cleaned = {}

    # --- order_id ---
    order_id = trim_spaces(record.get("order_id", ""))
    if not order_id:
        rejection_reasons.append("Missing order ID")
    elif order_id in seen_order_ids:
        rejection_reasons.append(f"Duplicate order ID: '{order_id}'")
    cleaned["order_id"] = order_id

    # --- customer_id ---
    cleaned["customer_id"] = trim_spaces(record.get("customer_id", ""))

    # --- customer_name ---
    customer_name = standardize_name(record.get("customer_name", ""))
    if not customer_name:
        rejection_reasons.append("Missing customer name")
    cleaned["customer_name"] = customer_name

    # --- city ---
    city = standardize_city(record.get("city", ""))
    if not city:
        rejection_reasons.append("Missing city value")
    cleaned["city"] = city

    # --- product_id ---
    product_id = trim_spaces(record.get("product_id", ""))
    product_valid, product_error = validate_product_id(product_id, product_master)
    if not product_valid:
        rejection_reasons.append(product_error)
    cleaned["product_id"] = product_id

    # --- product_name and category (from master) ---
    if product_valid and product_id in product_master:
        cleaned["product_name"] = product_master[product_id]["product_name"]
        cleaned["category"] = product_master[product_id]["category"]
    else:
        cleaned["product_name"] = ""
        cleaned["category"] = ""

    # --- quantity ---
    qty, qty_error = validate_quantity(record.get("quantity", ""))
    if qty_error:
        rejection_reasons.append(qty_error)
    cleaned["quantity"] = qty if qty is not None else 0

    # --- unit_price ---
    unit_price, price_error = validate_unit_price(
        record.get("unit_price", ""), product_id, product_master
    )
    if price_error:
        rejection_reasons.append(price_error)
    cleaned["unit_price"] = unit_price if unit_price is not None else 0.0

    # --- total_amount (always recalculated) ---
    if qty and unit_price:
        cleaned["total_amount"] = round(qty * unit_price, 2)
    else:
        cleaned["total_amount"] = 0.0

    # --- order_status ---
    order_status = standardize_status(record.get("order_status", ""))
    if order_status not in VALID_STATUSES:
        rejection_reasons.append(f"Invalid order status: '{order_status}'")
    cleaned["order_status"] = order_status

    # --- payment_method ---
    payment_method = standardize_payment(record.get("payment_method", ""))
    if payment_method not in VALID_PAYMENT_METHODS:
        rejection_reasons.append(f"Invalid payment method: '{payment_method}'")
    cleaned["payment_method"] = payment_method

    # --- order_date ---
    order_date, date_error = validate_date(record.get("order_date", ""))
    if date_error:
        rejection_reasons.append(date_error)
    cleaned["order_date"] = order_date if order_date else trim_spaces(record.get("order_date", ""))

    return cleaned, rejection_reasons


# --- Batch Processing ---

def process_orders(raw_orders, product_master):
    """
    Process all raw orders through cleaning and validation.

    For each record:
      - If valid after cleaning: added to cleaned_orders
      - If any validation fails: added to rejected_orders with reason(s)

    Duplicate detection: the first occurrence of an order_id is processed normally;
    any subsequent occurrence is rejected as a duplicate.

    Args:
        raw_orders (list): List of raw order dicts from loader.
        product_master (dict): Dict of product_id -> product info.

    Returns:
        tuple: (cleaned_orders list, rejected_orders list)
    """
    cleaned_orders = []
    rejected_orders = []
    seen_order_ids = set()

    for record in raw_orders:
        order_id = trim_spaces(record.get("order_id", ""))
        cleaned, reasons = clean_record(record, product_master, seen_order_ids)

        if reasons:
            # Build rejected record: keep original raw values + add reason column
            rejected = dict(record)
            rejected["rejection_reason"] = "; ".join(reasons)
            rejected_orders.append(rejected)
        else:
            cleaned_orders.append(cleaned)

        # Mark this order_id as seen (for future duplicate detection)
        if order_id:
            seen_order_ids.add(order_id)

    return cleaned_orders, rejected_orders
