from dotenv import load_dotenv
import pandas as pd
import os
import requests

load_dotenv()


def google_search():
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    SEARCH_QUERY = os.environ.get('SEARCH_QUERY')
    ROW_PER_SEARCH = int(os.environ.get('ROW_PER_SEARCH'))

    query = SEARCH_QUERY
    query += "-filetype:pdf"

    start_pages = []
    df = pd.DataFrame(columns=['Title', 'Link', 'Description'])
    row_count = 0

    for i in range(1, ROW_PER_SEARCH + 10, 10):
        start_pages.append(i)

    for start_page in start_pages:
        url = (f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}"
               f"&q={query}&start={start_page}")

        data = requests.get(url).json()
        search_items = data.get("items")

        for i, search_item in enumerate(search_items, start=1):
            if search_item is not None:
                link = search_item.get("link")
                title = search_item.get("title")
                description = search_item.get("snippet")

                df.loc[start_page + i] = [title, link, description]

                row_count += 1
            if row_count >= ROW_PER_SEARCH:
                break

    return df


print(google_search())
