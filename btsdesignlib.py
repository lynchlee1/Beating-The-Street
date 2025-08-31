from utilitylib import safe_average, safe_frac, safe_sum_dict, safe_average_dict, digit_formatter

def create_row(configs, display_warning = False):
    label = configs.get("label")

    num1_dict = configs.get("num1_dict")
    num2_dict = configs.get("num2_dict")
    den1_dict = configs.get("den1_dict")
    den2_dict = configs.get("den2_dict")

    order = configs.get("order", (0, 1))
    amplifier = configs.get("amplifier", 1)

    unit = configs.get("unit")
    zero_on_none = configs.get("zero_on_none", False)
    g_row = configs.get("g_row", False)

    # must be fiscal dates : all same intended, but coded for safety.
    all_dates = set()
    if num1_dict: all_dates.update(num1_dict.keys())
    if num2_dict: all_dates.update(num2_dict.keys())
    if den1_dict: all_dates.update(den1_dict.keys())
    if den2_dict: all_dates.update(den2_dict.keys())
    days = sorted(list(all_dates), reverse=True)

    if num1_dict and display_warning:
        missing_dates = [d for d in days if d not in num1_dict]
        if missing_dates: print(f"Warning: {label} num1_dict missing dates: {missing_dates}")
    if num2_dict and display_warning:
        missing_dates = [d for d in days if d not in num2_dict]
        if missing_dates: print(f"Warning: {label} num2_dict missing dates: {missing_dates}") 
    if den1_dict and display_warning:
        missing_dates = [d for d in days if d not in den1_dict]
        if missing_dates: print(f"Warning: {label} den1_dict missing dates: {missing_dates}")    
    if den2_dict and display_warning:
        missing_dates = [d for d in days if d not in den2_dict]
        if missing_dates: print(f"Warning: {label} den2_dict missing dates: {missing_dates}")

    # Get 3Y, 5Y, 10Y, 13Y, 20Y averages
    averages = []
    for length in [12, 20, 40, 52, 80]:
        # Calculate average of 4Y fractions
        values = {}
        for i in range(0, length, 4):
            if (num1_dict and len(num1_dict) < length) or (num2_dict and len(num2_dict) < length) or (den1_dict and len(den1_dict) < length) or (den2_dict and len(den2_dict) < length):
                values[i//4] = None
            elif i + 4 <= length:
                num1 = safe_sum_dict(num1_dict, days[i:i+4]) if num1_dict else 1
                num2 = safe_sum_dict(num2_dict, days[i:i+4]) if num2_dict else 1
                den1 = safe_sum_dict(den1_dict, days[i:i+4]) if den1_dict else 1
                den2 = safe_sum_dict(den2_dict, days[i:i+4]) if den2_dict else 1
                amplifier_use = amplifier * ((1/4)**order[0])
                values[i//4] = safe_frac(num1, den1, num2, den2, amplifier=amplifier_use)
        averages.append(digit_formatter(safe_average(values, zero_on_none=zero_on_none), "", unit = unit))

    # Get 3/1Y, 5/1Y, 10/3Y, 13/3Y, 20/3Y growth rates
    growth_rates = []
    if g_row:
        for item in [[12, 4], [20, 4], [40, 12], [52, 12], [80, 12]]:
            data_length, trailing_length = item[0], item[1]
            if any((d and len(d) < data_length) for d in [num1_dict, num2_dict, den1_dict, den2_dict]):
                growth_rates.append("N/A")
                continue
            last_days = days[0:trailing_length]
            first_days = days[data_length - trailing_length:data_length]

            # Calculate sums for first and last periods
            last_num1 = safe_sum_dict(num1_dict, last_days) if num1_dict else 1
            last_num2 = safe_sum_dict(num2_dict, last_days) if num2_dict else 1
            last_den1 = safe_sum_dict(den1_dict, last_days) if den1_dict else 1
            last_den2 = safe_sum_dict(den2_dict, last_days) if den2_dict else 1
            last_value = safe_frac(last_num1, last_den1, last_num2, last_den2)

            first_num1 = safe_sum_dict(num1_dict, first_days) if num1_dict else 1
            first_num2 = safe_sum_dict(num2_dict, first_days) if num2_dict else 1
            first_den1 = safe_sum_dict(den1_dict, first_days) if den1_dict else 1
            first_den2 = safe_sum_dict(den2_dict, first_days) if den2_dict else 1
            first_value = safe_frac(first_num1, first_den1, first_num2, first_den2)

            try: growth_rate = (last_value / first_value) ** (4/(data_length - trailing_length)) - 1
            except: growth_rate = None
            growth_rates.append(digit_formatter(growth_rate, "", unit = "%"))
    else:
        growth_rates = ["N/A" for i in range(len(averages))]

    return averages, growth_rates

def create_table(configs, title = "", header = ["", "3Y", "5Y", "10Y", "13Y", "20Y"]):
    table = {"type": "table", "title": title, "columns": ["" for _ in range(len(header))], "rows": [header]}
    for config in configs:
        label = config.get("label")

        num1_dict = config.get("num1_dict")
        num2_dict = config.get("num2_dict")
        den1_dict = config.get("den1_dict")
        den2_dict = config.get("den2_dict")

        order = config.get("order", (0, 1))
        amplifier = config.get("amplifier", 1)

        unit = config.get("unit")
        zero_on_none = config.get("zero_on_none", False)
        g_row = config.get("g_row", False)

        row_config = {
            "label": label, 
            "order": order, 
            "amplifier": amplifier, 
            "zero_on_none": zero_on_none,
            "g_row": g_row
        }

        if num1_dict: row_config["num1_dict"] = num1_dict
        if num2_dict: row_config["num2_dict"] = num2_dict
        if den1_dict: row_config["den1_dict"] = den1_dict
        if den2_dict: row_config["den2_dict"] = den2_dict
        if unit: row_config["unit"] = unit
        averages, growth_rates = create_row(row_config)
        table["rows"].append([label] + averages)
        if g_row: table["rows"].append(["\tGrowth"] + growth_rates)

    return table
