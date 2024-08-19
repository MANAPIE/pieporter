from dotenv import load_dotenv
import os
import requests

load_dotenv()

def google_search(query):
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

    start_page = "1"

    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}&q={SEARCH_QUERY}&start={start_page}"

    response = requests.get(url).json()

    return response

SEARCH_QUERY = os.environ.get('SEARCH_QUERY')

print(google_search(SEARCH_QUERY))