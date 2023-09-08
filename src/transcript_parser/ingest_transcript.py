import requests
from typing import Tuple
from bs4 import BeautifulSoup
from src.transcript_parser.conversationswithtyler_parser import conversationswithtyler_parser
from typing import List, Dict
from urllib.parse import urlparse
from parsers import parsers_dict
from models import SourceInterview

class ParsedInterview():
    def __init__(self, url:str) -> None:
        self.url = url
        self.domain = urlparse(url).netloc
        self.parser = parsers_dict.get(self.domain, None)

        if self.parser is None:
            raise ValueError(f"No parser available for domain {self.domain}")

        self.title, self.exchanges = self._download_and_parse()
        self.source_interview = SourceInterview.create_or_update({"title": self.title, "url": self.url, "domain": self.domain})
        self.source_interview.save()
        self.source_interview.add_exchanges(self.exchanges)


    def add_exchanges(self) -> Tuple[str, List[Dict[str, str]]]:
        response = requests.get(self.url)
        response.raise_for_status()  # Raise exception if the request failed

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title found"

        return title, self.parser(response.text)

    def __repr__(self):
        return f"<ParsedInterview title={self.title}>"

