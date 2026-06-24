# Test Cases — Python Data Processing Pipeline

## Overview
This document contains 12 test cases covering all major validation and cleaning scenarios in the pipeline.

Each test case includes: **Input Condition**, **Expected Output**, and **Reason**.

---

## Test Case 1: Valid Record (Clean Pass-Through)

**Input Condition:**
```
order_id=ORD001, customer_id=C001, customer_name=Rahul Sharma,
city=Mumbai, product_id=P001, quantity=1, unit_price=45000.00,
order_status=Completed, payment_method=Credit Card, order_date=2026-01-10
```

**Expected Output:**
- Record appears in `cleaned_orders.csv`
- `total_amount` = 45000.00 (recalculated)
- `product_name` = Laptop, `category` = Electronics (enriched from master)
- Record does **not** appear in `rejected_records.csv`

**Reason:**
All fields are valid, product ID exists in master, price matches, date format is correct, status and payment method are valid.

---

## Test Case 2: Duplicate Order ID

**Input Condition:**
```
order_id=ORD002 appears twice — first at row 2 and again at row 65
Both have different products and dates
```

**Expected Output:**
- First occurrence (row 2) → `cleaned_orders.csv`
- Second occurrence (row 65) → `rejected_records.csv`
- `rejection_reason` = "Duplicate order ID: 'ORD002'"

**Reason:**
The pipeline tracks seen order IDs. The second occurrence of the same order_id must be rejected to prevent double-counting.

---

## Test Case 3: Missing Customer Name

**Input Condition:**
```
order_id=ORD015, customer_name="" (empty), all other fields valid
```

**Expected Output:**
- Record appears in `rejected_records.csv`
- `rejection_reason` contains "Missing customer name"

**Reason:**
A customer name is mandatory for business records. An order with no identifiable customer cannot be processed.

---

## Test Case 4: Missing City Value

**Input Condition:**
```
order_id=ORD020, city="" (empty), all other fields valid
```

**Expected Output:**
- Record appears in `rejected_records.csv`
- `rejection_reason` contains "Missing city value"

**Reason:**
City is required for geographic analysis and order fulfilment routing.

---

## Test Case 5: Invalid Quantity — Zero

**Input Condition:**
```
order_id=ORD025, quantity=0, all other fields valid
```

**Expected Output:**
- Record appears in `rejected_records.csv`
- `rejection_reason` contains "Invalid quantity: 0 (must be > 0)"

**Reason:**
An order with zero quantity has no business value and is likely a data entry error.

---

## Test Case 6: Invalid Quantity — Negative Value

**Input Condition:**
```
order_id=ORD040, quantity=-2, all other fields valid
```

**Expected Output:**
- Record appears in `rejected_records.csv`
- `rejection_reason` contains "Invalid quantity: -2 (must be > 0)"

**Reason:**
Negative quantities are logically impossible for an order and indicate data corruption.

---

## Test Case 7: Invalid Product ID (Not in Master)

**Input Condition:**
```
order_id=ORDXXX, product_id=P999 (does not exist in product_master.csv)
```

**Expected Output:**
- Record appears in `rejected_records.csv`
- `rejection_reason` contains "Product ID not found in master: 'P999'"

**Reason:**
Orders referencing non-existent products cannot be enriched with product name or category and must be rejected.

---

## Test Case 8: Invalid Payment Method

**Input Condition:**
```
order_id=ORD055, payment_method=Bitcoin
order_id=ORD065, payment_method=Cheque
```

**Expected Output:**
- Both records appear in `rejected_records.csv`
- `rejection_reason` contains "Invalid payment method: 'Bitcoin'" / "Invalid payment method: 'Cheque'"

**Reason:**
Only Credit Card, Debit Card, UPI, Cash, and Net Banking are accepted. Unrecognised methods cannot be processed.

---

## Test Case 9: Invalid Order Status

**Input Condition:**
```
order_id=ORD050, order_status=Delivered
order_id=ORD059, order_status=Processing
```

**Expected Output:**
- Both appear in `rejected_records.csv`
- `rejection_reason` contains "Invalid order status: 'Delivered'" / "Invalid order status: 'Processing'"

**Reason:**
Only Completed, Pending, Shipped, and Cancelled are valid. Unrecognised statuses indicate bad data from upstream systems.

---

## Test Case 10: Unit Price Mismatch with Product Master

**Input Condition:**
```
order_id=ORD045, product_id=P001 (Laptop), unit_price=40000.00
standard_price from product_master = 45000.00
```

**Expected Output:**
- Record appears in `rejected_records.csv`
- `rejection_reason` contains "Unit price mismatch: order has 40000.00, standard is 45000.00"

**Reason:**
Unit prices must match the product master to prevent revenue miscalculation. A Rs. 5000 difference is well above the tolerance threshold.

---

## Test Case 11: Invalid Date Format

**Input Condition:**
```
order_id=ORD060, order_date=24/06/2026 (DD/MM/YYYY format — incorrect)
Expected format: YYYY-MM-DD
```

**Expected Output:**
- Record appears in `rejected_records.csv`
- `rejection_reason` contains "Invalid date format: '24/06/2026' (expected YYYY-MM-DD)"

**Reason:**
Consistent date formatting is critical for time-series analysis and reporting. Only YYYY-MM-DD is accepted.

---

## Test Case 12: Revenue Calculation (Recalculation Verification)

**Input Condition:**
```
order_id=ORD008, product_id=P008 (Wireless Mouse), quantity=2, unit_price=1200.00
```

**Expected Output:**
- `total_amount` in `cleaned_orders.csv` = 2400.00 (2 × 1200.00)
- The original `total_amount` from raw CSV (if any) is ignored and recalculated

**Reason:**
`total_amount` must always be recalculated as `quantity × unit_price` to ensure accuracy, regardless of any value in the raw file.

---

## Test Case 13: Rejection Reason Generation for Multiple Issues

**Input Condition:**
```
A record has both a missing customer name AND an invalid date format
```

**Expected Output:**
- Record appears in `rejected_records.csv`
- `rejection_reason` = "Missing customer name; Invalid date format: '...'"
- Both reasons are captured in one record (semicolon-separated)

**Reason:**
The pipeline collects ALL validation errors per record. Multi-issue records must report every problem so that fixing a single issue does not reveal another one in the next run.

---

## Test Case 14: Standardisation (Casing and Spacing — Cleaned, Not Rejected)

**Input Condition:**
```
order_id=ORD062, customer_name=priya patel (lowercase), city=DELHI (uppercase)
order_id=ORD061, customer_name="  Rahul   Sharma  " (extra spaces), city="  Mumbai  "
order_id=ORD064, customer_name=SNEHA SINGH (all caps)
```

**Expected Output:**
- All three records appear in `cleaned_orders.csv` (not rejected)
- `customer_name` corrected to Title Case: "Priya Patel", "Rahul Sharma", "Sneha Singh"
- `city` corrected to Title Case: "Delhi", "Mumbai", "Chennai"
- Extra spaces removed

**Reason:**
Casing and spacing issues are data quality imperfections that can be fixed programmatically. They do not make a record invalid — they are standardised during cleaning.
