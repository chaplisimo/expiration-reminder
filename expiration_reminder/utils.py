# Function to check if a value is a float
def is_float(value):
    """
    Returns True if the value is a float, False otherwise.
    Handles both numeric and string inputs safely.
    """
    # Direct type check for numeric values
    if isinstance(value, float):
        return True
    
    # Try converting strings to float
    if isinstance(value, str):
        try:
            float(value)  # Attempt conversion
            return '.' in value or 'e' in value.lower()  # Ensure it's not an int-like string
        except ValueError:
            return False
    
    return False
