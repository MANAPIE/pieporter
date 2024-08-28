from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import smtplib
import os
import glob
import requests
import datetime

load_dotenv()


def google_search(search_query):
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    SEARCH_RANGE = int(os.environ.get("SEARCH_RANGE") or 0)
    ROW_PER_SEARCH = int(os.environ.get("ROW_PER_SEARCH"))

    query = search_query
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

    filename = f"result/{FILE_PREFIX}_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    df.to_csv(filename, index=False)

    return filename


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


def send_email(subject, body, to_email, attachment_path=None):
    EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    SMTP_SERVER = os.environ.get("SMTP_SERVER")
    SMTP_PORT = int(os.environ.get("SMTP_PORT"))

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    print("    Send email")

    if attachment_path is not None:
        attachment = open(attachment_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        print("    Email sent successfully")

    except Exception as e:
        print(f"    Failed to send email: {e}")


def send_report(search_query, diff, result_file):
    EMAIL_PREFIX = os.environ.get("EMAIL_PREFIX")
    EMAIL_TO = os.environ.get("EMAIL_TO")

    subject = EMAIL_PREFIX + f"New search result for {search_query}"
    body = ""
    for diff_index, diff_row in diff.iterrows():
        body += f"{diff_row['Title']}\n{diff_row['Link']}\n{diff_row['Description']}\n\n"

    send_email(subject, body, EMAIL_TO, result_file)


def __init__():
    start = datetime.datetime.now()
    print(f"Start at {start.strftime('%Y-%m-%d %H:%M:%S')}")

    SEARCH_QUERY = os.environ.get("SEARCH_QUERY")

    df = google_search(SEARCH_QUERY)
    diff = compare_dataframes(get_recent_result(), df)

    result_file = save_to_csv(df)

    send_report(SEARCH_QUERY, diff, result_file)

    end = datetime.datetime.now()
    print(f"Done in {end - start}")


__init__()
