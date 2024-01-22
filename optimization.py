from dataclasses import dataclass
from similarity import similarity_semantic, similarity_string, similarity_transformer
from util import Candidate

HOLD = 0.95

@dataclass
class SimilarTerm:
    similarity: int
    candidate: Candidate

def filter_by_similarity(term: str, candidates: list[Candidate], hold=HOLD, calculate_sim=similarity_string) -> list[Candidate]:

    good_candidates = {}
    group_candidates = {}

    for c in candidates:

        sim = calculate_sim(term, c.label)

        if sim >= hold:

            if c.cui not in good_candidates:
                good_candidates[c.cui] = SimilarTerm(sim, c)
            else:
                if good_candidates[c.cui].similarity > sim:
                    group_candidates[c.cui] = SimilarTerm(sim, c)

        if c.cui not in group_candidates:
            group_candidates[c.cui] = SimilarTerm(sim, c)
        else:
            sim_now = calculate_sim(term, c.label)

            if sim_now > group_candidates[c.cui].similarity:
                group_candidates[c.cui] = SimilarTerm(sim_now, c)


    if len(good_candidates) > 0:
        return [similarTerm.candidate for similarTerm in good_candidates.values()]
    else:
        return [similarTerm.candidate for similarTerm in group_candidates.values()]