import pprint
import time
from ncp import struct
from read import process_input
import logging
import traceback
from backgroundKnowledge import UMLSSearcherElastic
from getDefinitions import UMLSSQL
from languageModels import LargeLanguageModel
from utils import make_combs, Candidate
from optimization import filter_by_similarity
from tqdm import tqdm



NORMALIZE_ENTS = ["CANCER_CONCEPT", 'CANCER_EXP', 'CANCER_LOC', 'CANCER_TYPE',
                  'CANCER_SUBTYPE', 'CANCER_INTRATYPE', 'SURGERY', 'TRAT', 'TRAT_DRUG']

MODEL = 'gpt-4'  # 'gpt-3.5-turbo' # #
MAX_TOKENS = 100  # Should be adjust depende on the query
TEMPERATURE = 0.5  # Low temperature to be the more precciss as posible

DB_ESLASTIC = UMLSSearcherElastic(id_query="filtered_boosted")
DB_SQL = UMLSSQL()

def input(clinical_note: str = None):

    data = None

    if clinical_note is not None:
        data = struct(clinical_note)
    else:
        data = process_input(struct)

    if data == None:
        raise Exception('No data passed!')

    clinical_list = data['data']['diags']

    # Obtained only the new values
    for diagnosis in clinical_list:
        for key, value in diagnosis.items():
            if isinstance(value, dict):
                new_value = value.get('new')
                diagnosis[key] = new_value[0]

    return clinical_list

def extract_entities(clinical_list):

    entities = {ent: None for ent in NORMALIZE_ENTS}

    for diagnosis in clinical_list:
        for ent in entities:
            entities[ent] = diagnosis.get(ent)

    print('\n\nEntities;', entities, '\n\n')

    return entities

def search_term(term, searcher: UMLSSearcherElastic, optimize=True) -> list[Candidate]:
    results = searcher.search(term)
    
    candidates = [Candidate(r['cui'], r['sgroup'], r['label']) for r in results]

    if len(candidates) > 0:

        langs = set([ r['lang'] for r in results])

        if 'SPA' not in langs and 'ENG' not in langs:
            print("The term is founded in oder language", term)
            print(langs)
            pprint.pprint(list(map(str, candidates)))
        
        if optimize:
            return filter_by_similarity(term, candidates)
        else:
            return candidates
    else:
        print("BK dont found: ", term)
        return []

def get_umls_definition(umls_definitions, candidates):

    for c in candidates:
        if c.cui not in umls_definitions:
            definitions = DB_SQL.get_cui_definition(c.cui)
            first_def = definitions[0][0] if definitions else None

            umls_definitions[c.cui] = first_def

        c.set_definition(umls_definitions[c.cui])


def disambiguate(term:str, context:str, llm:LargeLanguageModel, candidates):

    result = llm.ask_llm(term, context, candidates)
    answer = result["answer"]

    revised_candidates = answer.get('candidates', False)

    term_transleted = answer.get('translation', False)

    return revised_candidates, term_transleted, result


def select_best_candidates(term: str, context:str, llm: LargeLanguageModel, candidates: list[Candidate], umls_definitions: dict) -> list[str]:

    api_usage = []

    print('\n Term:', term, '\n')

    if len(candidates) == 0:
        print("No candidates")
        return {"candidates":False, "usage": False}
    
    if len(candidates) == 1:  # Best candidates is alredy founded
        return {"candidates": [candidates[0].cui], "usage": False}
    
    # Desambiguate with LLM
    try:

        get_umls_definition(umls_definitions, candidates)

        revised_candidates, term_transleted, result = disambiguate(
            term, context, llm, candidates)
        
        api_usage.append(result)

        if revised_candidates == False:

            print(term_transleted)

            new_candidates = search_term(term_transleted, DB_ESLASTIC)

            if len(new_candidates) == 0:
                return {"candidates":False, "usage": False}
             
            if len(candidates) == 1:  # Best candidates is alredy founded
                return {"candidates": [candidates[0].cui], "usage": False}
            
            # Try in English
            get_umls_definition(umls_definitions, new_candidates)

            revised_candidates, _, result = disambiguate(
                term_transleted, context, llm, new_candidates)
            
            api_usage.append(result)

        print(revised_candidates)

        return {"candidates": revised_candidates, "usage": api_usage}

    except Exception as e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
        time.sleep(10)
        return {"candidates":False, "usage": False, "why": str(e), "term": term}

 
def map2UMLS(terms_context, llm:LargeLanguageModel):
    '''

    '''

    # Background Knowledge
    term_candidates_context = [(term, context, search_term(term, DB_ESLASTIC)) for term, context in tqdm(terms_context, "Quering BK")]

    # Algorith that select the best
    DB_SQL.open_connection()
    umls_definitions = {}

    terms_bests = {term: select_best_candidates(
        term, context, llm, candidates, umls_definitions) for term, context, candidates in term_candidates_context}
    
    DB_SQL.close_connection()

    return terms_bests


def main():
    '''
    Map a cancer diagnosis and tratments concepts to UMLS

    In: a string that represent the clinical note
    Out: The best cuis that represent the clinical note

    Pipeline: 
    raw text -> (NCP) -> JSON strucutred clinical note -> terms2normalize -> 
    (elastic search) -> list of candidates for each term -> remove duplicates for each term -> 
    (mySQL - Definitions) -> prepare best candidates ->
    (LLM-OPENAI) -> best cui for each term -> JSON structured and normalized

    '''

    LLM = LargeLanguageModel("gpt-4", 3, {'temperature':TEMPERATURE, 'max-tokens':MAX_TOKENS}) 

    clinical_list = input()

    ents = extract_entities(clinical_list)

    terms = make_combs(ents)

    if len(terms) == 0:
        print('No terms found')
        return 0

    best_terms = map2UMLS(LLM, terms)

    pprint.pprint(best_terms)

if __name__ == '__main__':
    main()
