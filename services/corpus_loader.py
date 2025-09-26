import os
import requests
from typing import List, Dict
from bs4 import BeautifulSoup, Tag

class CorpusService:
    """
    Service to fetch and load scriptures, old books, and public domain texts
    from Project Gutenberg, Internet Archive, or local files.
    """

    def __init__(self):
        self.gutenberg_base = "https://www.gutenberg.org"
        self.archive_search = "https://archive.org/advancedsearch.php"

    def fetch_from_gutenberg(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search and fetch books from Project Gutenberg.
        Returns a list of dicts with 'title' and 'content'.
        """
        url = f"https://www.gutenberg.org/ebooks/search/?query={query}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        books = []
        for link in soup.select(".booklink")[:max_results]:
            title_elem = link.select_one(".title")
            a_elem = link.find("a")
            if not title_elem or not a_elem or not isinstance(a_elem, Tag):
                continue
            title = title_elem.text.strip()
            href = a_elem.get("href")
            if not href or not isinstance(href, str):
                continue
            book_id = href.split("/")[-1]
            text_url = f"{self.gutenberg_base}/files/{book_id}/{book_id}-0.txt"

            try:
                txt = requests.get(text_url, timeout=10)
                if txt.status_code == 200:
                    content = txt.text[:50000]  # limit to first 50k chars
                    books.append({"title": title, "content": content, "source": "Gutenberg"})
            except:
                continue

        return books

    def fetch_from_archive(self, query: str, max_results: int = 2) -> List[Dict]:
        """
        Search and fetch books from Internet Archive.
        """
        params = {
            "q": f"{query} mediatype:texts collection:opensource",
            "fl[]": "identifier,title",
            "rows": max_results,
            "output": "json"
        }
        try:
            r = requests.get(self.archive_search, params=params, timeout=10)
            print(f"Archive search status: {r.status_code}")
            if r.status_code != 200:
                return []

            data = r.json()
        except Exception as e:
            print(f"Error fetching from archive: {e}")
            return []
        docs = data.get("response", {}).get("docs", [])
        print(f"Archive docs count: {len(docs)}")
        for doc in docs:
            print(f"Doc: {doc.get('title', 'No title')} - identifier: {doc.get('identifier', 'No id')}")

        books = []
        for doc in docs:
            identifier = doc["identifier"]
            title = doc["title"]

            # Get metadata to find .txt file
            metadata_url = f"https://archive.org/metadata/{identifier}"
            try:
                meta_r = requests.get(metadata_url, timeout=10)
                if meta_r.status_code != 200:
                    continue
                meta = meta_r.json()
                files = meta.get("files", [])
                print(f"For {identifier}, files: {[f.get('name', '') for f in files]}")
                txt_file = None
                for f in files:
                    name = f.get("name", "")
                    if name.endswith(".txt"):
                        txt_file = name
                        break
                print(f"For {identifier}, txt_file: {txt_file}")
                if not txt_file:
                    continue
                url = f"https://archive.org/download/{identifier}/{txt_file}"
                txt = requests.get(url, timeout=10)
                if txt.status_code == 200:
                    content = txt.text[:50000]
                    books.append({"title": title, "content": content, "source": "Archive"})
            except:
                continue

        return books

    def load_local_text(self, file) -> Dict:
        """
        Load text from a local uploaded file (.txt only here).
        """
        content = file.read().decode("utf-8", errors="ignore")
        return {"title": file.name, "content": content, "source": "Local"}
