# NSSC: Neuro-Symbolic System for Cancer
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14042506.svg)](https://doi.org/10.5281/zenodo.14042506)


NSCC is a system designed to address the challenge of **oncological entity linking** in clinical narratives written in Spanish. The repository contains a variety of components, each contributing to different aspects of the system's functionality.


<img src="./img/flow-chart.png" width="60%" height="auto">


## NSCC System Overview

NSSC employs a holistic approach to oncological entity linking, combining deep learning for context-aware Named Entity Recognition (NER), symbolic reasoning for capturing complex relationships and semantics within clinical text, and large language models (LLMs) for entity disambiguation.

- **Named Entity Recognition:** Utilizes state-of-the-art techniques to recognize and classify oncological entities such as tumor types, treatment modalities, and relevant clinical concepts.

- **Medical Entity Linking:** Integrates background knowledge and rule-based methods to identify the most appropriate terms in the Unified Medical Language System (UMLS).

- **Medical Entity Disambiguation:** Detects cases requiring disambiguation and, through prompt engineering over LLMs, identifies the most appropriate UMLS terms for recognized entities.

For detailed information on NSSC components, refer to the respective files in the repository.


## Repository Structure

- **bk_indexer.py:** Module for managing background knowledge used in symbolic reasoning.
- **bk_definitions.py:** Script for obtaining definitions.

- **eval:**
  - **eval_elastic.py:** Evaluation script for Search-based entity linking.
  - **evaluation.py:** General evaluation utilities.
  - **finetune_th.py:** Script for fine-tuning models.
  - **golds.py:** Module for handling gold standard data.
  - **metrics.py:** Metrics calculation utilities.
  - **rules_to_validate.md:** Documentation on rules for validation.
  

- **llm.py:** Module for handling large language models (LLMs).
    
- **ner.py:** Script for handling Named Entity Recognition (NER) using deep learning.
  
- **nssc.py:** Main module encapsulating the NSCC system.
  
- **optimization.py:** Module for optimization-related functionalities.
    
- **static:**
  - **golds.json:** Gold standard data in JSON format.
  - **sample.md:** Sample clinical narrative for testing purposes.
  - **sample_query_BK.json:** Sample query data related to background knowledge.
  
- **utils.py:** General utility functions for various tasks.



**Note:** Ensure that you review the LICENSE file for usage permissions and restrictions.


### Set up

Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Acknowledgments

- This research is based on the paper [NSCC: A Neuro-Symbolic AI System for Enhancing Accuracy of Named Entity Recognition and Linking from Oncological Clinical Notes](https://link.springer.com/article/10.1007/s11517-024-03227-4), published in [Medical & Biological Engineering & Computing](https://link.springer.com/journal/11517).
- If you find it useful you can cite it in:
```bibtext
@article{10.1007/s11517-024-03227-4, 
year = {2024}, 
title = {{NSSC: a neuro-symbolic AI system for enhancing accuracy of named entity recognition and linking from oncologic clinical notes}}, 
author = {García-Barragán, Álvaro and Sakor, Ahmad and Vidal, Maria-Esther and Menasalvas, Ernestina and Gonzalez, Juan Cristobal Sanchez and Provencio, Mariano and Robles, Víctor}, 
journal = {Medical \& Biological Engineering \& Computing}, 
issn = {0140-0118}, 
doi = {10.1007/s11517-024-03227-4}, 
abstract = {{Accurate recognition and linking of oncologic entities in clinical notes is essential for extracting insights across cancer research, patient care, clinical decision-making, and treatment optimization. We present the Neuro-Symbolic System for Cancer (NSSC), a hybrid AI framework that integrates neurosymbolic methods with named entity recognition (NER) and entity linking (EL) to transform unstructured clinical notes into structured terms using medical vocabularies, with the Unified Medical Language System (UMLS) as a case study. NSSC was evaluated on a dataset of clinical notes from breast cancer patients, demonstrating significant improvements in the accuracy of both entity recognition and linking compared to state-of-the-art models. Specifically, NSSC achieved a 33\% improvement over BioFalcon and a 58\% improvement over scispaCy. By combining large language models (LLMs) with symbolic reasoning, NSSC improves the recognition and interoperability of oncologic entities, enabling seamless integration with existing biomedical knowledge. This approach marks a significant advancement in extracting meaningful information from clinical narratives, offering promising applications in cancer research and personalized patient care.}}, 
pages = {1--24}
}
```
