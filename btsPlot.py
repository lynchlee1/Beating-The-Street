import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import base64
from io import BytesIO
import numpy as np

# Functions for handling None and NaN values
def safe_min(values):
    non_none = [x for x in values if x is not None and not (isinstance(x, float) and np.isnan(x))]
    return min(non_none) if non_none else 0

def safe_max(values):
    non_none = [x for x in values if x is not None and not (isinstance(x, float) and np.isnan(x))]
    return max(non_none) if non_none else 0

# Assign None to outliers
def cutoff_dict(dict, cutoff_ratio = None, cutoff_value = None):
    mean = sum(dict.values()) / len(dict)
    stddev = (sum((x - mean) ** 2 for x in dict.values()) / len(dict)) ** 0.5
    max_stddev = (len(dict)-1) ** 0.5

    if cutoff_ratio is not None:
        cutoff = cutoff_ratio * max_stddev
    elif cutoff_value is not None:
        cutoff = cutoff_value

    new_dict = {}    
    for key in dict.keys():
        if (dict[key] - mean) / stddev > cutoff or (dict[key] - mean) / stddev < -cutoff:
            new_dict[key] = None
        else:
            new_dict[key] = dict[key]

    return new_dict

# Digit formatter for y-axis
def digit_formatter(x, pos):
    if abs(x) < 1_000:
        return f'{x:.1f}'
    elif 1_000 <= abs(x) < 1_000_000:
        return f'{x/1_000:.1f}K'
    elif 1_000_000 <= abs(x) < 1_000_000_000:
        return f'{x/1_000_000:.1f}M'
    elif 1_000_000_000 <= abs(x) < 1_000_000_000_000:
        return f'{x/1_000_000_000:.1f}B'
    elif 1_000_000_000_000 <= abs(x) < 1_000_000_000_000_000:
        return f'{x/1_000_000_000_000:.1f}T'

# Formatting function
def finance_format(number, format = None, round_digit = 2, amplifier = 1):
    if number is None:
        return None
    
    if number >= 0:
        lsign, rsign = '', ''
    else:
        lsign, rsign = '(', ')'

    if format == "%":
        rsign = "%" + rsign
        amplifier = 100
    elif format == "x":
        rsign = "x" + rsign

    abs_num = abs(number) * amplifier

    if abs_num >= 1_000_000_000_000:    return f"{lsign}{round(abs_num/1_000_000_000_000, round_digit)}T{rsign}"
    elif abs_num >= 1_000_000_000:      return f"{lsign}{round(abs_num/1_000_000_000, round_digit)}B{rsign}"
    elif abs_num >= 1_000_000:          return f"{lsign}{round(abs_num/1_000_000, round_digit)}M{rsign}"
    elif abs_num >= 1_000:              return f"{lsign}{round(abs_num/1_000, round_digit)}K{rsign}"
    else:                               return f"{lsign}{round(abs_num, round_digit)}{rsign}"

# General dual-axis plotting function
def plot_metrics(data, plot_config):
    # annual, quarterly, None
    timeframe = plot_config["timeframe"] if "timeframe" in plot_config else None
    
    # {"roe": {"label": "ROE", "color": "tab:red", "num_metric1": "netIncome", "den_metric1": "totalStockholdersEquity"}, ...}
    ax1_metrics = plot_config["ax1_metrics"] if "ax1_metrics" in plot_config else None
    ax2_metrics = plot_config["ax2_metrics"] if "ax2_metrics" in plot_config else None

    x_discrete = plot_config["x_discrete"] if "x_discrete" in plot_config else 1
    x_grid = plot_config["x_grid"] if "x_grid" in plot_config else True
    y_grid = plot_config["y_grid"] if "y_grid" in plot_config else False

    max_display1 = plot_config["max_display1"] if "max_display1" in plot_config else None
    min_display1 = plot_config["min_display1"] if "min_display1" in plot_config else None
    max_display2 = plot_config["max_display2"] if "max_display2" in plot_config else None
    min_display2 = plot_config["min_display2"] if "min_display2" in plot_config else None
    auto_scale = plot_config["auto_scale"] if "auto_scale" in plot_config else 0 # 0: no auto scale, 1: auto scale ax1 to ax2, 2: auto scale ax2 to ax1
    scale1 = plot_config["scale1"] if "scale1" in plot_config else 1
    scale2 = plot_config["scale2"] if "scale2" in plot_config else 1

    suppress_display = plot_config["suppress_display"] if "suppress_display" in plot_config else True
    marker = plot_config["marker"] if "marker" in plot_config else 'o'
    marker_size = plot_config["marker_size"] if "marker_size" in plot_config else 3
    line_width = plot_config["line_width"] if "line_width" in plot_config else 1.5

    min_margin = plot_config["min_margin"] if "min_margin" in plot_config else 1.5
    max_margin = plot_config["max_margin"] if "max_margin" in plot_config else 1.1

    metric_values = {}
    for metric in ax1_metrics.keys():
        metric_values[metric] = []
    if ax2_metrics:
        for metric in ax2_metrics.keys():
            metric_values[metric] = []

    if timeframe is not None: dates = sorted(data[list(ax1_metrics.keys())[0]][timeframe].keys())
    else: dates = sorted(data[list(ax1_metrics.keys())[0]].keys())
    
    for date in dates:
        if timeframe is not None:
            for metric in metric_values.keys():
                metric_values[metric].append(data[metric][timeframe].get(date, None))
        else:
            for metric in metric_values.keys():
                metric_values[metric].append(data[metric].get(date, None))

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx() if ax2_metrics else None

    ax1.grid(x_grid, axis='x') 
    ax1.grid(y_grid, axis='y')  
    if ax2:
        ax2.grid(x_grid, axis='x')  
        ax2.grid(y_grid, axis='y')

    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(digit_formatter))
    if ax2:
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(digit_formatter)) 
    
    # Add horizontal line at y = 0
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=0.5)  

    # example: {"revenue": {"label": "Revenue", "color": "tab:red"}}
    for metric, config in ax1_metrics.items():
        label = config["label"] if "label" in config else metric
        color = config["color"] if "color" in config else "tab:red"
        zorder = config["zorder"] if "zorder" in config else 1
        opacity = config["opacity"] if "opacity" in config else 1
        ax1.plot(dates, metric_values[metric], label=label, color=color, marker=marker, markersize=marker_size, zorder=zorder, alpha=opacity, linewidth=line_width)
    if ax2_metrics:
        for metric, config in ax2_metrics.items():
            label = config["label"] if "label" in config else metric
            color = config["color"] if "color" in config else "tab:red"
            zorder = config["zorder"] if "zorder" in config else 1
            opacity = config["opacity"] if "opacity" in config else 1
            ax2.plot(dates, metric_values[metric], label=label, color=color, marker=marker, markersize=marker_size, zorder=zorder, alpha=opacity, linewidth=line_width)

    ax1.tick_params(axis='x', rotation=30)
    ax1.set_xticks(dates[::x_discrete])
    if ax2:
        ax2.tick_params(axis='x', rotation=30)
        ax2.set_xticks(dates[::x_discrete])

    lines1, labels1 = ax1.get_legend_handles_labels()
    if ax2:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, 
                  bbox_to_anchor=(0, 0.92, 1, 0.2), loc='upper left', 
                  borderaxespad=0., ncol=4, frameon=False)
    else:
        ax1.legend(lines1, labels1,
                  bbox_to_anchor=(0, 0.92, 1, 0.2), loc='upper left',
                  borderaxespad=0., ncol=4, frameon=False)

    ax1_values = [metric_values[metric] for metric in ax1_metrics.keys()]
    y1min = min(0, min_margin * min(safe_min(vals) for vals in ax1_values))
    y1max = max_margin * max(safe_max(vals) for vals in ax1_values)        
    if y1min == 0 and y1max == 0: y1max = 1

    if ax2_metrics:
        ax2_values = [metric_values[metric] for metric in ax2_metrics.keys()]
        if min_display2 is not None:
            y2min = max(min_display2, min(0, min_margin * min(safe_min(vals) for vals in ax2_values)))
        else:
            y2min = min(0, min_margin * min(safe_min(vals) for vals in ax2_values))
        if max_display2 is not None:
            y2max = min(max_display2, max_margin * max(safe_max(vals) for vals in ax2_values))
        else:
            y2max = max_margin * max(safe_max(vals) for vals in ax2_values)
        if y2min == 0 and y2max == 0: y2max = 1

        y12min = min(y1min, y2min)
        y12max = max(y1max, y2max)

    # auto_scale is provided only when ax2 is provided
    if auto_scale == 1:
        max1 = max(safe_max(vals) for vals in ax1_values)
        max2 = max(safe_max(vals) for vals in ax2_values)
        if max1 != 0:
            scale1 = max2 / max1
        elif max1 == 0:
            scale1 = 1
    elif auto_scale == 2:
        max1 = max(safe_max(vals) for vals in ax1_values)
        max2 = max(safe_max(vals) for vals in ax2_values)
        if max2 != 0:
            scale2 = max1 / max2
        elif max2 == 0:
            scale2 = 1

    ax1.set_ylim(y1min / scale1, y1max / scale1)
    if ax2_metrics:
        ax1.set_ylim(y12min / scale1, y12max / scale1)
        ax2.set_ylim(y12min / scale2, y12max / scale2)

    if max_display1 is not None:
        ax1.set_ylim(y12min / scale1, max_display1 / scale1)
    if max_display2 is not None:
        ax2.set_ylim(y2min / scale2, max_display2 / scale2)
    if min_display1 is not None:
        ax1.set_ylim(min_display1 / scale1, y1max / scale1)
    if min_display2 is not None:
        ax2.set_ylim(min_display2 / scale2, y2max / scale2)


    fig.tight_layout()

    if not(suppress_display):
        plt.show()

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{img_base64}" style="max-width:100%;max-height:320px;width:auto;height:auto;display:block;margin:0 auto;"/>'

def plot_valuation_bands(data, plot_config):
    base_dict = plot_config["base_dict"]
    base_dict_dates = sorted(list(base_dict.keys()))
    market_cap_dates = sorted(list(data["market_cap"].keys()))

    amplifier = plot_config["amplifier"] if "amplifier" in plot_config else 1
    suppress_display = plot_config["suppress_display"] if "suppress_display" in plot_config else True
    x_discrete = plot_config["x_discrete"] if "x_discrete" in plot_config else 1

    base_data = []
    market_cap = []
    dates = []
    for date in market_cap_dates:
        dates.append(date)
        market_cap.append(data["market_cap"][date])
        if date > base_dict_dates[-1]:
            base_data.append(base_dict[base_dict_dates[-1]])
        else:
            for i in range(len(base_dict_dates)-1):
                if base_dict_dates[i] <= date < base_dict_dates[i+1]:
                    base_data.append(base_dict[base_dict_dates[i]])
                    break
    
    fig, ax = plt.subplots(figsize=(10, 5))

    upper_band = [np.nan] * (len(dates) - len(base_data)) + [income * amplifier * 18 for income in base_data]
    middle_line = [np.nan] * (len(dates) - len(base_data)) + [income * amplifier * 13 for income in base_data]
    lower_band = [np.nan] * (len(dates) - len(base_data)) + [income * amplifier * 8 for income in base_data]
    
    ax.fill_between(dates, upper_band, middle_line, alpha=0.3, color='orange')
    ax.fill_between(dates, middle_line, lower_band, alpha=0.3, color='orange')
    
    ax.plot(dates, middle_line, color='orange', linewidth=0.5)
    ax.plot(dates, market_cap, color='tab:red', linewidth=1.5, label='Market Cap')
    
    ax.grid(True, axis='x') 
    ax.grid(False, axis='y') 
    
    ax.tick_params(axis='x', rotation=30)
    ax.set_xticks(dates[::x_discrete])
    
    ax.set_ylim(0, 1.1 * max(safe_max(upper_band), safe_max(market_cap)))    
    ax.legend(bbox_to_anchor=(0, 0.92, 1, 0.2), loc='upper left', 
              borderaxespad=0., ncol=4, frameon=False)
    
    plt.tight_layout()
    
    if not suppress_display:
        plt.show()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{img_base64}" style="max-width:100%;max-height:320px;width:auto;height:auto;display:block;margin:0 auto;"/>'

def plot_box_whisker(data_list, labels=None, suppress_display=True, n_groups=None, m_elements=None, market_cap=None):
    if not data_list:
        return '<div class="placeholder">No data available for box plot</div>'
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    box_data = []
    positions = []
    
    for group in range(n_groups):
        group_data = []
        group_positions = []
        for i in range(m_elements):
            idx = group * m_elements + i
            value = data_list[idx]
            
            upper = 18 * value
            median = 13 * value
            lower = 8 * value
                
            box_range = (upper - lower) * 0.01 
            q1, q3 = median - box_range, median + box_range
            
            synthetic_data = []
            box_points = np.linspace(q1, q3, 20)
            synthetic_data.extend(box_points)

            synthetic_data.extend([lower, upper])
            group_data.append(synthetic_data)
            
            group_spacing = m_elements + 1
            position = group * group_spacing + i
            group_positions.append(position)
        
        box_data.extend(group_data)
        positions.extend(group_positions)
    
    if not box_data:
        return '<div class="placeholder">Invalid data format for box plot</div>'
    
    bp = ax.boxplot(box_data,
                    positions=positions,
                    patch_artist=True,
                    medianprops=dict(color="black", linewidth=0.8),
                    boxprops=dict(linewidth=0, facecolor='none'),
                    showfliers=False,
                    showcaps=True,
                    whis=[0, 100])
    
    for element in ['whiskers', 'caps']:
        plt.setp(bp[element], color='black', linewidth=0.8)

    if market_cap is not None:
        ax.axhline(y=market_cap, color='red', linewidth=1.2, linestyle='-', label='Current Market Cap')
        ax.legend(bbox_to_anchor=(0, 0.92, 1, 0.2), loc='upper left', 
                  borderaxespad=0., ncol=4, frameon=False)

    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.grid(False)    
    ax.set_ylim(0, 1.1 * max(market_cap, 18*max(data_list)))
    plt.tight_layout()
    if not suppress_display:
        plt.show()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{img_base64}" style="max-width:100%;max-height:320px;width:auto;height:auto;display:block;margin:0 auto;"/>'

# Extract image source from HTML
def extract_image_src(img_html):
    if 'src="' in img_html:
        start = img_html.find('src="') + 5
        end = img_html.find('"', start)
        return img_html[start:end]
    return img_html

def get_average_value(dict, length, amplifier=1):
    dates = sorted(dict.keys())[-length:]
    values = [dict[date] for date in dates]
    non_none_values = [v for v in values if v is not None]
    if not non_none_values:
        return None
    return sum(non_none_values) / len(non_none_values) * amplifier

def get_growth_value(dict, time_horizon, time_length):
    def safe_sum(list):
        non_none_values = [x for x in list if x is not None]
        if not non_none_values:
            return 0
        return sum(non_none_values)
    
    dates = sorted(dict.keys())
    sorted_dict_list = []
    for i in range(len(dates)):
        sorted_dict_list.append(dict[dates[i]])
    
    final_value = safe_sum(sorted_dict_list[-time_length:])
    if 4 * time_horizon > len(dates):
        return None
    else:
        initial_value = safe_sum(sorted_dict_list[-4*time_horizon:-4*time_horizon+time_length])
    
    if initial_value == 0:
        return None
    
    ratio = (final_value / initial_value) ** (1/(time_horizon - time_length/4)) - 1
    if not isinstance(ratio, complex):
        return ratio
    
    return None

def get_column(dict, label, mode="average", amplifier=1, format=None):
    if mode == "average":
        return [label,
                finance_format(get_average_value(dict, 12, amplifier=amplifier), format=format), 
                finance_format(get_average_value(dict, 20, amplifier=amplifier), format=format), 
                finance_format(get_average_value(dict, 40, amplifier=amplifier), format=format), 
                finance_format(get_average_value(dict, 52, amplifier=amplifier), format=format), 
                finance_format(get_average_value(dict, 80, amplifier=amplifier), format=format)
            ]
    elif mode == "growth":
        format = "%" if format is None else format
        return [label,
                finance_format(get_growth_value(dict, 3, 4), format=format), 
                finance_format(get_growth_value(dict, 5, 4), format=format), 
                finance_format(get_growth_value(dict, 10, 12), format=format), 
                finance_format(get_growth_value(dict, 13, 12), format=format), 
                finance_format(get_growth_value(dict, 20, 12), format=format)
            ]
    
    return None
