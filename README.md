# AEGIS: A Multi-Agent LLM Framework for Cross-Domain Incident Triage and Negotiated Assignment

## Overview

AEGIS is an autonomous security incident triage framework that leverages Large Language Models (LLMs) to create intelligent, collaborative agents for handling cybersecurity incidents. The system addresses the scalability and efficiency challenges faced by traditional Security Operations Centers (SOCs) through a multi-agent architecture that simulates human team dynamics.

## System Architecture

The framework operates through three primary layers:

1. **Data & Context Layer**: Handles data ingestion, ETL preprocessing, and knowledge base management
2. **Multi-Agent Layer**: Core intelligence layer with specialized agents for semantic analysis and candidate selection
3. **Collaborative Decision Layer**: Manages agent negotiation, voting, and final assignment through iterative consensus


## Datasets

### GUIDE Dataset
- **Domain**: Cloud Incident Reports
- **Type**: Unstructured text (logs, alerts, comments)
- **Ground Truth**: MITRE ATT&CK framework alignment

### CICIDS2017 Dataset
- **Domain**: Network Intrusion Detection
- **Type**: Structured numerical flow data (80+ features)
- **Ground Truth**: Specific attack categories (DDoS, DoS Hulk, Benign, etc.)

## Experimental Results

### Performance Metrics Summary

| Dataset | Success Rate (SR) | Accuracy Rate (AR) | Rejection Rate (RR) | Avg Time per Incident |
|---------|-------------------|--------------------|--------------------|----------------------|
| GUIDE | 100.0% | 76.2% | 0.0% | 7.38 seconds |
| CICIDS2017 | 86.8% | 99.3% | 13.2% | 13.27 seconds |

### Key Findings

- **GUIDE Dataset**: Achieved perfect operational success with 100% incident assignment, demonstrating robust handling of ambiguous, complex cloud incidents
- **CICIDS2017 Dataset**: Near-perfect accuracy (99.3%) on objective classification tasks, validating semantic matching effectiveness
- **Zero Error Rate**: Both datasets showed 0.0% system errors, confirming framework stability and reliability
- **Processing Efficiency**: Average processing time of 7-14 seconds per incident represents significant improvement over manual triage

### Performance Analysis

- **GUIDE**: The 76.2% accuracy reflects the inherent ambiguity in human-labeled ground truth for complex multi-stage attacks. The system prioritizes successful operational assignment over rigid classification matching.
- **CICIDS2017**: The 13.2% rejection rate demonstrates the system's cautious approach on rare attack types, correctly flagging ambiguous cases rather than making potentially incorrect assignments.



## Installation and Setup

```bash
# Clone the repository
git clone https://github.com/zhreyu/AEGIS.git

# Install dependencies
uv init 
source .venv/bin/activate
uv sync

# Configure API keys
export OPENAI_API_KEY="your-api-key"

# Run the framework
python main.py --dataset GUIDE --config config/guide.yaml
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

