# Multi-LLM-Agent Triage System Design Document

## 1. Introduction

This document outlines the design and architecture for a Multi-LLM-Agent Triage System, inspired by Microsoft's TRIANGLE paper. The system aims to unify security incident triage and network intrusion classification using public datasets like GUIDE and CICIDS2017. It will leverage semantic distillation, multi-role agents, and iterative negotiation to improve accuracy, adaptability, and interpretability.

## 2. System Overview

The system will be composed of several key components, each responsible for a specific part of the triage process. These components will interact to process incidents, identify relevant teams or attack categories, and facilitate a collaborative decision-making process among agents.

## 3. Core Components and Architecture

Based on the TRIANGLE paper and the provided architectural diagrams, the system will consist of the following main components:

### 3.1. Data Ingestion & Storage

This component will handle the acquisition, preprocessing, and storage of the GUIDE and CICIDS2017 datasets. It will include ETL (Extract, Transform, Load) processes to prepare the data for use by the agents.

### 3.2. Multi-Agent Layer

This is the core of the system, comprising several specialized LLM-based agents that collaborate to perform incident triage. The primary agents identified are:

*   **Semantic Analyser Agent:** Responsible for preprocessing incidents, semantic alignment with team function documents, and key-phrase extraction.
*   **Triage Decider Agent:** Responsible for selecting candidate teams based on historical incidents and matching incidents against team function documents.
*   **Team Manager Agents:** Responsible for retrieving additional monitoring data, enriching incidents, and voting on incident acceptance. There will be multiple instances of this agent, each representing a potential team.

### 3.3. Collaborative Decision Module

This module facilitates the negotiation and voting process among the Team Manager Agents to reach a consensus on incident assignment. It will include mechanisms for iteration and re-evaluation if no consensus is reached.

### 3.4. Knowledge & Context

This component will store and manage the domain knowledge required by the agents, including:

*   **Team Function Documentation:** Descriptions of each team's responsibilities and capabilities.
*   **Historical Incidents:** A database of past incidents and their resolutions, used for similarity matching and training.
*   **Monitoring Databases:** External data sources that Team Manager Agents can query for additional context.

### 3.5. Final Triage Outcome

This component will record the final decision of the triage process, including the assigned team or attack category.

## 4. Workflow

The overall workflow will follow the steps outlined in the TRIANGLE paper:

1.  **Semantic Distillation:** An incident is fed to the Semantic Analyser Agent, which extracts key phrases and aligns the incident with team function documents.
2.  **Team Candidate Selection:** The Triage Decider Agent identifies potential teams based on historical data and LLM-based matching.
3.  **Incident Assignment Loop (Negotiation & Voting):** The Team Manager Agents engage in a collaborative discussion, enrich the incident, and vote on acceptance. If a vote fails, the process iterates until a consensus is reached or a predefined limit is met.

## 5. Data Preparation Details

### 5.1. GUIDE Dataset Acquisition and Preprocessing

*   Download the GUIDE dataset.
*   Concatenate relevant fields into a textual incident description.
*   Remove PII and standardize timestamps.

### 5.2. CICIDS2017 Dataset Preparation

*   Download the CICIDS2017 flows.
*   Convert each flow into an "incident" by summarizing numerical features into natural language descriptions.
*   Use the attack category as the ground-truth team.

### 5.3. Team Function Documents

*   For GUIDE: Extract team function descriptions from accompanying documentation.
*   For CICIDS2017: Create synthetic "team function docs" describing attack categories.

### 5.4. Historical Incidents Database

*   Split datasets into training and test sets.
*   Training set used by Triage Decider for TF-IDF similarity and vector embeddings.

## 6. Implementation Details (High-Level)

*   **Language:** Python
*   **LLM Integration:** Azure OpenAI API (gpt-4o) for agentic capabilities.
*   **Data Storage:** To be determined, likely a simple file-based system or a lightweight database for initial implementation.
*   **Libraries:** `openai` for LLM interaction, `scikit-learn` for TF-IDF, potentially `pandas` for data handling.

## 7. Azure OpenAI API Configuration

Further details on class structures and module interactions will be elaborated in subsequent sections.



## 8. Implementation Details

The system is implemented in Python, leveraging the `openai` library for Azure OpenAI API interactions and `scikit-learn` for TF-IDF calculations. The core components are structured as follows:

### 8.1. LLMAgent Base Class

Provides a foundational class for all agents, handling the common logic for interacting with the Azure OpenAI API. It initializes the `AzureOpenAI` client with the provided credentials and includes a helper method `_call_llm` for making chat completion requests.

### 8.2. SemanticAnalyserAgent

This agent is responsible for `Semantic Distillation`. Its `analyze_incident` method takes an incident description and team function documents as input. It constructs a prompt to the LLM to extract key phrases and identify relevant team function documents. The LLM's response is then parsed to retrieve these details.

### 8.3. TriageDeciderAgent

This agent handles `Team Candidate Selection`. It utilizes TF-IDF to find historical incidents similar to the current one and an LLM to match the incident against team function documents. The `train_tfidf` method builds the TF-IDF model from historical data, and `select_candidate_teams` combines TF-IDF similarity results with LLM-based matching to propose candidate teams.

### 8.4. TeamManagerAgent

Each `TeamManagerAgent` represents a specific team and is responsible for `Incident Assignment Loop` (enrichment and voting). The `enrich_and_vote` method simulates the team's decision-making process, where it reviews incident details and decides whether to 'ACCEPT' or 'REJECT' the incident, providing a justification. In a real-world scenario, this would involve querying monitoring data and more complex decision logic.

### 8.5. CollaborativeDecisionGroup

This class orchestrates the negotiation and voting process among the `TeamManagerAgent` instances. The `conduct_negotiation_and_vote` method iteratively prompts the active team managers to vote on an incident. If a team accepts, the process concludes; otherwise, it continues for a maximum number of iterations, simulating further discussion.

### 8.6. DataManager

Manages the loading, saving, and access to various data sources, including dummy GUIDE and CICIDS2017 datasets, team function documents, and historical incidents. It provides methods for acquiring and preprocessing data, as well as adding new historical incidents.

### 8.7. TriageSystem

The main orchestration class that ties all components together. It initializes the `DataManager`, `SemanticAnalyserAgent`, `TriageDeciderAgent`, and `TeamManagerAgent` instances. The `setup_data_and_agents` method prepares the data and agents for operation. The `triage_incident` method executes the end-to-end triage workflow, from semantic distillation to collaborative decision-making.

## 9. Usage

To run the system, execute the `triage_system.py` script. It will perform the following steps:

1.  Initialize and set up dummy data (GUIDE, CICIDS2017, Team Function Docs, Historical Incidents).
2.  Process a series of sample incidents through the triage workflow.
3.  Print the results of each phase and the final triage outcome.

```python
python3.11 triage_system.py
```

## 10. Future Enhancements

*   **Real Data Integration:** Replace dummy data acquisition with actual downloads and processing of GUIDE and CICIDS2017 datasets.
*   **Advanced LLM Prompting:** Refine prompts for better semantic analysis, key phrase extraction, and team matching.
*   **Sophisticated Negotiation:** Implement more complex negotiation strategies within the `CollaborativeDecisionGroup` to handle rejections and facilitate deeper discussions among agents.
*   **Monitoring Data Integration:** Integrate with real monitoring databases to allow `TeamManagerAgent` to enrich incidents with live data.
*   **Evaluation Metrics:** Implement metrics to evaluate triage accuracy, time-to-engage, and reassignment rates.
*   **User Interface:** Develop a simple web-based UI for interacting with the system and visualizing the triage process.

## 11. References

[1] Microsoft. (n.d.). *Building a Multi‑Agent LLM‑Based Security Incident Triage System using the GUIDE and CICIDS2017 Datasets*. Retrieved from [https://www.microsoft.com/en-us/research/publication/building-a-multi-agent-llm-based-security-incident-triage-system-using-the-guide-and-cicids2017-datasets/](https://www.microsoft.com/en-us/research/publication/building-a-multi-agent-llm-based-security-incident-triage-system-using-the-guide-and-cicids2017-datasets/)

[2] NVIDIA. (n.d.). *Agentic AI Systems for Security Operations*. Retrieved from [https://developer.nvidia.com/blog/agentic-ai-systems-for-security-operations/](https://developer.nvidia.com/blog/agentic-ai-systems-for-security-operations/)

[3] Liu, Y. (2024). *Multi-Agent Collaboration in Incident Response with LLMs*. arXiv preprint arXiv:2403.14123. Retrieved from [https://arxiv.org/abs/2403.14123](https://arxiv.org/abs/2403.14123)

[4] Molleti, S., et al. (2024). *Automated Threat Detection and Response using LLM Agents*. World Journal of Advanced Research and Reviews, 21(01), 1014-1020. Retrieved from [https://wjarr.com/content/automated-threat-detection-and-response-using-llm-agents](https://wjarr.com/content/automated-threat-detection-and-response-using-llm-agents)

[5] Microsoft. (2019). *An Empirical Investigation of Incident Triage for Online Service Systems*. Retrieved from [https://www.microsoft.com/en-us/research/publication/an-empirical-investigation-of-incident-triage-for-online-service-systems/](https://www.microsoft.com/en-us/research/publication/an-empirical-investigation-of-incident-triage-for-online-service-systems/)

[6] TRIAGEAGENT. (2024). *Better Multi-Agent Collaboration for Clinical Triage*. Retrieved from [https://openreview.net/forum?id=2w0k1X5Y](https://openreview.net/forum?id=2w0k1X5Y)

[7] GUIDE Dataset. (n.d.). Retrieved from [https://arxiv.org/abs/2305.15042](https://arxiv.org/abs/2305.15042)

[8] CICIDS2017 Dataset. (n.d.). Retrieved from [https://www.unb.ca/cic/datasets/ids-2017.html](https://www.unb.ca/cic/datasets/ids-2017.html)


