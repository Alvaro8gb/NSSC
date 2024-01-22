import json
import logging
import sys
import fire 

sys.path.append('.')
from languageModels import LargeLanguageModel
from nssc import map2UMLS
from golds import load_golds
from eval.metrics import correct_cui

entity_mapping = {
    'Cancer Concept': 'CANCER_CONCEPT',
    'Cancer Type': 'CANCER_TYPE',
    'Cancer Expansion': 'CANCER_EXP',
    'Cancer Location': 'CANCER_LOC',
    'Cancer Metastasis': 'CANCER_MET',
    'Cancer Recurrence': 'CANCER_REC',
    'Cancer Subtype' : 'CANCER_SUBTYPE',
    'Molecular Marker': 'MOLEC_MARKER',
    'Cancer Stage': 'CANCER_STAGE',
    'TNM': 'TNM',
    'Treatment Name': 'TRAT',
    'Treatment Schema': 'TRAT_SHEMA',
    'Treatment Drug': 'TRAT_DRUG',
    'Treatment Frequency': 'TRAT_FREQ',
    'Treatment Quantity': 'TRAT_QUANTITY',
    'Surgery': 'SURGERY',
}

inverse_mapping = {v: k for k, v in entity_mapping.items()}


def setup_logging():
    # Configurar el formato del log
    logging.basicConfig(
        # Puedes ajustar el nivel según tus necesidades (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='app.log',  # Nombre del archivo de log
        filemode='a'  # 'a' para agregar registros a un archivo existente, 'w' para sobrescribir el archivo cada vez
    )


def log_list(list_name, data_list):
    # Convertir la lista a formato JSON
    json_data = json.dumps(data_list, indent=2)

    # Registrar la lista en el log
    logging.info(list_name + ":\n" + json_data)


def eval_bench(golds):
    #LLM = LargeLanguageModel("gpt-4", 3, **{'temperature':0, 'max_tokens':400}) 
    #LLM = LargeLanguageModel("gpt-35-turbo", 3, **{'temperature':0, 'max_tokens':400}) 
    LLM = LargeLanguageModel("gpt-35-turbo", 2, **{'temperature':0, 'max_tokens':400}) 
    #LLM = LargeLanguageModel("gpt-4", 2, **{'temperature':0, 'max_tokens':400}) 


    print(LLM)
    logging.info("llm:" + str(LLM))
    logging.info('Evaluation: ' + str(len(golds)) + ' terms')
    terms = [(g.term, inverse_mapping[g.context]) for g in golds]

    terms_bests = map2UMLS(terms, LLM)

    not_found = []
    bad = []
    goods = 0
    global_usage = []

    for g in golds:
        predicted = terms_bests[g.term]["candidates"]
        usage = terms_bests[g.term]["usage"]

        global_usage.append(usage)

        try:
            if predicted == False:
                not_found.append(g.__dict__)
            else:
                if correct_cui(set(g.cuis), set(predicted)): # One element in common
                    goods+=1
                else:
                    bad.append({"term":g.term, "Predict":predicted, "Real": g.cuis})

        except:
            logging.error('Parsing results')

    log_list('Results with no cui', not_found)
    log_list('Results Bad', bad)
    log_list("Usage", global_usage)

    acurracy = round(goods/len(golds), 4)

    logging.info("Accuracy: " + str(acurracy)+ " " + str(LLM))

    print(str(LLM), acurracy)

def main(path_gold="./static/datasets/validation_wo_integrated.json", optimize=True):
    
    print("Starting with", "path", path_gold, "optimize", optimize )
    golds = load_golds(path_gold)
    print("Golds loaded")
    setup_logging()
    logging.info('Starting evalution of benchmark')
    eval_bench(golds)
    logging.info('Ending evalution of benchmark')

if __name__ == "__main__":
    fire.Fire(main)

