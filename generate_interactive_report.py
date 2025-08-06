def generate_interactive_report(ticker, plot_configs, table_data, table_column_labels=None):
    # Extract images and subbutton labels from plot_configs
    images = plot_configs["images"]
    subbutton_labels = plot_configs["subbutton_labels"]
    
    # Get analysis types from table_data keys
    analysis_types = list(table_data.keys())
    
    # Get subbuttons from subbutton_labels values
    subbuttons = list(subbutton_labels.values())

    # Use table_column_labels if provided, otherwise use subbutton labels
    if table_column_labels is None:
        table_column_labels = subbuttons
    
    # Generate analysis type buttons HTML
    analysis_buttons_html = ""
    for i, analysis_type in enumerate(analysis_types):
        active_class = " active" if i == 0 else ""
        analysis_buttons_html += f'<button class="analysis-button{active_class}" onclick="showAnalysis(\'{analysis_type}\')">{analysis_type}</button>'
    
    # Generate subbutton buttons HTML
    subbutton_buttons_html = ""
    for i, subbutton in enumerate(subbuttons):
        active_class = " active" if i == 0 else ""
        subbutton_buttons_html += f'<button class="subbutton-button{active_class}" onclick="showSubbutton(\'{subbutton}\')">{subbutton}</button>'
    
    # Generate images HTML
    images_html = ""
    for analysis_type in analysis_types:
        for subbutton in subbuttons:
            key = f"{analysis_type}_{subbutton}"
            hidden_class = "" if (analysis_type == analysis_types[0] and subbutton == subbuttons[0]) else " hidden"
            if key in images:
                images_html += f'<img id="{key}-img" class="chart-img{hidden_class}" src="{images[key]}" alt="{analysis_type} - {subbutton}">'
            else:
                print(f"Warning: Missing image for {subbutton}")
                images_html += f'<img id="{key}-img" class="chart-img{hidden_class}" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBhdmFpbGFibGU8L3RleHQ+PC9zdmc+" alt="{analysis_type} - {subbutton}">'
    # Convert table_data to JSON for JavaScript
    import json
    table_data_json = json.dumps(table_data)
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{ticker}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 30px;
            background-color: #ffffff;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
        }}
        .header {{
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 2em;
            color: #333;
            margin: 0;
        }}
        .analysis-container {{
            display: flex;
            justify-content: flex-start;
            gap: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}
        .analysis-button {{
            padding: 8px 20px;
            font-size: 14px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f0f0f0;
            color: #333;
            min-width: 120px;
        }}
        .analysis-button:hover {{
            background: #e0e0e0;
            transform: translateY(-2px);
        }}
        .analysis-button.active {{
            background: #007bff;
            color: white;
        }}
        .subbutton-container {{
            display: flex;
            justify-content: flex-start;
            gap: 8px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}
        .subbutton-button {{
            padding: 6px 14px;
            font-size: 13px;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f0f0f0;
            color: #333;
        }}
        .subbutton-button:hover {{
            background: #e0e0e0;
            transform: translateY(-2px);
        }}
        .subbutton-button.active {{
            background: #007bff;
            color: white;
        }}
        .main-content {{
            display: flex;
            gap: 8px;
            align-items: flex-start;
            width: 100%;
        }}
        .chart-container {{
            text-align: left;
            min-height: 400px;
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
            background: #ffffff;
            padding: 0px;
            flex: 0 0 52%;
        }}
        .chart-img {{
            max-width: 100%;
            max-height: 480px;
        }}
        .tables-container {{
            display: flex;
            flex-direction: column;
            gap: 0px;
            flex: 0 0 48%;
            margin-top: 23px;
        }}
        .table-box {{
            background: white;
            padding: 8px;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        /* data table styling : width, height padding */
        .data-table th, .data-table td {{
            padding: 8px 10px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        .data-table th:first-child, .data-table td:first-child {{
            width: 32%;
            text-align: right;
        }}
        .data-table th:not(:first-child), .data-table td:not(:first-child) {{
            width: 13%;
            text-align: center;
        }}
        .data-table th {{
            background: #f8f9fa;
            font-weight: bold;
            color: #555;
        }}
        .data-table td {{
            color: #333;
        }}
        .hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{ticker}</h1>
        </div>
        
        <div class="analysis-container">
            {analysis_buttons_html}
        </div>
        
        <div class="subbutton-container">
            {subbutton_buttons_html}
        </div>
        
        <div class="main-content">
            <div class="chart-container">
                {images_html}
            </div>
            <div class="tables-container">
                {generate_tables_html(table_data, table_column_labels)}
            </div>
        </div>
    </div>

    <script>
        let currentAnalysis = '{analysis_types[0]}';
        let currentSubbutton = '{subbuttons[0]}';
        
        // Table data for different analysis types
        const tableData = {table_data_json};
        
        function showAnalysis(analysisType) {{
            currentAnalysis = analysisType;
            updateDisplay();
            updateTables();
            
            // Update button states
            document.querySelectorAll('.analysis-button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.currentTarget.classList.add('active');
        }}
        
        function showSubbutton(subbutton) {{
            currentSubbutton = subbutton;
            updateDisplay();
            
            // Update button states
            document.querySelectorAll('.subbutton-button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.currentTarget.classList.add('active');
        }}
        
        function updateDisplay() {{
            // Hide all images
            const allImages = document.querySelectorAll('.chart-img');
            allImages.forEach(img => img.classList.add('hidden'));
            
            // Show selected image
            const selectedImage = document.getElementById(currentAnalysis + '_' + currentSubbutton + '-img');
            selectedImage.classList.remove('hidden');
        }}
        
        function updateTables() {{
            const data = tableData[currentAnalysis];
            
            // Update metrics table
            const metricsTable = document.getElementById('metrics-table');
            const metricsThead = metricsTable.querySelector('thead');
            const metricsTbody = metricsTable.querySelector('tbody');
            metricsTbody.innerHTML = '';
            if (data && data.metrics) {{
                data.metrics.forEach(row => {{
                    const tr = document.createElement('tr');
                    let rowHtml = `<td>${{row[0]}}</td>`;
                    for (let i = 1; i < row.length; i++) {{
                        rowHtml += `<td>${{row[i]}}</td>`;
                    }}
                    tr.innerHTML = rowHtml;
                    metricsTbody.appendChild(tr);
                }});
                metricsThead.classList.toggle('hidden', data.metrics.length === 0);
            }} else {{
                metricsThead.classList.add('hidden');
            }}

            // Update growth table
            const growthTable = document.getElementById('growth-table');
            const growthThead = growthTable.querySelector('thead');
            const growthTbody = growthTable.querySelector('tbody');
            growthTbody.innerHTML = '';
            if (data && data.growth) {{
                data.growth.forEach(row => {{
                    const tr = document.createElement('tr');
                    let rowHtml = `<td>${{row[0]}}</td>`;
                    for (let i = 1; i < row.length; i++) {{
                        rowHtml += `<td>${{row[i]}}</td>`;
                    }}
                    tr.innerHTML = rowHtml;
                    growthTbody.appendChild(tr);
                }});
                growthThead.classList.toggle('hidden', data.growth.length === 0);
            }} else {{
                growthThead.classList.add('hidden');
            }}
        }}
        
        // Initialize tables
        updateTables();
    </script>
</body>
</html>
"""
    
    return html

def generate_tables_html(table_data, table_column_labels):
    # Generate headers HTML
    headers_html = ''.join([f'<th>{label}</th>' for label in table_column_labels])
    
    # Get the first analysis type for table content
    first_analysis = list(table_data.keys())[0]
    metrics = table_data[first_analysis]['metrics']
    growth = table_data[first_analysis]['growth']
    
    # Generate metrics table rows
    metrics_rows_html = ''
    for row in metrics:
        row_html = f'<tr><td>{row[0]}</td>'
        for value in row[1:]:
            row_html += f'<td>{value}</td>'
        row_html += '</tr>'
        metrics_rows_html += row_html
    
    # Generate growth table rows
    growth_rows_html = ''
    for row in growth:
        row_html = f'<tr><td>{row[0]}</td>'
        for value in row[1:]:
            row_html += f'<td>{value}</td>'
        row_html += '</tr>'
        growth_rows_html += row_html
    
    # Generate the tables HTML
    tables_html = f"""
    <div class="table-box">
        <table class="data-table" id="metrics-table">
            <thead{' class="hidden"' if not metrics else ''}>
                <tr>
                    <th>Metric</th>
                    {headers_html}
                </tr>
            </thead>
            <tbody>
                {metrics_rows_html}
            </tbody>
        </table>
    </div>
    
    <div class="table-box">
        <table class="data-table" id="growth-table">
            <thead{' class="hidden"' if not growth else ''}>
                <tr>
                    <th>Metric</th>
                    {headers_html}
                </tr>
            </thead>
            <tbody>
                {growth_rows_html}
            </tbody>
        </table>
    </div>
    """
    
    return tables_html
