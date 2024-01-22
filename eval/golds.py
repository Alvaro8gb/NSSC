import json
from dataclasses import dataclass

GOLD_FILE = 'golds.json'


@dataclass
class Gold:
    term: str
    context: str
    cuis: list
        
    def __str__(self):
        return f"Gold(term='{self.term}', cuis={self.cuis}, context='{self.context}')"


def load_golds(file=GOLD_FILE):
    with open(file, "r") as archivo:
        content = archivo.read()

    results_json = json.loads(content)
    golds = [Gold(**gold) for gold in results_json]

    return golds
