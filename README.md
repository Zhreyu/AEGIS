# Multi-LLM-Agent Triage System

A sophisticated incident triage system that uses multiple Large Language Model (LLM) agents to automatically classify and assign security incidents to appropriate teams.

## Architecture Overview

The system implements a multi-agent architecture with the following components:

### Core Agents

1. **Semantic Analyser Agent**: Extracts key phrases and performs semantic analysis of incident descriptions
2. **Triage Decider Agent**: Uses TF-IDF similarity and LLM-based matching to select candidate teams
3. **Team Manager Agents**: Represent different security teams and vote on incident acceptance
4. **Collaborative Decision Group**: Facilitates negotiation and voting among team managers

### Data Management

- **DataManager**: Handles data ingestion, preprocessing, and storage
- Supports GUIDE and CICIDS2017 datasets
- Automatic team function document generation
- Historical incident tracking for TF-IDF training

## Installation and Setup

### Prerequisites

```bash
pip install openai scikit-learn pandas pyarrow
```

### Kaggle API Setup

1. Place your `kaggle.json` API key file in the project directory
2. The system will automatically configure Kaggle access

### Running the System

```bash
python3.11 main.py
```

## System Workflow

### Phase 1: Semantic Distillation
- Analyzes incident descriptions using LLM
- Extracts relevant key phrases
- Identifies potentially relevant team documents

### Phase 2: Team Candidate Selection
- Uses TF-IDF similarity with historical incidents
- Performs LLM-based matching against team function documents
- Combines results to create candidate team list

### Phase 3: Incident Assignment Loop
- Creates collaborative decision group with candidate teams
- Conducts multi-round negotiation and voting
- Teams can accept or reject incidents with justification

### Phase 4: Final Triage Outcome
- Assigns incident to accepting team
- Logs decision process and rationale

## Data Sources

### CICIDS2017 Dataset
- Network intrusion detection dataset
- Contains various attack types: DoS, DDoS, Brute Force, etc.
- Processed from parquet files for efficiency

### GUIDE Dataset
- Incident triage dataset
- Contains historical incident descriptions and team assignments
- Used for TF-IDF training and validation

## Team Categories

The system automatically identifies and creates teams based on data:

- **Benign**: Normal network traffic and system behavior
- **DoS/DDoS Attacks**: Denial of service incidents
- **Brute Force**: Password and credential attacks
- **Infiltration**: Unauthorized access attempts
- **Web Attacks**: Application-layer security incidents
- **Botnet**: Compromised system incidents
- **Port Scan**: Network reconnaissance activities

## Configuration

### Azure OpenAI Integration
The system uses Azure OpenAI for LLM capabilities. Configuration is handled in `triage_system.py`:

```python
AZURE_OPENAI_API_KEY = "your-api-key"
AZURE_OPENAI_ENDPOINT = "your-endpoint"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"
```

## Sample Usage

The system processes various incident types:

```python
sample_incidents = [
    "Server outage in datacenter A, error code 503, high network latency.",
    "Application unresponsive, database connection failed.",
    "Suspicious network activity detected: multiple failed login attempts from unknown IP.",
    "Unusual traffic spike, potential DoS attack on web server.",
    "New malware detected on endpoint, requires immediate isolation."
]
```

## Output Format

Each triage operation returns:

```python
{
    "final_result": "Incident assigned to: TeamName",
    "triage_outcome": {
        "status": "ACCEPTED",
        "assigned_team": "TeamName",
        "discussion_log": [...]
    },
    "analysis_result": {
        "key_phrases": [...],
        "relevant_docs": [...],
        "llm_raw_response": "..."
    },
    "candidate_teams": [...]
}
```

## File Structure

```
project/
├── main.py                    # Main execution script
├── triage_system.py          # Core system implementation
├── download_kaggle_datasets.py # Data acquisition script
├── data/                     # Data directory
│   ├── guide/               # GUIDE dataset files
│   ├── cicids2017/          # CICIDS2017 parquet files
│   ├── guide_incidents.json # Processed GUIDE data
│   ├── cicids_incidents.json # Processed CICIDS data
│   └── team_function_docs.json # Team descriptions
└── README.md               # This documentation
```

## Performance Considerations

- Data sampling limits (1000 samples by default) to manage memory usage
- TF-IDF vectorization for efficient similarity computation
- Parquet format for fast data loading
- Caching of preprocessed data to avoid recomputation

## Extensibility

The system is designed for easy extension:

- Add new agent types by inheriting from `LLMAgent`
- Implement custom team selection algorithms
- Integrate additional data sources
- Customize negotiation and voting logic

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all required packages are installed
2. **Kaggle API**: Verify `kaggle.json` is properly configured
3. **Memory Issues**: Reduce sample sizes if processing large datasets
4. **API Limits**: Monitor Azure OpenAI usage and rate limits

### Logging

The system provides detailed console output for each phase:
- Data acquisition and preprocessing status
- Agent decision rationales
- Voting outcomes and team assignments

## Future Enhancements

- Real-time incident streaming
- Advanced negotiation strategies
- Performance metrics and evaluation
- Web-based dashboard interface
- Integration with existing ITSM systems

