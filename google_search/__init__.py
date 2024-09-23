from dotenv import load_dotenv
import pandas as pd
import os
import requests

load_dotenv()


def search(search_query, row_per_search):
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

    query = search_query

    start_pages = []
    df = pd.DataFrame(columns=["Title", "Link", "Description"])
    row_count = 0

    for i in range(1, row_per_search + 1, 10):
        start_pages.append(i)

    print(f"    Search \"{query}\" in Google")

    for start_page in start_pages:
        url = (f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}"
               f"&q={query}&start={start_page}")

        data = requests.get(url).json()
        search_items = data.get("items")

        if search_items is not None:
            for i, search_item in enumerate(search_items, start=1):
                if search_item is not None:
                    title = search_item.get("title")
                    link = search_item.get("link")
                    description = search_item.get("snippet")

                    df.loc[start_page + i] = [title, link, description]

                    row_count += 1
                if row_count >= row_per_search:
                    break

        else:
            break

    print(f"    {len(df)} results")

    return df
