import re

def validate_sku(sku: str) -> bool:
    """
    Validates a product SKU based on the following rules:
    - 3 uppercase Latin letters (category)
    - Hyphen '-'
    - 4 digits (year)
    - Hyphen '-'
    - 6 digits (unique number)
    Example: ELE-2026-004512
    """
    # Regex breakdown:
    # ^[A-Z]{3} : Starts with exactly 3 uppercase Latin letters
    # -         : Followed by a literal hyphen
    # \d{4}     : Followed by exactly 4 digits
    # -         : Followed by a literal hyphen
    # \d{6}$    : Ends with exactly 6 digits
    pattern = r"^[A-Z]{3}-\d{4}-\d{6}$"
    return bool(re.match(pattern, sku))

def run_tests():
    test_cases = [
        # Valid examples
        ("ELE-2026-004512", True),
        ("CLO-2023-123456", True),
        ("HOM-1999-000001", True),
        ("ABC-2000-999999", True),
        
        # Invalid examples
        ("el-2026-004512", False),   # Lowercase letters
        ("ELE-26-004512", False),    # Year only 2 digits
        ("ELE-2026-12345", False),   # Number only 5 digits
        ("ELE_2026_004512", False),  # Underscores instead of hyphens
        ("ELECTRONICS-2026-001", False), # Category too long, number too short
        ("ELE-2026-1234567", False), # Number too long
        ("123-2026-004512", False),  # Category is digits
        ("ELE-abcd-004512", False),  # Year is letters
        (" ELE-2026-004512", False), # Leading space
        ("ELE-2026-004512 ", False), # Trailing space
    ]

    print(f"{'SKU':<20} | {'Expected':<10} | {'Result':<10} | {'Status'}")
    print("-" * 55)

    passed = 0
    for sku, expected in test_cases:
        result = validate_sku(sku)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result == expected:
            passed += 1
        print(f"{sku:<20} | {str(expected):<10} | {str(result):<10} | {status}")

    print("-" * 55)
    print(f"Passed {passed}/{len(test_cases)} tests.")

if __name__ == "__main__":
    run_tests()
