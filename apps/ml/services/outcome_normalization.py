def normalize_case_outcome(disposition: str) -> str:
    """
    Normalizes a raw case disposition string into standard categories.
    E.g., "Dismissed with prejudice" -> "DISMISSED"
    """
    if not disposition:
        return "UNKNOWN"
        
    disp_lower = disposition.lower()
    if 'dismiss' in disp_lower:
        return "DISMISSED"
    elif 'settle' in disp_lower or 'compromise' in disp_lower:
        return "SETTLED"
    elif 'allow' in disp_lower or 'decree' in disp_lower or 'judgment for plaintiff' in disp_lower:
        return "ALLOWED"
    elif 'convict' in disp_lower:
        return "CONVICTED"
    elif 'acquit' in disp_lower:
        return "ACQUITTED"
    elif 'transfer' in disp_lower:
        return "TRANSFERRED"
    elif 'withdraw' in disp_lower:
        return "WITHDRAWN"
    elif 'pending' in disp_lower or 'open' in disp_lower:
        return "PENDING"
    else:
        return "OTHER"
