# NSCC - A Neuro-Symbolic AI System for Enhancing Accuracy of Named Entity Recognition and Linking from Oncological Clinical Notes

NSCC is a system designed to address the challenge of **oncological entity linking** in clinical narratives written in Spanish. The repository contains a variety of components, each contributing to different aspects of the system's functionality.

![img](./img/approach.png)


## Repository Structure

- **backgroundKnowledge.py:** Module for managing background knowledge used in symbolic reasoning.
  
- **eval:**
  - **eval_elastic.py:** Evaluation script for Elastic Search-based entity linking.
  - **evaluation.py:** General evaluation utilities.
  - **finetune_th.py:** Script for fine-tuning models.
  - **golds.py:** Module for handling gold standard data.
  - **metrics.py:** Metrics calculation utilities.
  - **rules_to_validate.md:** Documentation on rules for validation.
  
- **getDefinitions.py:** Script for obtaining definitions.

- **languageModels.py:** Module for handling large language models (LLMs).
    
- **ncp.py:** Script for handling Named Entity Recognition (NER) using deep learning.
  
- **nssc.py:** Main module encapsulating the NSCC system.
  
- **optimization.py:** Module for optimization-related functionalities.
  
- **read.py:** Module for reading and processing clinical narratives.
  
- **static:**
  - **golds.json:** Gold standard data in JSON format.
  - **sample.md:** Sample clinical narrative for testing purposes.
  - **sample_query_BK.json:** Sample query data related to background knowledge.
  
- **utils.py:** General utility functions for various tasks.

## NSCC System Overview

NSSC employs a holistic approach to oncological entity linking, combining deep learning for context-aware Named Entity Recognition (NER), symbolic reasoning for capturing complex relationships and semantics within clinical text, and large language models (LLMs) for entity disambiguation.

- **NER Component:** Utilizes state-of-the-art techniques to recognize and classify oncological entities such as tumor types, treatment modalities, and relevant clinical concepts.

- **Symbolic System:** Integrates background knowledge and rule-based methods to identify the most appropriate terms in the Unified Medical Language System (UMLS).

- **Entity Disambiguation:** Detects cases requiring disambiguation and, through prompt engineering over LLMs, identifies the most appropriate UMLS terms for recognized entities.

For detailed information on NSSC components, refer to the respective files in the repository.

**Note:** Ensure that you review the LICENSE file for usage permissions and restrictions.