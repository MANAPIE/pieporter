from dotenv import load_dotenv
from collections import deque
import pandas as pd
import os
import requests
import re
import time

load_dotenv()

RATE_LIMIT_PER_MINUTE = 90
_request_times = deque()


def throttle():
    now = time.monotonic()
    while _request_times and now - _request_times[0] >= 60:
        _request_times.popleft()
    if len(_request_times) >= RATE_LIMIT_PER_MINUTE:
        wait = 60 - (now - _request_times[0])
        if wait > 0:
            print(f"    Rate limit: sleeping {wait:.1f}s")
            time.sleep(wait)
        now = time.monotonic()
        while _request_times and now - _request_times[0] >= 60:
            _request_times.popleft()
    _request_times.append(time.monotonic())


def extract_keywords(search_query):
    query = search_query.replace(' AND ', ' ').replace(' OR ', ' ')
    query = re.sub(r'[^\w\s가-힣]', ' ', query)
    keywords = [kw.strip() for kw in query.split() if kw.strip()]

    return keywords


def highlight_keywords(text, keywords):
    if not text or not keywords:
        return text

    result = text
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        result = pattern.sub(lambda m: f'<mark>{m.group()}</mark>', result)

    return result


def search(search_query, row_per_search, original_search_query=None):
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

    query = search_query

    keywords = []
    if original_search_query:
        keywords = extract_keywords(original_search_query)

    start_pages = []
    df = pd.DataFrame(columns=["Title", "Link", "Description"])
    row_count = 0

    for i in range(1, row_per_search + 1, 10):
        start_pages.append(i)

    print(f"    Search \"{query}\" in Google")

    for start_page in start_pages:
        url = (f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}"
               f"&q={query}&start={start_page}")

        throttle()
        data = requests.get(url).json()

        if "error" in data:
            error = data["error"]
            print(f"    API error {error.get('code')}: {error.get('message')}")
            break

        search_items = data.get("items")

        if search_items is not None:
            for i, search_item in enumerate(search_items, start=1):
                if search_item is not None:
                    title = search_item.get("title")
                    link = search_item.get("link")
                    description = search_item.get("snippet")

                    if len(keywords) >= 2:
                        matched = sum(
                            1 for kw in keywords
                            if (title and re.search(re.escape(kw), title, re.IGNORECASE))
                            or (description and re.search(re.escape(kw), description, re.IGNORECASE))
                        )
                        if matched < 2:
                            continue

                    if keywords and title:
                        title = highlight_keywords(title, keywords)

                    if keywords and description:
                        description = highlight_keywords(description, keywords)

                    df.loc[start_page + i] = [title, link, description]

                    row_count += 1
                if row_count >= row_per_search:
                    break

        else:
            break

    print(f"    {len(df)} results")

    return df
