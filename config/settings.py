import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CHROMA_PERSIST_DIR = "data/chroma"
COLLECTION_NAME = "gst-regulations"
