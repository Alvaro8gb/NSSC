
import os
import json
import openai
import requests
from typing import List
from dotenv import load_dotenv
from typing import List, Literal, TypedDict

Role = Literal["system", "user", "assistant"]


class Message(TypedDict):
    role: Role
    content: str


Dialog = List[Message]

class ResultOpenAI(TypedDict):
    answer:dict
    prompt_tokens:int
    completion_tokens:int
    total_tokens:int


LLMs = {'gpt', 'llama'}

DEF_NCI = "forms in tissues of the breast, usually the ducts (tubes that carry milk to the nipple) and lobules (glands that make milk)"

def generate_behave(term, context):
    return f"""You are an assistant and a skilled linguist specialized in entity linking text to a vocabulary. 
                In the background of breast cancer diagnosis, that {DEF_NCI}.
                Predict the best candidate term of Unified Medical Language System (UMLS) for the label '{term}' and the context '{context}'.
                
                Consider also the definition, semantic group and the labels of the candidates. 
                Ensure that all the words are present in the term and nothing more. 
                In the case where two candidates are synonyms, return both in the order with more coincidence, considering the clauses and the context.

                The output should be always  in JSON  format as especified bellow:
                    If you you think the CUI or CUIS is in the candidates return it in this format: {{"candidates": ["<CUI>"]}}. 
                In case of not found the best return: {{"translation": <term translated to english>}}.
                
            """

def zero_prompt(term, context):
    return {
            "role": "system",
            "content": f"""
                {generate_behave(term, context)}
                """
        }

def few_prompt(term, context):
    return {
            "role": "system",
            "content": f"""
                
                Promt:
                {generate_behave(term, context)}

                Positive example:
                        In: 
                            Term: carcinoma mama
                            Candidates: 
                                CUI: C0678222, Semantic Group: DISO, Label: carcinoma de mama, Definition: The presence of a carcinoma of the breast. [HPO:probinson]
                                CUI: C4209064, Semantic Group: LIVB, Label: mama, Definition: None
                                CUI: C0566398, Semantic Group: DISO, Label: mama, Definition: None
                                CUI: C0006141, Semantic Group: ANAT, Label: mama, Definition: In humans, one of the paired regions in the anterior portion of the THORAX. The breasts consist of the MAMMARY GLANDS, the SKIN, the MUSCLES, the ADIPOSE TISSUE, and the CONNECTIVE TISSUES.
                        Out: {{"candidates": ["C0678222"]}}

                    Negative example:
                        In: 
                                Term: cancer mama
                                Candidates: 
                                    CUI: C4209064, Semantic Group: LIVB, Label: mama, Definition: None
                                    CUI: C0566398, Semantic Group: DISO, Label: mama, Definition: None
                                    CUI: C0006141, Semantic Group: ANAT, Label: mama, Definition: In humans, one of the paired regions in the anterior portion of the THORAX. The breasts consist of the MAMMARY GLANDS, the SKIN, the MUSCLES, the ADIPOSE TISSUE, and the CONNECTIVE TISSUES.
                        Out: {{"translation": "breast carcinoma"}}
                """
        }


def cot_prompt(term, context):
    return {
        "role": "system",
        "content": f"""
            {generate_behave(term, context)}
            Provide an explanation of the outcome and include it in the JSON as: {{"explanation":" text explaining why you take this decision"}}
            
            Here is an example of what you should behave:

                Positive example:
                    In: 
                        Term: carcinoma mama
                        Candidates: 
                            CUI: C0678222, Semantic Group: DISO, Label: carcinoma de mama, Definition: The presence of a carcinoma of the breast. [HPO:probinson]
                            CUI: C4209064, Semantic Group: LIVB, Label: mama, Definition: None
                            CUI: C0566398, Semantic Group: DISO, Label: mama, Definition: None
                            CUI: C0006141, Semantic Group: ANAT, Label: mama, Definition: In humans, one of the paired regions in the anterior portion of the THORAX. The breasts consist of the MAMMARY GLANDS, the SKIN, the MUSCLES, the ADIPOSE TISSUE, and the CONNECTIVE TISSUES.
                    Out: {{"candidates": ["C0678222"] , "explanation": "Because 'carcinoma de mama' is the same as 'carcinoma mama'"}}

                Negative example:
                    In: 
                        Term: cancer mama
                        Candidates: 
                            CUI: C4209064, Semantic Group: LIVB, Label: mama, Definition: None
                            CUI: C0566398, Semantic Group: DISO, Label: mama, Definition: None
                            CUI: C0006141, Semantic Group: ANAT, Label: mama, Definition: In humans, one of the paired regions in the anterior portion of the THORAX. The breasts consist of the MAMMARY GLANDS, the SKIN, the MUSCLES, the ADIPOSE TISSUE, and the CONNECTIVE TISSUES.
                    Out: {{"translation": "breast carcinoma"}}  
        """
    }


PROMTS_TYPE = { 1: zero_prompt, 2:few_prompt, 3:cot_prompt}

def generate_messages(term: str, context: str, candidates, promt_type:int) -> Dialog:

    candidates_text = "\nCandidates: " + \
        '\n\t'.join([str(c) for c in candidates])


    dialog = [PROMTS_TYPE[promt_type](term, context)
        ,
        {
            "role": "user",
            "content": candidates_text
        }
    ]

    return dialog


class LargeLanguageModel():

    def __init__(self, model_name, promt_type=0, **params):
        base = model_name.split('-')[0]
        self.model_name = model_name
        self.promt_type = promt_type

        if base in LLMs:
            self.name = model_name
            self.params = params

            if base == 'gpt':
                
                load_dotenv()

                openai.api_key = os.getenv("OPENAI_API_KEY")
                openai.api_base = os.getenv("OPENAI_API_BASE")
                openai.api_type = 'azure'
                openai.api_version = "2023-05-15"

                self.query = self.query_openai
            else:

                self.query = self.query_llama
        else:
            raise Exception('No model found')

    def query_openai(self, dialog: Dialog):

        response = openai.ChatCompletion.create(
            engine=self.model_name,
            messages=dialog,
            temperature=self.params['temperature'],
            max_tokens=self.params['max_tokens']
        )

        response_message = response["choices"][0]["message"]

        # print(msgs)
        # print("Assistant:", response_message)

        return ResultOpenAI(answer=json.loads(response_message['content']), 
                            promt_tokens=response["usage"]["prompt_tokens"], 
                            completion_tokens=response["usage"]["completion_tokens"], 
                            total_tokens=response["usage"]["total_tokens"])

    def query_llama(self, dialog=Dialog):

        url = "http://localhost:8001/chat"
        headers = {"Content-Type": "application/json"}

        data = {"dialogs": [dialog]}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        result = {'data': False}

        if response.status_code == 200:
            data = response.json()[0]["generation"]["content"]
            result = {'data': data}
        else:
            print("Error code:", response.status_code)

        print(result)
        return result

    def ask_llm(self, term: str, context: str, candidates) -> dict:

        msgs = generate_messages(term, context, candidates, self.promt_type)

        result = self.query(msgs)

        return result
    
    def __str__(self):
        return f"Gold(model_name='{self.model_name}', promt_type={self.promt_type}, params='{self.params}')"



