## Pie-Porter
```pieporter```

Search through the search engine,<br>
And report the results via email with a CSV file.<br>

If the immediate previous search result exists, report contains only new items.<br>
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

### Google Search API Settings for ```google_search```
- ```GOOGLE_SEARCH_ENGINE_ID```: Google Search Engine ID<br> https://programmablesearchengine.google.com/
- ```GOOGLE_API_KEY```: GCP Custom Search Engine allowed API KEY<br> https://console.cloud.google.com/apis/credentials
- ```ROW_PER_SEARCH```: Number of search results per search
  - Default value is 10, maximum value is 100
> Google Search API may incur charges. Be careful.

### Pie-Porter Settings for ```pieporter```
- ```SEARCH_QUERY```: Search keywords
    - You can use Google search operators 
- ```QUERY_SEPERATOR```: Seperator for multiple search queries
    - Default value is |
- ```EXCLUDE_SITE```: Exclude site from search results
    - Separate multiple sites with ```QUERY_SEPERATOR```
    - Adds ```-site:example.com``` to search query
- ```SEARCH_RANGE=```: Search range in days from today
    - Default value is 0, and it means unlimited search range.
- ```FILE_PREFIX```: Prefix for the CSV file name
- ```EMAIL_PREFIX```: Prefix for the email subject
- ```EMAIL_TO```: Receiver's email address
- ```SEND_REPORT_EACH```: If there is a value(means not false), send separate emails for each keyword.


---

<br>

### Example of ```.env```

    # send_email
    EMAIL_ADDRESS=@@@
    EMAIL_PASSWORD=@@@
    SMTP_SERVER=@@@
    SMTP_PORT=587
    
    # google_search
    GOOGLE_SEARCH_ENGINE_ID=1234567890abcdef
    GOOGLE_API_KEY=1234567890abcdefghijklmnopqrstuvwxyz-_=
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



### ...And its result

![pieporter_example](https://github.com/user-attachments/assets/10f1644b-b987-4055-a880-ae2d8110b7f5)

Reports are mobile-friendly and also dark-mode-friendly.


