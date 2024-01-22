from abc import ABC, abstractmethod
from itertools import product
from typing import List

START_ENTITY = "CANCER_CONCEPT"

DIAG_ENTITIES = ['CANCER_EXP', 'CANCER_LOC',
                 'CANCER_TYPE', 'CANCER_SUBTYPE', 'CANCER_INTRATYPE']

TREATMENT_ENTITIES = ['SURGERY', 'TRAT', 'TRAT_DRUG']

FULL_CONCEPT = {'CANCER_EXP', 'CANCER_LOC', 'CANCER_TYPE'}


def join_comb(elements: list):
    return ' '.join(str(e) for e in elements)


def get_combs(first_list: List[str], second_list: List[str]):
    combinations = list(product(first_list, second_list))
    return [join_comb(c) for c in combinations]


def make_combs(ents: dict):

    basic_terms = []
    meddium_terms = []
    treat_terms = []
    full_terms = []

    concept = ents[START_ENTITY]
    diag_terms = [ents[key] for key in DIAG_ENTITIES if ents[key] != None]

    basic_terms = get_combs([concept], diag_terms)
    treat_terms = [ents[key]
                   for key in TREATMENT_ENTITIES if ents[key] != None]

    # Three concepts
    if len(diag_terms) > 1:
        duplex = get_combs([diag_terms[0]], diag_terms[1:])
        meddium_terms = [join_comb([concept, e]) for e in duplex]

    # Full concept
    diags_keys = {key for key in DIAG_ENTITIES if ents[key] != None}

    if FULL_CONCEPT <= diags_keys:
        full_terms = [join_comb(
            [concept, ents['CANCER_TYPE'], ents['CANCER_EXP'], ents['CANCER_LOC']])]

    return basic_terms + meddium_terms + treat_terms + full_terms

# Searcher

class AbstractUMLSsearcher(ABC):
    """
    An abstract class representing a UMLS (Unified Medical Language System) searcher.

    This class provides the structure for implementing a UMLS searcher that aims to find the Concept Unique Identifier (CUI)
    for a given term. The subclasses should implement the search method to perform the actual search in UMLS.

    """

    @abstractmethod
    def search(self, term: str) -> str or None:
        """
        Performs a search in UMLS for the specified term and returns the corresponding CUI if found, or None if not found.

        Args:
            term (str): The term to search for in UMLS.

        Returns:
            str or None: The Concept Unique Identifier (CUI) if the term is found in UMLS, or None if the term is not found.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        pass


class Candidate:
    def __init__(self, cui, semantic_group, label):
        self.cui = cui
        self.semantic_group = semantic_group
        self.label = label
        self.definition = None

    def set_definition(self, definition):
        self.definition = definition

    def __str__(self):
        return f"CUI: {self.cui}, Semantic Group: {self.semantic_group}, Label: {self.label}, Definition: {self.definition}"

