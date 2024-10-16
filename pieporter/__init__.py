from dotenv import load_dotenv
from difflib import SequenceMatcher
import pandas as pd
import os
import glob
import datetime

import send_email
import google_search

from .templates import report_all

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
    SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD") or 0.9)

    if old_df is None:
        return new_df

    print("    Compare with recent results")

    def similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    new_rows = []

    for new_index, new_row in new_df.iterrows():
        is_new = True
        for old_index, old_row in old_df.iterrows():
            title_similarity = similarity(new_row['Title'], old_row['Title'])
            description_similarity = similarity(new_row['Description'], old_row['Description'])
            if title_similarity > SIMILARITY_THRESHOLD or description_similarity > SIMILARITY_THRESHOLD:
                is_new = False
                break
        if is_new:
            new_rows.append(new_row)

    return pd.DataFrame(new_rows)


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

    body = templates.report_one(diff)

    send_email.send_email(subject, body, EMAIL_TO, "html", [result_file])


def send_reports_at_once(results_list):
    EMAIL_PREFIX = os.environ.get("EMAIL_PREFIX")
    EMAIL_TO = os.environ.get("EMAIL_TO")

    if EMAIL_TO is None:
        print("    No email address to send")
        return

    subject = EMAIL_PREFIX + f"New search results for {len(results_list)} queries"
    body = ""

    body = report_all(results_list)

    attachment_path_list = [result['file'] for result in results_list]

    send_email.send_email(subject, body, EMAIL_TO, "html", attachment_path_list)


def search():
    SEARCH_QUERY = os.environ.get("SEARCH_QUERY")
    QUERY_SEPERATOR = os.environ.get("QUERY_SEPERATOR")
    EXCLUDE_SITE = os.environ.get("EXCLUDE_SITE")
    SEARCH_RANGE = int(os.environ.get("SEARCH_RANGE") or 0)
    ROW_PER_SEARCH = min([int(os.environ.get("ROW_PER_SEARCH") or 10), 100])
    SEND_REPORT_EACH = bool(os.environ.get("SEND_REPORT_EACH"))

    search_query_list = SEARCH_QUERY.split(QUERY_SEPERATOR)
    results_list = []

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

        if SEND_REPORT_EACH:
            send_report(search_query, diff, result_file)
        else:
            results_list.append({"query": search_query, "diff": diff, "file": result_file})

    if not SEND_REPORT_EACH:
        send_reports_at_once(results_list)
