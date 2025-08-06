import re
from datetime import datetime
from dateutil import parser

def extract_expiry_date(text):
    """
    Extract expiry date from text with priority for expiry-related terms.
    """
    if not text:
        return None
    
    # Look specifically for expiry date patterns with labels
    expiry_patterns = [
        r'(?:exp|expiry|expiration|best before|use by|bb)[:\s]*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})',
        r'(?:exp|expiry|expiration|best before|use by|bb)[:\s]*(\d{1,2}[\s]*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s]*\d{2,4})',
    ]
    
    # First try to find dates with explicit expiry labels
    for pattern in expiry_patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            for match in matches:
                try:
                    date = parser.parse(match, fuzzy=True)
                    return date
                except:
                    continue
    
    # If no explicit expiry date found, look for date patterns
    # Common date formats in product packaging
    date_patterns = [
        # DD.MM.YY or DD.MM.YYYY format (common in many countries)
        r'(\d{1,2}\.\d{1,2}\.\d{2,4})',
        # DD/MM/YY or DD/MM/YYYY format
        r'(\d{1,2}\/\d{1,2}\/\d{2,4})',
        # YYYY-MM-DD format (ISO)
        r'(\d{4}\-\d{1,2}\-\d{1,2})',
        # DD-MM-YY or DD-MM-YYYY format
        r'(\d{1,2}\-\d{1,2}\-\d{2,4})',
    ]
    
    all_dates = []
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                date = parser.parse(match, fuzzy=True)
                all_dates.append(date)
            except:
                continue
    
    if all_dates:
        # Sort dates and return the latest one (most likely to be expiry date)
        # This assumes expiry date is later than manufacturing date
        return max(all_dates)
    
    return None
