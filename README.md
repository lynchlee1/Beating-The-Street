# Financial Report Generation Tool

This project creates complete HTML financial report with only ticker input.

## Key Features

- **In-depth Financial Analysis**: Calculates a wide range of key financial metrics including Valuation, Operational Stability, Financial Stability, Capital Structure.
- **Long-Term Trend Analysis**: Computes 3, 5, 10, 13, 20 year averages for major financial indicators.

- **Dynamic Visualizations**: Generates interactive HTML with buttons to toggle between different trailing periods for visualizing financial metrics and trends.
- **Double Axis Graph Alignment**: Automatically aligns dual y-axes to ensure visual clarity when comparing metrics of different scales.


### Use

1.  Create a `config.py` file in the root directory.
2.  Add your API key to `config.py` as follows:
    ```python
    API_KEY = "YOUR_API_KEY"
    ```
3. Open the `main.py` file and modify the `test_cases` list to include the stock tickers you want to analyze.
4. The script will iterate through the tickers, fetch the data, perform analysis, and generate an HTML report for each valid ticker in the `reports/` directory.
