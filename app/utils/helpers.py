"""
Utility functions and helpers.
"""

import re
from datetime import datetime
from typing import Optional


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """
    Normalize date string to DD/MM/YYYY format.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Normalized date string or None
    """
    if not date_str:
        return None
    
    # Common date patterns
    patterns = [
        (r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1"),  # YYYY-MM-DD
        (r"(\d{2})/(\d{2})/(\d{4})", r"\1/\2/\3"),  # DD/MM/YYYY (already correct)
        (r"(\d{2})-(\d{2})-(\d{4})", r"\1/\2/\3"),  # DD-MM-YYYY
        (r"(\d{1,2})\s+(\w+)\s+(\d{4})", None),      # 1 Jan 2024 (needs special handling)
    ]
    
    for pattern, replacement in patterns:
        if replacement and re.match(pattern, date_str.strip()):
            return re.sub(pattern, replacement, date_str.strip())
    
    # Handle month names
    months = {
        "jan": "01", "january": "01",
        "feb": "02", "february": "02",
        "mar": "03", "march": "03",
        "apr": "04", "april": "04",
        "may": "05",
        "jun": "06", "june": "06",
        "jul": "07", "july": "07",
        "aug": "08", "august": "08",
        "sep": "09", "september": "09",
        "oct": "10", "october": "10",
        "nov": "11", "november": "11",
        "dec": "12", "december": "12",
    }
    
    match = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_str.strip(), re.IGNORECASE)
    if match:
        day, month_name, year = match.groups()
        month = months.get(month_name.lower()[:3])
        if month:
            return f"{day.zfill(2)}/{month}/{year}"
    
    return date_str


def clean_passport_number(passport: Optional[str]) -> Optional[str]:
    """
    Clean and normalize passport number.
    
    Args:
        passport: Raw passport number string
        
    Returns:
        Cleaned passport number
    """
    if not passport:
        return None
    
    # Remove spaces and normalize to uppercase
    cleaned = re.sub(r"\s+", "", passport.upper())
    return cleaned if cleaned else None


def clean_uid_number(uid: Optional[str]) -> Optional[str]:
    """
    Clean and normalize UID number.
    
    Args:
        uid: Raw UID number string
        
    Returns:
        Cleaned UID number (digits only)
    """
    if not uid:
        return None
    
    # Extract digits only
    cleaned = re.sub(r"\D", "", uid)
    return cleaned if cleaned else None


def validate_email(email: Optional[str]) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email format
    """
    if not email:
        return False
    
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def truncate_string(text: str, max_length: int = 100) -> str:
    """
    Truncate string to maximum length with ellipsis.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
