"""
Simple data ingestion script to populate vector stores.
"""

from dotenv import load_dotenv

from app.datastore import initialise_all_stores
from app.utils import check_api_key

load_dotenv()

if __name__ == "__main__":
    print("----Starting data ingestion---")

    try:
        has_api_key = check_api_key()
        if not has_api_key:
            raise ValueError("OpenAI API key is not set")
        initialise_all_stores()
        print("--Data ingestion completed!---")

    except Exception as e:
        print(f"Error: {e}")
