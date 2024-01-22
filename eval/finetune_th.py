
import sys
import pandas as pd
sys.path.append('.')  # run in WD

from evaluation import load_golds
from optimization import filter_by_similarity
from backgroundKnowledge import UMLSSearcherElastic
from tqdm import tqdm
from util import Candidate


def finetune_th(golds_term, term_candidates, threshold: int):
    term_ranked_candidates = [(t, filter_by_similarity(
        t, candidates, threshold), candidates) for t, candidates in term_candidates]
    be_in_filt = 0
    be_in_all = 0

    for term, candidates_filt, candidates_all in term_ranked_candidates:

        real_cuis = golds_term[term]
        candidate_all_cuis = [c.cui for c in candidates_filt]
        candidate_filt_cuis = [c.cui for c in candidates_all]

        if len(set(real_cuis) & set(candidate_filt_cuis)) > 0:
            be_in_filt += 1

        if len(set(real_cuis) & set(candidate_all_cuis)) > 0:
            be_in_all += 1

    acurracyAll = round(be_in_filt/len(golds_term), 4)
    acurracyFiltered = round(be_in_all/len(golds_term), 4)

    print('Be in All:', acurracyAll)
    print('Be in Filtered:', acurracyFiltered)

    return acurracyAll, acurracyFiltered

def search_umls(searcher, term):
    results = searcher.search(term)
    return [Candidate(r['cui'], r['sgroup'], r['label']) for r in results]

def main(path_gold="golds.json"):

    searcher = UMLSSearcherElastic(id_query="filtered_boosted")

    golds = load_golds(path_gold)
    print("Number of terms in benchmark", len(golds))

    terms = [g.term for g in golds]

    golds_term = {g.term: g.cuis for g in golds}
    terms_candidates = [(term, search_umls(searcher, term) ) for term in tqdm(terms, "Searching in UMLS")]

    print("Finish to query BK")

    results = []

    for threshold in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.96, 0.97, 0.98, 1]:
        print("Testing with th:", threshold)
        acurracyAll, acurracyFiltered = finetune_th(
            golds_term, terms_candidates, threshold)
        results.append({"Threshold": threshold, "Be in All": acurracyAll,
                       "Be in Filtered": acurracyFiltered})

    result_df = pd.DataFrame(
        results, columns=["Threshold", "Be in All", "Be in Filtered"])

    print(result_df)

if __name__ == '__main__':
    main()
