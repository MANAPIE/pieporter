from dotenv import load_dotenv
import pandas as pd
import os
import glob
import requests
import datetime

load_dotenv()


def google_search():
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    SEARCH_QUERY = os.environ.get("SEARCH_QUERY")
    SEARCH_RANGE = int(os.environ.get("SEARCH_RANGE") or 0)
    ROW_PER_SEARCH = int(os.environ.get("ROW_PER_SEARCH"))

    query = SEARCH_QUERY
    query += " -filetype:pdf"

    if SEARCH_RANGE > 0:
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=SEARCH_RANGE)
        query += f" after:{start_date.strftime('%Y-%m-%d')}"

    start_pages = []
    df = pd.DataFrame(columns=["Title", "Link", "Description"])
    row_count = 0

    for i in range(1, ROW_PER_SEARCH + 10, 10):
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
                if row_count >= ROW_PER_SEARCH:
                    break

        else:
            break

    print(f"    {len(df)} results")

    return df


def save_to_csv(df):
    FILE_PREFIX = os.environ.get("FILE_PREFIX") or "pieporter"

    print("    Save in CSV")
    now = datetime.datetime.now()
    df.to_csv(f"result/{FILE_PREFIX}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv", index=False)


def get_recent_result():
    list_of_files = glob.glob('result/*.csv')
    if not list_of_files:
        return None

    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    return df


def compare_dataframes(old_df, new_df):
    if old_df is None:
        return None

    print("    Compare with recent results")
    new_rows = new_df[~new_df.apply(tuple, 1).isin(old_df.apply(tuple, 1))]
    return new_rows


def __init__():
    start = datetime.datetime.now()
    print(f"Start at {start.strftime('%Y-%m-%d %H:%M:%S')}")
    df = google_search()

    print(compare_dataframes(get_recent_result(), df))

    save_to_csv(df)

    end = datetime.datetime.now()
    print(f"Done in {end - start}")


__init__()
