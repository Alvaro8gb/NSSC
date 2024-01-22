
import warnings
import urllib3

from elasticsearch import Elasticsearch, ElasticsearchWarning
from opensearchpy import OpenSearch, RequestsHttpConnection

from util import AbstractUMLSsearcher

warnings.filterwarnings("ignore", category=ElasticsearchWarning)
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LANGUAGES = ["SPA", "ENG", 'POR']  # Languages to include in the query

BOOST_WORDS = ['cancer', 'carcinoma', 'tumor', 'mama']
BOOST = 0.8

BASE = {
    "size": 20,
    "track_scores": True,
    "sort": [
        {"_score": {"order": "desc"}},
        {"freq": {"order": "desc"}}
    ],
    "collapse": {
        "field": "cui"
    }
}

def client_local():
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        connection_class=RequestsHttpConnection
    )

    return client


class UMLSSearcherElastic(AbstractUMLSsearcher):
    def __init__(self, id_query, local=1):
        if local:
            self.searcher = client_local()
            self.index = "umls"
            queries = {"multi_SPA":self.search_multi_SPA, "multi": self.search_multi, "filtered_boosted": self.search_filter, "basic_fuzzy":self.basic_search, "exact":self.exact_search}

            if id_query not in queries:
                raise Exception("This query is not avaiable " + id_query)
            else:           
                self.query = queries[id_query]
                self.query_name = id_query
        else:
            pass
            ENDPOINT = "Antiguamente Hannover"
            self.searcher = Elasticsearch([ENDPOINT])
            self.index = "umls_all_5_tk"

    def process_result(self, elasticResults):
        search_results = elasticResults['hits']['hits']

        return [
            {
                'label': result["_source"]["label"],
                'cui': result["_source"]["cui"],
                'score': int(result["_score"]),
                'freq': int(result["_source"]["freq"]),
                'sgroup': result["_source"]["sgroup"],
                'lang': result["_source"]["lang"]
            }
            for result in search_results
        ]

    def search_multi_SPA(self, term: str):

        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "function_score": {
                                "query": {
                                    "multi_match": {
                                        "query": term,
                                        "fields": ["label"],
                                        "fuzziness": "AUTO"
                                    }
                                },
                                "script_score": {
                                    "script": {
                                        "source": "10 / new StringTokenizer(params['_source']['label']).countTokens()"
                                    }
                                },
                                "boost_mode": "sum"
                            }
                        }
                    ],
                    "filter": {
                        "term": {
                            "lang": "SPA"
                        }
                    }
                }
            }
        }

        elasticResults = self.searcher.search(index=self.index, body=body)

        return self.process_result(elasticResults)
    
    def search_multi(self, term: str):

        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "function_score": {
                                "query": {
                                    "multi_match": {
                                        "query": term,
                                        "fields": ["label"],
                                        "fuzziness": "AUTO"
                                    }
                                },
                                "script_score": {
                                    "script": {
                                        "source": "10 / new StringTokenizer(params['_source']['label']).countTokens()"
                                    }
                                },
                                "boost_mode": "sum"
                            }
                        }
                    ],
                    "filter": {
                        "term": {
                            "lang": "SPA"
                        }
                    }
                }
            }
        }

        elasticResults = self.searcher.search(index=self.index, body=body)

        return self.process_result(elasticResults)
    def search_filter(self, term: str, sgroup: str = '', langs: list[str] = [], boosted: list = BOOST_WORDS) -> list:

        body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "function_score": {
                                "query": {
                                    "multi_match": {
                                        "query": term,
                                        "fields": ["label"],
                                        "fuzziness": "AUTO"
                                    }
                                },
                                "script_score": {
                                    "script": {
                                        "source": "10 / new StringTokenizer(params['_source']['label']).countTokens()"
                                    }
                                },
                                "boost_mode": "sum"
                            }
                        }
                    ],
                    "filter": []
                }
            }
        }

        for word in boosted:
            boosted = {
                "match": {
                    "label": {
                        "query": word,
                        "boost": BOOST
                    }
                }
            }
            body['query']['bool']['should'].append(boosted)

        if sgroup != '':
            query = {"term": {"sgroup": sgroup}}
            body['query']['bool']['filter'].append(query)

        if langs != []:
            query = {"terms": {"lang": langs}}
            body['query']['bool']['filter'].append(query)

        elasticResults = self.searcher.search(index=self.index, body=body)

        return self.process_result(elasticResults)

    def basic_search(self, term: str):
        body = {
            "query": {
                "fuzzy": {
                    "label": {
                        "value": term,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }
        
        elasticResults = self.searcher.search(index=self.index, body=body)
        return self.process_result(elasticResults)

    def exact_search(self, term: str):

        body = {
            "query": {
                "match": {
                    "label": {
                        "query": term
                    }
                }
            }
        }

        elasticResults = self.searcher.search(index=self.index, body=body)

        return self.process_result(elasticResults)

    def search(self, term: str) -> str or None:
        results = self.query(term)
        return results
        
    def __str__(self):
        return f"Text searcher (index='{self.index}', query={self.query_name}')"
