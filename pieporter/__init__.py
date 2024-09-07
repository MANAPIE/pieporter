from dotenv import load_dotenv
import pandas as pd
import os
import glob
import datetime

import send_email
import google_search

load_dotenv()


def save_to_csv(search_query, df):
    FILE_PREFIX = os.environ.get("FILE_PREFIX") or "pieporter"

    print("    Save in CSV")
    now = datetime.datetime.now()

    filename = f"result/{FILE_PREFIX}_{search_query}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    df.to_csv(filename, index=False)

    return filename


def get_recent_result(search_query):
    FILE_PREFIX = os.environ.get("FILE_PREFIX") or "pieporter"

    list_of_files = glob.glob(f'result/{FILE_PREFIX}_{search_query}_*.csv')
    if not list_of_files:
        return None

    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    return df


def compare_dataframes(old_df, new_df):
    if old_df is None:
        return new_df

    print("    Compare with recent results")
    new_rows = new_df[~new_df.apply(tuple, 1).isin(old_df.apply(tuple, 1))]
    return new_rows


def send_report(search_query, diff, result_file):
    EMAIL_PREFIX = os.environ.get("EMAIL_PREFIX")
    EMAIL_TO = os.environ.get("EMAIL_TO")

    if EMAIL_TO is None:
        print("    No email address to send")
        return

    subject = EMAIL_PREFIX + f"New search result for {search_query}"
    body = ""

    if diff is not None:
        for diff_index, diff_row in diff.iterrows():
            body += f"{diff_row['Title']}\n{diff_row['Link']}\n{diff_row['Description']}\n\n"

    send_email.send_email(subject, body, EMAIL_TO, result_file)


def search():
    SEARCH_QUERY = os.environ.get("SEARCH_QUERY")
    QUERY_SEPERATOR = os.environ.get("QUERY_SEPERATOR")
    EXCLUDE_SITE = os.environ.get("EXCLUDE_SITE")
    SEARCH_RANGE = int(os.environ.get("SEARCH_RANGE") or 0)
    ROW_PER_SEARCH = int(os.environ.get("ROW_PER_SEARCH"))

    search_query_list = SEARCH_QUERY.split(QUERY_SEPERATOR)
    for search_query in search_query_list:
        query = search_query
        query += " -filetype:pdf"

        if EXCLUDE_SITE:
            exclude_site_list = EXCLUDE_SITE.split(QUERY_SEPERATOR)
            for exclude_site in exclude_site_list:
                query += f" -site:{exclude_site}"

        if SEARCH_RANGE > 0:
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=SEARCH_RANGE)
            query += f" after:{start_date.strftime('%Y-%m-%d')}"

        df = google_search.search(query, ROW_PER_SEARCH)
        diff = compare_dataframes(get_recent_result(search_query), df)

        result_file = save_to_csv(search_query, df)

        send_report(search_query, diff, result_file)
