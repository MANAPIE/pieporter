from dotenv import load_dotenv
from urllib.parse import urlparse
import pandas as pd
import os
import requests
import re
import time
import datetime
import fnmatch

load_dotenv()

BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"
COUNT_PER_PAGE = 20
OFFSET_MAX = 9
REQUEST_INTERVAL = 1.1
MAX_RETRIES = 3

_last_request_time = 0.0


def throttle():
    global _last_request_time
    wait = REQUEST_INTERVAL - (time.monotonic() - _last_request_time)
    if wait > 0:
        time.sleep(wait)
    _last_request_time = time.monotonic()


def extract_keywords(search_query):
    query = search_query.replace(' AND ', ' ').replace(' OR ', ' ')
    query = re.sub(r'[^\w\s가-힣]', ' ', query)
    keywords = [kw.strip() for kw in query.split() if kw.strip()]

    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword.lower() not in seen:
            seen.add(keyword.lower())
            unique_keywords.append(keyword)

    return unique_keywords


def highlight_keywords(text, keywords):
    if not text or not keywords:
        return text

    result = text
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        result = pattern.sub(lambda m: f'<mark>{m.group()}</mark>', result)

    return result


def build_freshness():
    try:
        SEARCH_RANGE = int(os.environ.get("SEARCH_RANGE") or 0)
    except ValueError:
        print("    Invalid SEARCH_RANGE, ignoring")
        SEARCH_RANGE = 0

    if SEARCH_RANGE <= 0:
        return None

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=SEARCH_RANGE)

    return f"{start_date.strftime('%Y-%m-%d')}to{end_date.strftime('%Y-%m-%d')}"


def get_exclude_patterns():
    EXCLUDE_SITE = os.environ.get("EXCLUDE_SITE")
    QUERY_SEPERATOR = os.environ.get("QUERY_SEPERATOR") or "|"

    if not EXCLUDE_SITE:
        return []

    return [pattern.strip() for pattern in EXCLUDE_SITE.split(QUERY_SEPERATOR) if pattern.strip()]


def is_excluded(link, exclude_patterns):
    hostname = urlparse(link).hostname or ""

    for pattern in exclude_patterns:
        if pattern.startswith("*."):
            domain = pattern[2:]
            if hostname == domain or hostname.endswith("." + domain):
                return True
        elif "*" in pattern:
            if fnmatch.fnmatch(hostname, pattern):
                return True
        elif hostname == pattern or hostname.endswith("." + pattern):
            return True

    return False


def is_pdf(link):
    return urlparse(link).path.lower().endswith(".pdf")


def request_page(query, offset, freshness):
    BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY")
    BRAVE_COUNTRY = os.environ.get("BRAVE_COUNTRY")
    BRAVE_SEARCH_LANG = os.environ.get("BRAVE_SEARCH_LANG")

    headers = {
        "X-Subscription-Token": BRAVE_API_KEY,
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }

    params = {"q": query, "count": COUNT_PER_PAGE, "offset": offset}

    if freshness:
        params["freshness"] = freshness
    if BRAVE_COUNTRY:
        params["country"] = BRAVE_COUNTRY
    if BRAVE_SEARCH_LANG:
        params["search_lang"] = BRAVE_SEARCH_LANG

    for attempt in range(MAX_RETRIES + 1):
        throttle()
        response = requests.get(BRAVE_API_URL, headers=headers, params=params)

        if response.status_code != 429 or attempt == MAX_RETRIES:
            break

        wait = float(2 ** attempt)
        reset = response.headers.get("X-RateLimit-Reset")
        if reset:
            try:
                wait = max(wait, float(reset.split(",")[0].strip()))
            except ValueError:
                pass

        print(f"    Rate limit: retrying in {wait:.1f}s")
        time.sleep(wait)

    try:
        return response.json()
    except ValueError:
        return {"error": {"status": response.status_code, "detail": "non-JSON response"}}


def search(search_query, row_per_search, original_search_query=None):
    query = search_query

    keywords = []
    if original_search_query:
        keywords = extract_keywords(original_search_query)

    exclude_patterns = get_exclude_patterns()
    freshness = build_freshness()

    for pattern in exclude_patterns:
        domain = pattern[2:] if pattern.startswith("*.") else pattern
        if "*" not in domain:
            query += f" -site:{domain}"

    page_count = min((row_per_search + COUNT_PER_PAGE - 1) // COUNT_PER_PAGE, OFFSET_MAX + 1)

    df = pd.DataFrame(columns=["Title", "Link", "Description"])
    seen_links = set()
    row_count = 0

    if not os.environ.get("BRAVE_API_KEY"):
        print("    Missing BRAVE_API_KEY")
        return df

    print(f"    Search \"{query}\" in Brave")

    for offset in range(page_count):
        data = request_page(query, offset, freshness)

        if "error" in data:
            error = data["error"]
            print(f"    API error {error.get('status') or error.get('code')}: {error.get('detail') or error.get('code')}")
            break

        web = data.get("web") or {}
        search_items = web.get("results")

        if not search_items:
            break

        for search_item in search_items:
            if search_item is not None:
                title = search_item.get("title")
                link = search_item.get("url")
                description = search_item.get("description")

                if not link or link in seen_links:
                    continue
                seen_links.add(link)

                if is_pdf(link) or is_excluded(link, exclude_patterns):
                    continue

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

                df.loc[len(df)] = [title, link, description]

                row_count += 1
            if row_count >= row_per_search:
                break

        if row_count >= row_per_search:
            break

        query_info = data.get("query") or {}
        if not query_info.get("more_results_available"):
            break

    print(f"    {len(df)} results")

    return df
