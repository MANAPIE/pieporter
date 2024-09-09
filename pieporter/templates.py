def stylesheet():
    return """
        <style>
            body {
                margin: 0;
                padding: 0;
            }
        
            .pieporter__container {
                background: #F4F4F7;
                font-size: 1em;
                color: #111111;
            }
            
            .pieporter__body {
                padding: 10px;
                margin: 0 auto;
                max-width: 800px;
            }
        
            .pieporter__for {
                color: #0D47A1;
                font-size: 1.2em;
                padding: 5px 0 5px 12px;
            }
        
            table.pieporter__results {
                background: #FFFFFF;
                border-collapse: collapse;
                width: 100%;
                border-top: 10px solid #FFFFFF;
                margin-bottom: 60px;
                border-radius: 8px;
            }
    
            td.pieporter__results_title {
                text-align: left;
                padding: 10px 12px 5px;
                font-weight: bold;
            }
    
            td.pieporter__results_title a {
                text-decoration: none;
                color: #2196F3;
                word-break: break-all;
                font-size: 0.8em;
            }
    
            td.pieporter__results_description {
                padding: 0 8px;
                font-size: 0.8em;
                color: #999999;
            }
    
            td.pieporter__results_description p {
                text-align: left;
                background-color: #F4F4F7;
                padding: 5px 8px;
                margin-bottom: 10px;
                border-radius: 5px;
            }
        </style>
    """


def report_one(diff):
    body = """
        <html>
        <head>
    """
    body += stylesheet()
    body += """
        </head>
        <body>
        <div class="pieporter__container">
            <div class="pieporter__body">
    """

    body += """
            <table class="pieporter__results">
            <tbody>
        """

    if diff is not None:
        for diff_index, diff_row in diff.iterrows():
            body += f"""
                <tr>
                    <td class="pieporter__results_title">
                        {diff_row['Title']}<br>
                        <a href="{diff_row['Link']}" target="_blank">{diff_row['Link']}</a>
                    </td>
                </tr>
                <tr>
                    <td class="pieporter__results_description" colspan="2">
                        <p>{diff_row['Description']}</p>
                    </td>
                </tr>
            """

    body += """
        </tbody>
        </table>
    """

    body += """
            </div>
        </div>
        </body>
        </html>
    """

    return body


def report_all(results_list):
    body = """
        <html>
        <head>
    """
    body += stylesheet()
    body += """
        </head>
        <body>
        <div class="pieporter__container">
            <div class="pieporter__body">
    """

    for result in results_list:
        body += f"""
            <h2 class="pieporter__for">Search query: {result['query']}</h2>
        """
        body += """
            <table class="pieporter__results">
            <tbody>
        """

        if result['diff'] is not None:
            for diff_index, diff_row in result['diff'].iterrows():
                body += f"""
                    <tr>
                        <td class="pieporter__results_title">
                            {diff_row['Title']}<br>
                            <a href="{diff_row['Link']}" target="_blank">{diff_row['Link']}</a>
                        </td>
                    </tr>
                    <tr>
                        <td class="pieporter__results_description" colspan="2">
                            <p>{diff_row['Description']}</p>
                        </td>
                    </tr>
                """

        body += """
            </tbody>
            </table>
        """

    body += """
            </div>
        </div>
        </body>
        </html>
    """

    return body
