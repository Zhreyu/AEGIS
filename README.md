# AEGIS - Advanced Security Triage System

A modular, object-oriented security incident triage system using multiple LLM agents for collaborative decision-making in security operations.

## 🏗️ Architecture

The AEGIS system is built with a clean, modular architecture following object-oriented principles:

```
AEGIS/
├── src/                    # Main source code
│   ├── agents/            # LLM agents for analysis and decision-making
│   │   ├── base_agent.py
│   │   ├── semantic_analyser.py
│   │   ├── triage_decider.py
│   │   ├── team_manager.py
│   │   └── collaborative_decision.py
│   ├── data/              # Data management and processing
│   │   ├── data_manager.py
│   │   ├── dataset_processor.py
│   │   └── team_document_manager.py
│   ├── core/              # Core triage system orchestration
│   │   └── triage_system.py
│   └── utils/             # Utility functions and helpers
│       ├── logger.py
│       ├── validators.py
│       └── formatters.py
├── config/                # Configuration management
│   └── settings.py
├── tests/                 # Test suite
├── docs/                  # Documentation
├── data/                  # Data storage directory
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
└── setup.py             # Package setup
```

## 🚀 Features

- **Multi-Agent Architecture**: Specialized LLM agents for different aspects of triage
- **Semantic Analysis**: Advanced incident description analysis and key phrase extraction
- **Collaborative Decision-Making**: Team managers negotiate and vote on incident assignments
- **Historical Data Integration**: TF-IDF similarity matching with historical incidents
- **Modular Design**: Clean separation of concerns with extensible components
- **Comprehensive Logging**: Detailed logging and monitoring capabilities

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access
- Kaggle API key (for dataset download)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/AEGIS.git
   cd AEGIS
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   export AZURE_OPENAI_API_KEY="your-api-key"
   export AZURE_OPENAI_ENDPOINT="your-endpoint"
   export AZURE_OPENAI_API_VERSION="2024-12-01-preview"
   export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
   ```

4. **Download datasets** (optional):
   ```bash
   python download_kaggle_datasets.py
   ```

## 🎯 Usage

### Basic Usage

```python
from src.core import TriageSystem

# Initialize the triage system
triage_system = TriageSystem()
triage_system.setup_data_and_agents()

# Triage an incident
incident = "Database server experiencing high CPU usage and connection timeouts"
result = triage_system.triage_incident(incident)

print(result['final_result'])
```

### Running the Main Script

```bash
python main.py
```

### Advanced Usage

```python
from src.core import TriageSystem
from src.agents import SemanticAnalyserAgent, TriageDeciderAgent

# Initialize components
triage_system = TriageSystem()
triage_system.setup_data_and_agents()

# Batch processing
incidents = [
    "Server outage in datacenter A, error code 503",
    "Suspicious network activity detected",
    "Application unresponsive, database connection failed"
]

results = triage_system.batch_triage_incidents(incidents)

# Get system status
status = triage_system.get_system_status()
print(f"System initialized: {status['initialized']}")
print(f"Available teams: {status['available_teams']}")
```

## 🧩 Components

### Agents (`src/agents/`)

- **BaseLLMAgent**: Base class for all LLM agents
- **SemanticAnalyserAgent**: Analyzes incidents and extracts key phrases
- **TriageDeciderAgent**: Selects candidate teams using TF-IDF and LLM matching
- **TeamManagerAgent**: Represents team managers for voting
- **CollaborativeDecisionGroup**: Manages team negotiation and voting

### Data Management (`src/data/`)

- **DataManager**: Main data coordinator
- **DatasetProcessor**: Processes GUIDE and CICIDS2017 datasets
- **TeamDocumentManager**: Creates and manages team function documents

### Core System (`src/core/`)

- **TriageSystem**: Main orchestrator for the triage process

### Utilities (`src/utils/`)

- **Logger**: Logging configuration and utilities
- **Validators**: Data validation functions
- **Formatters**: Output formatting utilities

## ⚙️ Configuration

The system uses environment variables for configuration:

```bash
# Required
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=your-endpoint

# Optional
DATA_DIR=./data
GUIDE_SAMPLE_SIZE=500
CICIDS_SAMPLE_SIZE=500
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_triage_system.py
```

## 📊 Data Sources

- **GUIDE Dataset**: Microsoft Security Incident Prediction dataset
- **CICIDS2017**: Canadian Institute for Cybersecurity Intrusion Detection dataset

## 🔧 Development

### Adding New Agents

```python
from src.agents.base_agent import BaseLLMAgent

class CustomAgent(BaseLLMAgent):
    def __init__(self):
        super().__init__("Custom Agent", "custom analysis agent")
    
    def analyze(self, data):
        # Custom analysis logic
        return self.call_llm(prompt)
```

### Adding New Data Sources

```python
from src.data.dataset_processor import DatasetProcessor

class CustomDatasetProcessor(DatasetProcessor):
    def process_custom_dataset(self, data):
        # Custom processing logic
        return processed_data
```

## 📈 Performance

The system is designed for scalability:

- **Parallel Processing**: Multiple agents can work simultaneously
- **Caching**: TF-IDF models are cached for performance
- **Batch Processing**: Support for processing multiple incidents
- **Configurable Sample Sizes**: Adjustable dataset sizes for different use cases

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Contact the development team
- Check the documentation in `docs/`

## 🔮 Roadmap

- [ ] Web interface using Streamlit
- [ ] REST API using FastAPI
- [ ] Real-time monitoring dashboard
- [ ] Integration with popular SIEM tools
- [ ] Advanced ML models for improved accuracy
- [ ] Multi-language support
- [ ] Cloud deployment options

---

**AEGIS** - Empowering Security Operations with AI-Driven Triage