import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import matplotlib.ticker as ticker

from utilitylib import safe_min, safe_max, safe_sum_dict, safe_frac, digit_formatter

from importlib import reload
import config
reload(config)
from config import TVBLACK, TVWHITE, TVRED, TVPINK, TVORANGE, TVBLUE, TVLIGHTBLUE, TVGREEN, TVDARKGREEN, TVGRAY

PLOT_MARGIN_HIGH = 1.1
PLOT_MARGIN_LOW = 1.25
MARGIN = 0.0001

# Dark UI theme for matplotlib.
def setup_dark_rc():
    plt.rcParams.update({
        # background colors
        "figure.facecolor": "none", # transparent canvas background
        "savefig.facecolor": "none", # transparent canvas background
        "axes.facecolor": TVBLACK, # plot background color
        "axes.edgecolor": TVBLACK, # plot background edge color
        # text colors
        "axes.labelcolor": TVWHITE,
        "axes.titlecolor": TVWHITE,
        "xtick.color": TVWHITE,
        "ytick.color": TVWHITE,
        # grid colors
        "grid.color": (1,1,1,0.12),
        "grid.linestyle": "--",
        "grid.linewidth": 0.7,
        "axes.grid": True,
        # font sizes
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        # other settings
        "figure.dpi": 150,
        "lines.linewidth": 2.0,
        "legend.frameon": False,
        "figure.figsize": (12,5),
        "figure.subplot.left": 0.07,
        "figure.subplot.right": 0.93,
        "figure.subplot.bottom": 0.15,
        "figure.subplot.top": 0.9
    })

# Tidy up and enable/disable spines.
def tidy_axes(ax, left=True, right = True, top = True, bottom=True):
    ax.spines["left"].set_color(TVGRAY)
    ax.spines["right"].set_color(TVGRAY)
    ax.spines["top"].set_color(TVGRAY)
    ax.spines["bottom"].set_color(TVGRAY)
    if not left:   ax.spines["left"].set_visible(False)
    if not right:  ax.spines["right"].set_visible(False)
    if not top:    ax.spines["top"].set_visible(False)
    if not bottom: ax.spines["bottom"].set_visible(False)
    ax.margins(x=0.01)

# Convert matplotlib figure to URI.
def fig_to_uri(fig, fmt="png"):
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, pad_inches=0.15, transparent=True)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return f"data:image/{fmt};base64,{b64}"

# Get Annualized trailing data for certain trailing length. 
# result[date] = (sum of num1 values * sum of num2 values) / (sum of den1 values * sum of den2 values)
def calc_trailing_data(config):
    dates = sorted(list(config.get("sum_dates")))
    trailing_length = config.get("trailing_length")

    num1_dict = config.get("num1_dict")
    num2_dict = config.get("num2_dict")
    den1_dict = config.get("den1_dict")
    den2_dict = config.get("den2_dict")

    zero_on_none = config.get("zero_on_none", False)

    # Order of (stock, flow): Multiplier is (1/len, 4/len)
    order = config.get("order", (0, 1))
    amplifier = config.get("amplifier", 1)
    amplifier = amplifier * ((1/trailing_length)**order[0]) * ((4/trailing_length)**order[1])

    remove_corrupt = config.get("remove_corrupt", True)
    remove_corrupt_threshold = config.get("remove_corrupt_threshold", 5.0)

    result = {}

    for i in range(trailing_length - 1):
        result[dates[i]] = None

    for i in range(trailing_length - 1, len(dates)):
        window_keys = [dates[j] for j in range(i-trailing_length+1, i+1)]
        if num1_dict: num1 = safe_sum_dict(num1_dict, window_keys, zero_on_none = zero_on_none)
        else: num1 = 1
        if num2_dict: num2 = safe_sum_dict(num2_dict, window_keys, zero_on_none = zero_on_none)
        else: num2 = 1
        if den1_dict: den1 = safe_sum_dict(den1_dict, window_keys, zero_on_none = zero_on_none)
        else: den1 = 1
        if den2_dict: den2 = safe_sum_dict(den2_dict, window_keys, zero_on_none = zero_on_none)
        else: den2 = 1
        result[dates[i]] = safe_frac(num1, den1, num2, den2, amplifier = amplifier)

    if remove_corrupt:
        values = [v for v in result.values() if v is not None and np.isfinite(v)]
        if len(values) > 3:
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            if iqr > 0:
                lower_bound = q1 - remove_corrupt_threshold * iqr
                upper_bound = q3 + remove_corrupt_threshold * iqr
                for date, value in result.items():
                    if value is not None and (value < lower_bound or value > upper_bound):
                        result[date] = None

    return result

# Plot box and whisker chart.
def plot_box_whisker(groups: dict, current_market_cap: float, y_grid_ticks: int = 6):
    setup_dark_rc()
    fig, ax = plt.subplots()

    group_labels = list(groups.keys())
    metric_labels = list(list(groups.values())[0].keys())
    n_groups = len(group_labels)
    n_metrics = len(metric_labels)
    
    x = np.arange(n_groups)
    total_width = 0.8
    metric_width = total_width / n_metrics
    
    all_plot_values = [current_market_cap]
    metric_colors = [TVGREEN, TVORANGE, TVPINK]

    for i, metric in enumerate(metric_labels):
        positions = x - total_width / 2 + i * metric_width + metric_width / 2
        values = [groups[g][metric] for g in group_labels]
        metric_color = metric_colors[i % len(metric_colors)]

        for pos, val in zip(positions, values):
            if val is None or np.isnan(val): continue

            whisker_min = 8 * val
            whisker_max = 18 * val
            median1 = 13 * val
            median2 = 13 * 2 / 3 * val
            all_plot_values.extend([whisker_min, whisker_max])

            # Whisker line
            ax.plot([pos, pos], [whisker_min, whisker_max], color=metric_color, linewidth=1.0, zorder=1)
            # Caps
            cap_width = metric_width * 0.4
            ax.plot([pos - cap_width, pos + cap_width], [whisker_min, whisker_min], color=metric_color, linewidth=1.0, zorder=1)
            ax.plot([pos - cap_width, pos + cap_width], [whisker_max, whisker_max], color=metric_color, linewidth=1.0, zorder=1)
            # Median lines
            ax.plot([pos - cap_width, pos + cap_width], [median1, median1], color=metric_color, linewidth=1.0, zorder=2)
            ax.plot([pos - cap_width, pos + cap_width], [median2, median2], color=metric_color, linestyle='--', linewidth=1.0, zorder=2)

    # Market cap line
    ax.axhline(current_market_cap, color=TVBLUE, linestyle='-', linewidth=1.5, label='Current Market Cap')

    # Set Y-axis limits
    ax.set_ylim(0, PLOT_MARGIN_HIGH * max(all_plot_values))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(digit_formatter))

    # X-axis ticks and labels
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels)
    ax.set_yticks(np.arange(0, PLOT_MARGIN_HIGH * PLOT_MARGIN_HIGH * max(all_plot_values), PLOT_MARGIN_HIGH * max(all_plot_values) / y_grid_ticks))

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color=TVBLUE, lw=2, label='Current Market Cap')]
    for i, metric in enumerate(metric_labels):
        legend_elements.append(Line2D([0], [0], color=metric_colors[i % len(metric_colors)], lw=2, label=metric))
    
    ax.legend(handles=legend_elements, bbox_to_anchor=(0, 1.04, 1, 0.1), loc='upper left', ncol=len(legend_elements), frameon=False)
    for text in ax.get_legend().get_texts():
        text.set_color(TVWHITE)

    tidy_axes(ax, right=False, top=False)
    return fig_to_uri(fig)

# Retrospective data collection.
def retro_get(dictionary, date):
    if date in dictionary: return dictionary.get(date)
    else:
        dict_dates = sorted(list(dictionary.keys()))
        if date < dict_dates[0]: return None
        for i in range(len(dict_dates) - 1):
            if dict_dates[i] <= date < dict_dates[i+1]:
                return dictionary.get(dict_dates[i])
        return None

# Plot metrics using dictionary as input.
def plot_metrics_dict(plot_config):
    def _safe_scale_min(n1, d1, n2, d2):
        if d1 * d2 != 0: return min(abs(n1 / d1), abs(n2 / d2))
        elif d1 == 0: return abs(n2 / d2)
        elif d2 == 0: return abs(n1 / d1)
        else: return 1

    def _safe_scale_max(n1, d1, n2, d2):
        if d1 * d2 != 0: return max(abs(n1 / d1), abs(n2 / d2))
        elif d1 == 0: return abs(n2 / d2)
        elif d2 == 0: return abs(n1 / d1)
        else: return 1

    setup_dark_rc()
    
    # x axis values
    dates = plot_config.get("axis_dates")
    # ax1_configs, ax2_configs have label, data, color
    ax1_configs = plot_config.get("ax1_configs", [])
    ax2_configs = plot_config.get("ax2_configs", [])

    # y axis ticks
    y_grid_ticks = plot_config.get("y_grid_ticks", 7)

    scale1 = plot_config.get("scale1", 1)
    scale2 = plot_config.get("scale2", 1)

    fig, ax1 = plt.subplots()
    if ax2_configs: ax2 = ax1.twinx()
    else: ax2 = None

    all_configs = ax1_configs + ax2_configs
    metric_values = {}
    for config in all_configs:
        label = config.get('label')
        data = config.get('data')
        metric_values[label] = [retro_get(data, d) for d in dates]

    # On/Off x, y grid
    x_grid = plot_config.get("x_grid", True)
    y_grid = plot_config.get("y_grid", True)
    ax1.grid(x_grid, axis='x') 
    ax1.grid(y_grid, axis='y')  
    if ax2:
        ax2.grid(x_grid, axis='x')  
        ax2.grid(y_grid, axis='y')

    # Set y axis formatter
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(digit_formatter))
    if ax2:
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(digit_formatter)) 
    
    # Plot ax1, ax2
    for _, config in enumerate(ax1_configs):
        label = config.get('label')
        if label and label in metric_values:
            ax1.plot(dates, metric_values[label], color=config.get('color'), label=label)
    if ax2_configs:
        for _, config in enumerate(ax2_configs):
            label = config.get('label')
            if label and label in metric_values:
                ax2.plot(dates, metric_values[label], color=config.get('color'), label=label)

    # Set x axis range
    ax1.set_xlim(dates[0], dates[-1])

    # Set x ticks and rotation
    ax1.tick_params(axis='x', rotation=30)
    x_discrete = plot_config.get("x_discrete", 4)
    ax1.set_xticks(dates[::x_discrete])
    if ax2:
        ax2.tick_params(axis='x', rotation=30)
        ax2.set_xticks(dates[::x_discrete])

    # Locate and design legend
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
        
    if ax1 and ax1.get_legend():
        for text in ax1.get_legend().get_texts():
            text.set_color(TVWHITE)
    if ax2 and ax2.get_legend():
        for text in ax2.get_legend().get_texts():
            text.set_color(TVWHITE)

    ax1_labels = [elem.get('label') for elem in ax1_configs]
    ax1_values = [metric_values[label] for label in ax1_labels if label in metric_values]
    y1min = PLOT_MARGIN_LOW * min(0, min(safe_min(vals) for vals in ax1_values))
    y1max = PLOT_MARGIN_HIGH * max(0, max(safe_max(vals) for vals in ax1_values))
    if y1min == y1max: y1min, y1max = min(0, y1min), max(1, y1max)

    if ax2_configs:
        ax2_labels = [elem.get('label') for elem in ax2_configs]
        ax2_values = [metric_values[label] for label in ax2_labels if label in metric_values]
        y2min = PLOT_MARGIN_LOW * min(0, min(safe_min(vals) for vals in ax2_values))
        y2max = PLOT_MARGIN_HIGH * max(0, max(safe_max(vals) for vals in ax2_values))
        if y2min == y2max: y2min, y2max = min(0, y2min), max(1, y2max)

    if y1min < 0 and y1max > 0:
        step = (y1max - y1min) / y_grid_ticks
        i = int(round(-y1min / step))
        zero_point = y1min + step * i
        if i != 0 and i != y_grid_ticks:
            if zero_point > 0: y1min = - y1max * i / (y_grid_ticks - i)
            elif zero_point < 0: y1max = - y1min * (y_grid_ticks - i) / i
        elif i == 0:
            y1min = - y1max / (y_grid_ticks - 1)
        elif i == y_grid_ticks:
            y1max = - y1min / (y_grid_ticks - 1)
    ax1.set_ylim(y1min / scale1, y1max / scale1)
    ax1.set_yticks(np.arange(y1min / scale1, MARGIN + y1max / scale1, (y1max - y1min) / scale1 / y_grid_ticks))

    if ax2_configs:
        if y1min == 0 and y2min == 0:
            None
        elif y1min == 0 and y2min < 0:
            # ax2 will have 0 at i = 1
            y1min = - y1max / (y_grid_ticks - 1)
            if - (y_grid_ticks - 1) * y2min >= y2max:
                # Move y2max
                y2max = - (y_grid_ticks - 1) * y2min
            elif - y2max / (y_grid_ticks - 1) <= y2min :
                # Move y2min
                y2min = - y2max / (y_grid_ticks - 1)
            else:
                print("Unexpected Error: Invalid axis setting")
        elif y1min < 0 and y2min == 0:
            # ax1 will have 0 at i = 1
            y2min = - y2max / (y_grid_ticks - 1)
            if - (y_grid_ticks - 1) * y1min >= y1max:
                # Move y1max
                y1max = - (y_grid_ticks - 1) * y1min
            elif - y1max / (y_grid_ticks - 1) <= y1min :
                # Move y1min
                y1min = - y1max / (y_grid_ticks - 1)
            else:
                print("Unexpected Error: Invalid axis setting")
        elif y1min < 0 and y2min < 0:
            step = (y2max - y2min) / y_grid_ticks
            i = int(round(-y2min / step))
            zero_point = y2min + step * i
            if i != 0:
                if zero_point > 0: y2min = - y2max * i / (y_grid_ticks - i)
                elif zero_point < 0: y2max = -y2min * (y_grid_ticks - i) / i
            elif i == 0:
                y2min = - y2max / (y_grid_ticks - 1)  
            elif i == y_grid_ticks:
                y2max = - y2min / (y_grid_ticks - 1)
        else:
            print("Error: Min/Max values are not properly set.")

        y12min, y12max = min(y1min, y2min), max(y1max, y2max)
        scale1, scale2 = scale1 * _safe_scale_min(y12max, y1max, y12min, y1min), scale2 * _safe_scale_min(y12max, y2max, y12min, y2min)

        ax1.set_ylim(y12min / scale1, y12max / scale1)
        ax2.set_ylim(y12min / scale2, y12max / scale2)
        
        ax1.set_yticks(np.arange(y12min / scale1, MARGIN + y12max / scale1, (y12max - y12min) / scale1 / y_grid_ticks))
        ax2.set_yticks(np.arange(y12min / scale2, MARGIN + y12max / scale2, (y12max - y12min) / scale2 / y_grid_ticks))

    if ax2_configs:
        tidy_axes(ax1, right=False, top=False)
        tidy_axes(ax2, left=False, top=False)
    else:
        tidy_axes(ax1, right=False, top=False)

    return fig_to_uri(fig)

# Iterate plot_metrics_dict for each trailing length.
def plot_trailing_data(main_config):
    # x axis values
    sum_dates = main_config.get("sum_dates")
    axis_dates = main_config.get("axis_dates")
    if not axis_dates: axis_dates = sum_dates

    # Each config in ax1_configs, ax2_configs has...
        # Must-pass : label & least one of num1_dict, num2_dict, den1_dict, den2_dict & color
        # Optional : zero_on_none(default False) & order(default (0, 1)) & amplifier(default 1)
    ax1_configs = main_config.get("ax1_configs", [])
    ax2_configs = main_config.get("ax2_configs", [])

    x_discrete = main_config.get("x_discrete", 4)
    x_grid = main_config.get("x_grid", True)
    y_grid = main_config.get("y_grid", True)
    y_grid_ticks = main_config.get("y_grid_ticks", 7)
    scale1 = main_config.get("scale1", 1)
    scale2 = main_config.get("scale2", 1)

    trailing_periods = {"1Q": 1, "4Q": 4, "12Q": 12}

    ax1_plot_datas = {}    
    for config in ax1_configs:
        label = config.get("label")
        ax1_plot_datas[label] = {}
        base_calc_config = {
            "sum_dates": sum_dates,
            "num1_dict": config.get("num1_dict"),
            "num2_dict": config.get("num2_dict"),
            "den1_dict": config.get("den1_dict"),
            "den2_dict": config.get("den2_dict"),
            "zero_on_none": config.get("zero_on_none", False),
            "order": config.get("order", (0, 1)),
            "amplifier": config.get("amplifier", 1),
            "remove_corrupt": config.get("remove_corrupt", True),
            "remove_corrupt_threshold": config.get("remove_corrupt_threshold", 5.0),
        }
        for period_label, length in trailing_periods.items():
            period_config = base_calc_config.copy()
            if config.get("disable_trailing", False):
                period_config["trailing_length"] = 1
            else:
                period_config["trailing_length"] = length
            ax1_plot_datas[label][period_label] = calc_trailing_data(period_config)
    
    ax2_plot_datas = {}
    for config in ax2_configs:
        label = config.get("label")
        ax2_plot_datas[label] = {}
        base_calc_config = {
            "sum_dates": sum_dates,
            "num1_dict": config.get("num1_dict"),
            "num2_dict": config.get("num2_dict"),
            "den1_dict": config.get("den1_dict"),
            "den2_dict": config.get("den2_dict"),
            "zero_on_none": config.get("zero_on_none", False),
            "order": config.get("order", (0, 1)),
            "amplifier": config.get("amplifier", 1),
            "remove_corrupt": config.get("remove_corrupt", True),
            "remove_corrupt_threshold": config.get("remove_corrupt_threshold", 5.0),
        }
        for period_label, length in trailing_periods.items():
            period_config = base_calc_config.copy()
            if config.get("disable_trailing", False):
                period_config["trailing_length"] = 1
            else:
                period_config["trailing_length"] = length
            ax2_plot_datas[label][period_label] = calc_trailing_data(period_config)
    
    plots = {}
    for period_label in trailing_periods.keys():
        plot_config = {
            "axis_dates": axis_dates,
            "ax1_configs": [{"label": label,
                            "data": ax1_plot_datas[label][period_label],
                            "color": ax1_configs[i].get("color")} for i, label in enumerate(ax1_plot_datas)],
            "ax2_configs": [{"label": label,
                            "data": ax2_plot_datas[label][period_label], 
                            "color": ax2_configs[i].get("color")} for i, label in enumerate(ax2_plot_datas)],
            "x_discrete": x_discrete,
            "x_grid": x_grid,
            "y_grid": y_grid,
            "y_grid_ticks": y_grid_ticks,
            "scale1": scale1,
            "scale2": scale2,
        }
        plots[period_label] = plot_metrics_dict(plot_config)
    
    return plots

# Plot valuation bands.
def plot_bands(plot_config):
    line_dict = plot_config.get("line_dict", {})
    line_dates = sorted(list(line_dict.keys()))
    area_dict = plot_config.get("area_dict", {})

    upper_band, middle_line, lower_band, line_data = [], [], [], []
    y_max = 0
    for date in line_dates:
        val = area_dict[date]
        upper_band.append(18 * val if val is not None else np.nan)
        middle_line.append(13 * val if val is not None else np.nan)
        lower_band.append(8 * val if val is not None else np.nan)
        line_data.append(line_dict[date])
        band_max = 18*val if val is not None else 0
        y_max = max(y_max, safe_max([line_dict[date], band_max]))
    y_max = PLOT_MARGIN_HIGH * y_max

    x_discrete = plot_config.get("x_discrete", 180)
    y_grid_ticks = plot_config.get("y_grid_ticks", 6)
    
    fig, ax = plt.subplots()
    ax.fill_between(line_dates, upper_band, lower_band, alpha=0.3, color=TVBLUE)
    ax.plot(line_dates, middle_line, color=TVBLUE, linewidth=0.5, alpha=0.3)
    ax.plot(line_dates, line_data, color=TVBLUE, linewidth=1.5, label='Market Cap')
    
    ax.tick_params(axis='x', rotation=30)
    ax.set_xticks(line_dates[::x_discrete])
    ax.set_ylim(0, y_max)
    ax.set_yticks(np.arange(0, 1.01 * y_max, y_max / y_grid_ticks))
  
    ax.legend(bbox_to_anchor=(0, 1.04, 1, 0.1), loc='upper left', 
              ncol=4, frameon=False)

    for text in ax.get_legend().get_texts():
        text.set_color(TVWHITE)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(digit_formatter))
    tidy_axes(ax, right=False, top=False)
    
    return fig_to_uri(fig)

# Iterate plot_bands for each trailing length.
def plot_trailing_bands(plot_config):
    setup_dark_rc()

    line_dict = plot_config.get("line_dict", {})
    line_dates = sorted(list(line_dict.keys()))
    area_dict = plot_config.get("area_dict", {})
    area_dates = sorted(list(area_dict.keys()))
    
    order = plot_config.get("order", (0, 1))
    amplifier = plot_config.get("amplifier", 1)
    x_discrete = plot_config.get("x_discrete", 180)
    y_grid_ticks = plot_config.get("y_grid_ticks", 6)
    
    area_config = {
        "sum_dates": area_dates,
        "num1_dict": area_dict,
        "zero_on_none": False,
        "order": order,
        "amplifier": amplifier,
    }
    area_datas = {}
    trailing_periods = {"1Q": 1, "4Q": 4, "12Q": 12}
    for period in trailing_periods:
        config = area_config.copy()
        config["trailing_length"] = trailing_periods[period]
        area_datas[period] = calc_trailing_data(config)
    
    line_data_dict = {}
    area_data_dict = {"1Q": {}, "4Q": {}, "12Q": {}}
    for date in line_dates:
        line_data_dict[date] = line_dict[date]
        area_data_dict["1Q"][date] = retro_get(area_datas["1Q"], date)
        area_data_dict["4Q"][date] = retro_get(area_datas["4Q"], date)
        area_data_dict["12Q"][date] = retro_get(area_datas["12Q"], date)

    plots = {}
    for period in trailing_periods:
        config = {
            "line_dict": line_data_dict,
            "area_dict": area_data_dict[period],
            "x_discrete": x_discrete,
            "y_grid_ticks": y_grid_ticks
        }
        plots[period] = plot_bands(config)
    return plots
