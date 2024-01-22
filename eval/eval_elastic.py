
import sys
import time
import fire

sys.path.append('.')

from golds import load_golds
from nssc import search_term
from backgroundKnowledge import UMLSSearcherElastic
from tqdm import tqdm
import pandas as pd 

COLUMNS = ["Query", "Accuracy Top1", "Accuracy Top15", "Execution Time"]

def eval(golds_term, term_candidates):

    top1 = 0
    inCandidates = 0

    for term, candidates in term_candidates:

        if len(candidates) > 0:

            real_cuis = golds_term[term]
            candidates_cuis = [c.cui for c in candidates]

            if len(set(real_cuis) & set(candidates_cuis)) > 0:
                inCandidates += 1
            else:
                print("Not in candidates of BK:", term)

            if real_cuis[0] == candidates_cuis[0]:
                top1 += 1

        else:
            print("Empty query result;", term, real_cuis)

    acurracyTop1 = round(top1/len(golds_term), 4)
    acurracyInCandidates = round(inCandidates/len(golds_term), 4)

    return acurracyTop1, acurracyInCandidates

def eval_query(terms, searcher, optimize=True):
    return [(t, search_term(t, searcher, optimize)) for t in tqdm(terms, desc="Query terms to BK")]

def eval_searcher(terms, searcher, golds_terms, optimize=True):
    start_s = time.time()
    terms_candidates = eval_query(terms, searcher, optimize)
    end_s = time.time()

    ac1, acAll = eval(golds_terms, terms_candidates)
    print('acurracyTop1:', ac1)
    print('acurracyTop15:', acAll)
    
    return ac1, acAll, end_s-start_s
        
       
def main(path_gold="golds.json", optimize=True):

    print("Starting with", "path", path_gold, "optimize", optimize )
    golds = load_golds(path_gold)

    print("Number of terms to validate:", len(golds))

    terms = [g.term for g in golds]
    golds_terms = {g.term: g.cuis for g in golds}

    results = []
    serchers = [UMLSSearcherElastic(id_query=query ) for query in ["multi", "filtered_boosted", "multi_SPA", "basic_fuzzy", "exact" ] ] 

    for searcher in serchers:
        print("Evaluating with:", searcher)
        
        ac1, acall, t = eval_searcher(terms, searcher, golds_terms, optimize)
        results.append((searcher.query_name, ac1, acall, t ))


    df = pd.DataFrame(results, columns=COLUMNS)  

    print(df)


if __name__ == '__main__':
    fire.Fire(main)
