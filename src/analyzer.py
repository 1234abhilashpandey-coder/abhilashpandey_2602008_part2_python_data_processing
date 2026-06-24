"""
analyzer.py
-----------
Computes business statistics and analytics from cleaned order data.
Uses only Python lists, dictionaries, and loops. No pandas.
"""


def get_total_revenue(cleaned_orders):
    """
    Calculate total revenue from Completed orders only.

    Args:
        cleaned_orders (list): List of cleaned order dicts.

    Returns:
        float: Total revenue from completed orders.
    """
    total = 0.0
    for order in cleaned_orders:
        if order.get("order_status") == "Completed":
            try:
                total += float(order.get("total_amount", 0))
            except (ValueError, TypeError):
                pass
    return round(total, 2)


def get_revenue_by_category(cleaned_orders):
    """
    Calculate total revenue by product category (Completed orders only).

    Returns:
        dict: {category: revenue} sorted descending by revenue.
    """
    revenue = {}
    for order in cleaned_orders:
        if order.get("order_status") == "Completed":
            cat = order.get("category", "Unknown")
            try:
                amount = float(order.get("total_amount", 0))
            except (ValueError, TypeError):
                amount = 0.0
            revenue[cat] = revenue.get(cat, 0.0) + amount

    # Sort by revenue descending
    sorted_revenue = dict(sorted(revenue.items(), key=lambda x: x[1], reverse=True))
    return {k: round(v, 2) for k, v in sorted_revenue.items()}


def get_revenue_by_city(cleaned_orders):
    """
    Calculate total revenue by city (Completed orders only).

    Returns:
        dict: {city: revenue} sorted descending by revenue.
    """
    revenue = {}
    for order in cleaned_orders:
        if order.get("order_status") == "Completed":
            city = order.get("city", "Unknown")
            try:
                amount = float(order.get("total_amount", 0))
            except (ValueError, TypeError):
                amount = 0.0
            revenue[city] = revenue.get(city, 0.0) + amount

    sorted_revenue = dict(sorted(revenue.items(), key=lambda x: x[1], reverse=True))
    return {k: round(v, 2) for k, v in sorted_revenue.items()}


def get_orders_by_payment_method(cleaned_orders):
    """
    Count number of orders by payment method (all statuses).

    Returns:
        dict: {payment_method: count} sorted descending by count.
    """
    counts = {}
    for order in cleaned_orders:
        method = order.get("payment_method", "Unknown")
        counts[method] = counts.get(method, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def get_top_customers(cleaned_orders, n=3):
    """
    Identify top N customers by total spend (all statuses included).

    Args:
        cleaned_orders (list): Cleaned order records.
        n (int): Number of top customers to return.

    Returns:
        list: List of tuples [(customer_label, total_spend), ...]
    """
    spend = {}
    names = {}
    for order in cleaned_orders:
        cid = order.get("customer_id", "Unknown")
        cname = order.get("customer_name", "Unknown")
        names[cid] = cname
        try:
            amount = float(order.get("total_amount", 0))
        except (ValueError, TypeError):
            amount = 0.0
        spend[cid] = spend.get(cid, 0.0) + amount

    sorted_spend = sorted(spend.items(), key=lambda x: x[1], reverse=True)
    result = []
    for cid, total in sorted_spend[:n]:
        label = f"{cid} ({names.get(cid, 'Unknown')})"
        result.append((label, round(total, 2)))
    return result


def get_product_highest_quantity(cleaned_orders):
    """
    Find the product with the highest total quantity sold.

    Returns:
        tuple: (product_name, total_quantity) or (None, 0) if empty.
    """
    qty_totals = {}
    names = {}
    for order in cleaned_orders:
        pid = order.get("product_id", "Unknown")
        pname = order.get("product_name", pid)
        names[pid] = pname
        try:
            q = int(order.get("quantity", 0))
        except (ValueError, TypeError):
            q = 0
        qty_totals[pid] = qty_totals.get(pid, 0) + q

    if not qty_totals:
        return None, 0
    top_pid = max(qty_totals, key=qty_totals.get)
    return names.get(top_pid, top_pid), qty_totals[top_pid]


def get_category_highest_revenue(cleaned_orders):
    """
    Find the category with the highest total revenue.

    Returns:
        tuple: (category_name, revenue) or (None, 0) if empty.
    """
    rev = get_revenue_by_category(cleaned_orders)
    if not rev:
        return None, 0
    top_cat = max(rev, key=rev.get)
    return top_cat, rev[top_cat]


def get_rejection_reason_counts(rejected_orders):
    """
    Count rejected records grouped by rejection reason category.

    Args:
        rejected_orders (list): List of rejected order dicts with 'rejection_reason' key.

    Returns:
        dict: {reason_label: count} sorted descending.
    """
    counts = {}
    for order in rejected_orders:
        raw_reason = order.get("rejection_reason", "Unknown")
        # Split multi-reason rejections and categorize each
        parts = raw_reason.split("; ")
        for part in parts:
            part_lower = part.lower()
            if "duplicate" in part_lower:
                key = "Duplicate order ID"
            elif "missing customer name" in part_lower:
                key = "Missing customer name"
            elif "missing city" in part_lower:
                key = "Missing city"
            elif "invalid quantity" in part_lower or "quantity" in part_lower:
                key = "Invalid quantity"
            elif "product id not found" in part_lower:
                key = "Product ID not found"
            elif "invalid order status" in part_lower:
                key = "Invalid order status"
            elif "invalid payment method" in part_lower:
                key = "Invalid payment method"
            elif "invalid date" in part_lower or "date format" in part_lower:
                key = "Invalid date format"
            elif "unit price mismatch" in part_lower or "price" in part_lower:
                key = "Unit price mismatch"
            elif "missing order id" in part_lower:
                key = "Missing order ID"
            else:
                key = part.strip()
            counts[key] = counts.get(key, 0) + 1

    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def generate_business_insights(stats, raw_count, rejected_count, cleaned_count):
    """
    Generate at least 3 plain-English business insights from pipeline statistics.

    Args:
        stats (dict): Aggregated stats dictionary.
        raw_count (int): Total raw records.
        rejected_count (int): Total rejected records.
        cleaned_count (int): Total cleaned records.

    Returns:
        list: List of insight strings.
    """
    insights = []

    # Insight 1: Data quality
    rejection_rate = (rejected_count / raw_count * 100) if raw_count > 0 else 0
    insights.append(
        f"Data Quality: {rejection_rate:.1f}% of raw records ({rejected_count} out of "
        f"{raw_count}) were rejected due to quality issues. Implementing stricter data "
        f"entry validation at the source could significantly improve pipeline efficiency."
    )

    # Insight 2: Top revenue category
    rev_by_cat = stats.get("revenue_by_category", {})
    if rev_by_cat:
        top_cat = list(rev_by_cat.keys())[0]
        top_rev = list(rev_by_cat.values())[0]
        total_rev = stats.get("total_revenue", 1)
        pct = (top_rev / total_rev * 100) if total_rev > 0 else 0
        insights.append(
            f"Top Revenue Driver: '{top_cat}' leads all categories with Rs. {top_rev:,.2f} "
            f"in revenue ({pct:.1f}% of total). Investing in this category's inventory and "
            f"promotions could yield the highest returns."
        )

    # Insight 3: Top city
    rev_by_city = stats.get("revenue_by_city", {})
    if rev_by_city:
        top_city = list(rev_by_city.keys())[0]
        city_rev = list(rev_by_city.values())[0]
        insights.append(
            f"Geographic Focus: '{top_city}' is the highest-revenue city at Rs. {city_rev:,.2f}. "
            f"Increasing delivery coverage, local partnerships, and targeted marketing in "
            f"this region could further boost sales."
        )

    # Insight 4: Most popular payment method
    payment_counts = stats.get("payment_method_counts", {})
    if payment_counts:
        top_pm = list(payment_counts.keys())[0]
        pm_count = list(payment_counts.values())[0]
        insights.append(
            f"Payment Preference: '{top_pm}' is the most preferred payment method with "
            f"{pm_count} orders. Ensuring seamless, reliable processing for this method "
            f"and offering exclusive discounts could improve customer retention."
        )

    return insights
