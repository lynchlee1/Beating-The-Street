# Minimum of None-removed list/dict. If all values are None, return None.
def safe_min(values):
    if isinstance(values, dict):
        values = list(values.values())
    non_none = [x for x in values if x is not None]
    return min(non_none) if non_none else None

# Maximum of None-removed list/dict. If all values are None, return None.
def safe_max(values):
    if isinstance(values, dict):
        values = list(values.values())
    non_none = [x for x in values if x is not None]
    return max(non_none) if non_none else None

# zero_on_none = False : Sum of None-removed list/dict. If all values are None, return None.
# zero_on_none = True  : Sum of list/dict with None considered as 0. If all values are None, return None.
def safe_sum(values, zero_on_none=False):
    if isinstance(values, dict):
        values = list(values.values())
    if zero_on_none: non_none = [0 if x is None else x for x in values]
    else: non_none = [x for x in values if x is not None]
    return sum(non_none) if non_none else None

# zero_on_none = False : Average of None-removed list/dict. If all values are None, return None.
# zero_on_none = True  : Average of list/dict with None considered as 0. If all values are None, return None.
def safe_average(values, zero_on_none=False):
    if isinstance(values, dict):
        values = list(values.values())
    if zero_on_none: non_none = [0 if x is None else x for x in values]
    else: non_none = [x for x in values if x is not None]
    return sum(non_none)/len(non_none) if non_none else None

# Sum of sum_dict for key in sum_keys. Use when some of sum_keys may not be in dict.
# zero_on_none = False : None breaks the sum and returns None.
# zero_on_none = True  : None considered as 0.
def safe_sum_dict(sum_dict, sum_keys, zero_on_none=False):
    sum = 0
    if not sum_dict: return None
    for key in sum_keys:
        value = sum_dict.get(key)
        if isinstance(value, (int, float)): sum += value
        elif value is None and zero_on_none: sum += 0
        else: return None
    return sum

# Average of sum_dict for key in sum_keys. Use when some of sum_keys may not be in dict.
# zero_on_none = False : None excluded for average calculation.
# zero_on_none = True  : None considered as 0.
def safe_average_dict(sum_dict, sum_keys, zero_on_none=False):
    sum, len = 0, 0
    if not sum_dict: return None
    for key in sum_keys:
        value = sum_dict.get(key)
        if isinstance(value, (int, float)): 
            sum += value
            len += 1
        elif value is None and zero_on_none: 
            sum += 0
            len += 1
        elif value is None and not zero_on_none:
            sum += 0
        else:
            return None
    return sum/len if len > 0 else None

# Calculate amplifier * (n1 * n2) / (d1 * d2). If fraction is invalid, return None.
def safe_frac(n1, d1, n2, d2, amplifier=1):
    try: return amplifier * (n1 * n2) / (d1 * d2)
    except: return None

# Change float x to a financial format string.
def digit_formatter(x, pos, unit=None):
    if not isinstance(x, (int, float)) or x is None: return "N/A"
    
    if unit == "%": return f'{x*100:.2f}%'

    # Consider negative values
    left_symbol, right_symbol = "", ""
    if -0.005 <= x < 0.005: return "0"
    if x < 0: left_symbol, right_symbol, x = "(", ")", -x

    # Financial unit conversion
    if x < 1_000: return f'{left_symbol}{x:.2f}{right_symbol}'
    elif 1_000 <= x < 1_000_000: return f'{left_symbol}{x/1_000:.1f}K{right_symbol}'
    elif 1_000_000 <= x < 1_000_000_000: return f'{left_symbol}{x/1_000_000:.1f}M{right_symbol}'
    elif 1_000_000_000 <= x < 1_000_000_000_000: return f'{left_symbol}{x/1_000_000_000:.1f}B{right_symbol}'
    elif 1_000_000_000_000 <= x < 1_000_000_000_000_000: return f'{left_symbol}{x/1_000_000_000_000:.1f}T{right_symbol}'
    else: return "N/A"

# Change financial format string x to a float.
def inv_digit_formatter(x):
    if isinstance(x, (int, float)): return x

    # Consider negative values
    if x[-1] == ")":
        x = "-" + x[1:-1]

    # Financial unit conversion
    if x[-1] == "%": x = float(x[:-1]) * 0.01
    elif x[-1] == "K": x = float(x[:-1]) * 1_000
    elif x[-1] == "M": x = float(x[:-1]) * 1_000_000
    elif x[-1] == "B": x = float(x[:-1]) * 1_000_000_000
    elif x[-1] == "T": x = float(x[:-1]) * 1_000_000_000_000
    else:
        try: x = float(x)
        except: x = None
    return x
