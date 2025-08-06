
# Adds new metric to data
def append_metrics(data, metric_config):
    label = metric_config["label"]

    numerator1 = metric_config["num1"] if "num1" in metric_config else None
    numerator2 = metric_config["num2"] if "num2" in metric_config else None
    denominator1 = metric_config["den1"] if "den1" in metric_config else None
    denominator2 = metric_config["den2"] if "den2" in metric_config else None
    amplifier = metric_config["amplifier"] if "amplifier" in metric_config else 1

    data[label] = {"quarterly": {}}
    for date in data["revenue"]["quarterly"].keys():
        try:
            num1 = data[numerator1]["quarterly"][date] if numerator1 is not None else 1
            num2 = data[numerator2]["quarterly"][date] if numerator2 is not None else 1
            den1 = data[denominator1]["quarterly"][date] if denominator1 is not None else 1
            den2 = data[denominator2]["quarterly"][date] if denominator2 is not None else 1
            data[label]["quarterly"][date] = (num1 * num2) / (den1 * den2) * amplifier
        except:
            data[label]["quarterly"][date] = None

    return None

# Appends per-ttm metric to data
def append_per_ttm(data, key, trailing_period):
    data[key] = {}
    quarterly_dates = sorted(list(data["netIncome"]["quarterly"].keys()))
    market_cap_dates = sorted(list(data["market_cap"].keys()))

    for date in market_cap_dates:
        if date < quarterly_dates[trailing_period-1]:
            data[key][date] = None
            continue
        fiscal_quarter = None
        for i in range(len(quarterly_dates)-1):
            if quarterly_dates[i] <= date < quarterly_dates[i+1]:
                fiscal_quarter = i
                break        
        if fiscal_quarter is None and date >= quarterly_dates[-1]:
            fiscal_quarter = len(quarterly_dates) - 1

        if fiscal_quarter is not None:
            ttm_sum = sum(data["netIncome"]["quarterly"][quarterly_dates[j]] for j in range(fiscal_quarter-trailing_period+1, fiscal_quarter+1))
            average_ttm = ttm_sum / (trailing_period/4)
            if average_ttm > 0:
                data[key][date] = data["market_cap"][date] / average_ttm
            else:
                data[key][date] = None

    return None

# Appends price-based metric to data
def append_metrics_price(data, metric_config):
    label = metric_config["label"] if "label" in metric_config else None
    num1 = metric_config["num1"] if "num1" in metric_config else None
    num2 = metric_config["num2"] if "num2" in metric_config else None
    den1 = metric_config["den1"] if "den1" in metric_config else None
    den2 = metric_config["den2"] if "den2" in metric_config else None
    market_cap_pos = metric_config["market_cap_pos"] if "market_cap_pos" in metric_config else "den"

    amplifier = metric_config["amplifier"] if "amplifier" in metric_config else 1
    
    data[label] = {"quarterly": {}}
    quarterly_dates = sorted(list(data[num1]["quarterly"].keys()))

    market_cap_dates_list = []
    for date in sorted(list(data["market_cap"].keys())):
        market_cap_dates_list.append(date)

    for date in quarterly_dates:
        market_cap_value = 0
        for i in range(len(market_cap_dates_list)):
            if market_cap_dates_list[i] <= date < market_cap_dates_list[i+1]:
                market_cap_value = data["market_cap"][market_cap_dates_list[i]]
                break
        if market_cap_value == 0:
            data[label]["quarterly"][date] = None
            continue
        
        if market_cap_pos == "den":
            num1_value = data[num1]["quarterly"][date] if num1 is not None else 1
            num2_value = data[num2]["quarterly"][date] if num2 is not None else 1
            den1_value = data[den1]["quarterly"][date] if den1 is not None else 1
            den2_value = data[den2]["quarterly"][date] if den2 is not None else 1
            data[label]["quarterly"][date] = (num1_value * num2_value) / (den1_value * den2_value) * amplifier / market_cap_value

        elif market_cap_pos == "num":
            num1_value = data[num1]["quarterly"][date] if num1 is not None else 1
            num2_value = data[num2]["quarterly"][date] if num2 is not None else 1
            den1_value = data[den1]["quarterly"][date] if den1 is not None else 1
            den2_value = data[den2]["quarterly"][date] if den2 is not None else 1
            data[label]["quarterly"][date] = (num1_value * num2_value) / (den1_value * den2_value) * amplifier * market_cap_value

    return None

# Appends trailing metric to trailing_dict
def append_trailing_value(data, trailing_dict, metric_config):
    num_metric1 = metric_config["num1"] if "num1" in metric_config else None
    num_metric2 = metric_config["num2"] if "num2" in metric_config else None
    den_metric1 = metric_config["den1"] if "den1" in metric_config else None
    den_metric2 = metric_config["den2"] if "den2" in metric_config else None

    new_metric = metric_config["label"]
    trailing_period = metric_config["trailing_period"]
    amplifier = metric_config["amplifier"] if "amplifier" in metric_config else 4/trailing_period

    trailing_dict[new_metric] = {}
    quarterly_dates = sorted(list(data[num_metric1]["quarterly"].keys()))
    for i in range(trailing_period - 1, len(quarterly_dates)):
        current_date = quarterly_dates[i]
        ttm_sum1 = sum(data[num_metric1]["quarterly"][quarterly_dates[j]] for j in range(i-trailing_period+1, i+1)) if num_metric1 is not None else 1
        ttm_sum2 = sum(data[num_metric2]["quarterly"][quarterly_dates[j]] for j in range(i-trailing_period+1, i+1)) if num_metric2 is not None else 1
        ttm_sum3 = sum(data[den_metric1]["quarterly"][quarterly_dates[j]] for j in range(i-trailing_period+1, i+1)) if den_metric1 is not None else 1
        ttm_sum4 = sum(data[den_metric2]["quarterly"][quarterly_dates[j]] for j in range(i-trailing_period+1, i+1)) if den_metric2 is not None else 1
        trailing_dict[new_metric][current_date] = (ttm_sum1 * ttm_sum2) / (ttm_sum3 * ttm_sum4) * amplifier
    
    return None
