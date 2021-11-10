from urllib.parse import quote
from bs4 import BeautifulSoup
import json
import re
import requests

class Term:
    def __init__(self, similarity, informal, vulgar, term):
        self.similarity = similarity
        self.informal = informal
        self.vulgar = vulgar
        self.term = term
        self.url = f"https://thesaurus.com/browse/{quote(term)}"


class Tab:
    def __init__(self, synonyms, antonyms, definition, definitionType):
        self.synonyms = synonyms
        self.antonyms = antonyms

        if definitionType == "adj.":
            definitionType = "adjective"

        self.category = {"definition": definition, "definitionType": definitionType}


def getTerms(key, data):
    terms = []

    for term in data[key]:
        terms.append(
            Term(
                int(term["similarity"]),
                bool(term["isInformal"]),
                bool(term["isVulgar"]),
                term["term"],
            )
        )
    return terms


def parsePosTabs(data):
    tabs = []
    for posTab in data:
        tabs.append(
            Tab(
                getTerms("synonyms", posTab),
                getTerms("antonyms", posTab),
                posTab["definition"],
                posTab["pos"],
            )
        )
    return tabs


def main(word):
    r = requests.get(f"https://thesaurus.com/browse/{quote(word)}")

    if r.status_code == 404:
        return "Not found"

    dom = BeautifulSoup(r.text, "html.parser")

    script = (
        (dom.find("script", string=re.compile("window.INITIAL_STATE")).contents[0])
        .split("window.INITIAL_STATE =")[1]
        .replace("undefined", "null")
        .replace(";", "")
        .strip()
    )

    data = json.loads(script)

    return parsePosTabs(data["searchData"]["tunaApiData"]["posTabs"])
