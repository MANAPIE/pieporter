## Pie-Porter
```pieporter```

Search through the search engine,<br>
And report the results via email with a CSV file.<br>

If previous search results exist, report contains only new items.<br>
You can configure how many recent results to compare against.<br>
(By the way, CSV file has all results.)

---

<br>

## Requirements

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) >= 3.10

<br>

## How to run

1. edit ``.env``

2. run


    python pieporter.py

<br>

## Configuration

### Email Report Settings for ```send_email```
- ```EMAIL_ADDRESS```: Sender's email address (ID)
- ```EMAIL_PASSWORD```: Sender's email password
- ```SMTP_SERVER```: SMTP server address
- ```SMTP_PORT```: SMTP server port

### Brave Search API Settings for ```brave_search```
- ```BRAVE_API_KEY```: Brave Search API KEY<br> https://api-dashboard.search.brave.com/
- ```BRAVE_COUNTRY```: (Optional) 2-letter country code for search results (e.g. KR)
- ```BRAVE_SEARCH_LANG```: (Optional) Language code for search results (e.g. ko)
- ```ROW_PER_SEARCH```: Number of search results per search
  - Default value is 10, maximum value is 100
  - Results are fetched in pages of 20 per API request
> Brave Search API may incur charges. Be careful.

### Pie-Porter Settings for ```pieporter```
- ```SEARCH_QUERY```: Search keywords
    - You can use search operators supported by Brave Search
- ```QUERY_SEPERATOR```: Seperator for multiple search queries
    - Default value is |
- ```EXCLUDE_SITE```: Exclude site from search results
    - Separate multiple sites with ```QUERY_SEPERATOR```
    - Results whose hostname matches are filtered out (wildcards like ```*.facebook.com``` supported)
- ```SEARCH_RANGE=```: Search range in days from today
    - Default value is 0, and it means unlimited search range.
- ```FILE_PREFIX```: Prefix for the CSV file name
- ```EMAIL_PREFIX```: Prefix for the email subject
- ```EMAIL_TO```: Receiver's email address
- ```SEND_REPORT_EACH```: If there is a value(means not false), send separate emails for each keyword.
- ```SIMILARITY_THRESHOLD```: If the similarity between the previous search result and the current search result is higher than this value, the current search result is considered as the same as the previous search result.
    - Default value is 0.9
- ```COMPARE_RECENT_N```: Number of recent search results to compare with current results
    - Default value is 1
- ```HIDE_EMPTY_RESULTS```: If there is a value(means not false), hide queries with no new results from the report.
    - The CSV file is still saved for future comparison, but the query is omitted from the email body and attachments.
    - When every query has no new results, no email is sent.


---

<br>

### Example of ```.env```

    # send_email
    EMAIL_ADDRESS=@@@
    EMAIL_PASSWORD=@@@
    SMTP_SERVER=@@@
    SMTP_PORT=587
    
    # brave_search
    BRAVE_API_KEY=BSA1234567890abcdefghijklmnopqrstuv
    BRAVE_COUNTRY=KR
    BRAVE_SEARCH_LANG=ko
    ROW_PER_SEARCH=2
    
    # pieporter
    SEARCH_QUERY="\"GUI\" trends OR news|\"python\" news"
    QUERY_SEPERATOR="|"
    EXCLUDE_SITE="*.facebook.com|*.tiktok.com"
    SEARCH_RANGE=7
    FILE_PREFIX=
    EMAIL_PREFIX='[pieporter] '
    EMAIL_TO=@@@
    SEND_REPORT_EACH=
    SIMILARITY_THRESHOLD=0.9
    COMPARE_RECENT_N=1
    HIDE_EMPTY_RESULTS=



### ...And its result

![pieporter_example](https://github.com/user-attachments/assets/10f1644b-b987-4055-a880-ae2d8110b7f5)

Reports are mobile-friendly and also dark-mode-friendly.


