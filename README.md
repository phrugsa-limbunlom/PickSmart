<h1 align="center"> PickSmart 🛒 </h1>
<div align="center">
<img alt="Langchain" src="https://img.shields.io/badge/-Langchain-013243?style=flat&logo=langchain&logoColor=white"> <img alt="Langgraph" src="https://img.shields.io/badge/-Langgraph-013243?style=flat&logo=Langgraph&logoColor=white"> <img alt="Tavily" src="https://img.shields.io/badge/-Tavily-231F20?style=flat&logo=Tavily&logoColor=white"> <img alt="MongoDB" src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white"><img alt="Tavily" src="https://img.shields.io/badge/-Groq-231F20?style=flat&logo=Groq&logoColor=white"><img alt="FastAPI" src="https://img.shields.io/badge/-Fastapi-009688?style=flat&logo=Fastapi&logoColor=white"> <img alt="Kafka" src="https://img.shields.io/badge/-Kafka-231F20?style=flat&logo=kafka&logoColor=white">
</div>
<br>
<p align="center">
AI-powered shopping assistant platform for real-time product search with contextual question-answering and personalized product recommendations empowered by the intelligent search and analyst agent:
</p>
<br>

![image](https://github.com/user-attachments/assets/3d2d0ca7-cfa9-4fec-8b2c-c802e5134411)


## 📌 Overview

PickSmart is a distributed and AI-powered product discovery platform that leverages the large language model and distributed system to provide real-time product search, contextual question-answering, and personalized product recommendations. The system integrates a Retrieval-Augmented Generation (RAG) architecture with a search agent (Hybrid RAG) for product discovery across multiple e-commerce marketplaces.


## 🚀 Features
|   Name  | Description |
|-------|-------------|
| **Ask a question about a product** | Submit a query to get detailed information, including specifications, pricing, and availability. |
| **Search multiple marketplaces and rank the results**| The system aggregates product listings from various online marketplaces, compares and ranks them based on relevance, price, and customer reviews. |
| **Receive personalized recommendations** |  Get AI-driven suggestions tailored to users' preferences, helping users make informed decisions. |

## ⚡Core Capabilities
|  Function | Description |
|-----------|-------------|
|**Natural Language Query Processing** | Advanced query decomposition and semantic analysis
| **Vector Database Integration** | Efficient data ingestion and storage for embedding-based semantic retrieval.
| **Distributed Real-time Search** | Multi-marketplace product discovery with parallel processing
| **Intelligent Product Ranking** | AI-powered relevance scoring and personalization
| **Context-Aware Recommendations** | Detailed answers with product suggestions
| **Scalable Data Processing** | Event-driven architecture for high-throughput data handling


## 🎥 Demo


https://github.com/user-attachments/assets/47f57b9d-7c8b-4d37-8943-06d1eba58961



## 🛠️ Tech Stack
- **Frontend**: React
- **Backend**: FastAPI
- **Streaming**: Kafka
- **RAG System**: LangChain, MongoDB (vector store)
- **Agents**: LangGraph, Tavily (search)
- **API Client**: Groq API


## 📐System Architecture

<div align="center">
    <img src="https://github.com/user-attachments/assets/f6c2d2f2-b5bd-462b-9998-e17dae221f3b" width="600" height="450">
</div>


### Frontend Layer
- **Framework**: React.js with TypeScript
- **State Management**: Redux for predictable state container
- **API Integration**: Axios for HTTP client

### Backend Services
- **API Framework**: FastAPI with asynchronous request handling and high-performance routing
- **Message Broker**: Apache Kafka for event streaming and distributed processing
- **Vector Store**: MongoDB for efficient similarity search and embedding storage
- **Search Engine**: Tavily API integration for real-time and accurate web search capabilities

### AI Components
- **LLM Integration**: Groq API for high-performance inference
- **Agent Framework**: LangChain for composable AI components
- **Workflow Orchestration**: LangGraph for agent coordination and planning
- **RAG System**: MongoDB for vector index implementation and semantic retrieval

### Agent Architecture

The system implements a search and analyst agent with a multi-step workflow using LangGraph for orchestration:

```python
graph = StateGraph(SearchAgentState)
graph.add_node("analyze_query", self.analyze_query_node)
graph.add_node("search_online_shop", self.search_online_node)
graph.add_node("analyze_and_rank", self.analyze_rank_node)
graph.add_node("search_product_source", self.search_source_node)
graph.set_entry_point("analyze_query")
graph.add_edge("analyze_query", "search_online_shop")
graph.add_edge("search_online_shop", "analyze_and_rank")
graph.add_edge("analyze_and_rank", "search_product_source")
graph.set_finish_point("analyze_and_rank")
self.graph = graph.compile(checkpointer=checkpointer)
```

The search and analyst agent progresses through the following sequential states:

| State | Name | Description |
|:-----:|-------|-------------|
|   1   | 🔍 **Query Analysis State** | Analyzes and decomposes the user query before identifying search intent and extracts key product attributes, serving as the entry point for all search requests |
|   2   | 🛒 **Online Shop Search State** | Performs search across multiple online websites, retrieves initial product information from available sources, and gathers raw product data for further analysis |
|   3   | ⭐ **Analysis and Ranking State** | Evaluates and ranks products using multiple criteria, prioritizing results based on relevance and quality to deliver the most appropriate options to users |
|   4   | 🔗 **Product Source Search State** | Extends search to discover additional product sources across e-commerce platforms, provides a direct purchasing link, and validates product availability |

The workflow follows a linear progression through these states, from which each state is built upon the results of the previous states.

## 📂 Folder Structure

This project contains a chatbot application with a backend server, Kafka integration, and a frontend interface.

```bash
chatbot-app  
├── public              # Static assets for the frontend  
├── src                 # Source code for the frontend  
├── .gitignore          # Git ignore file for frontend  
├── Dockerfile          # Dockerfile for frontend containerization  
├── package-lock.json   # Dependency lock file  
├── package.json        # Node.js project configuration  

chatbot-server  
├── src                 # Source code for the backend  
│   ├── agent           # AI agent-related logic  
│   ├── constants       # Configuration and constant values  
│   ├── data            # Data handling and storage logic  
│   ├── processor       # Data processing and transformation logic  
│   ├── service         # Business logic and service layer  
│   ├── utils           # Utility functions and helpers  
│   ├── chatbot.py      # Main chatbot logic  
│   ├── main.py         # Entry point for the backend server  
├── .gitignore          # Git ignore file for backend  
├── Dockerfile          # Dockerfile for backend containerization  
├── __init__.py         # Marks the package directory  
├── model.yaml          # AI model configuration file  
├── requirements.txt    # Python dependencies  

kafka  
├── config              # Kafka configuration files  
├── Dockerfile          # Dockerfile for Kafka setup  
├── .gitignore          # Git ignore file for Kafka  

LICENSE                 # Project license file  

```
   
## ⚙️ Configuration

### Environment Variables
Create ```.env``` file under ```chatbot-server``` folder and add API keys and MongoDB configuration as below:

```env
GROQ_API_KEY="<API_KEY>"
TAVILY_API_KEY="<API_KEY>"
CO_API_KEY="<API_KEY>"
MONGO_USER_NAME="<USERNAME>"
MONGO_PASSWORD="<PASSWORD>"
MONGO_CLUSTER="picksmart-cluster"
MONGO_DATABASE="picksmart"
```
- To get Groq api key: https://console.groq.com/keys
- To get Tavily api key: https://tavily.com/
- To get Cohere api key: https://dashboard.cohere.com/
- To set up MongoDB: https://www.mongodb.com/

### Model Configuration

Configure the LLM model in ```model.yaml``` file:
```yaml
LLM: <LLM_MODEL>
```

## 🚢 Deployment

### Docker Deployment
The application supports containerized deployment using Docker and Docker Compose for simplified orchestration.

1. Clone the repository:
```bash
git clone https://github.com/phrugsa-limbunlom/PickSmart.git
cd PickSmart
```

2. Create the network:
```bash
docker network create chatbot-network
```

3. Deploy services:
```bash
docker-compose up --build
```

The application will be accessible at `localhost:3000`.

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/phrugsa-limbunlom/PickSmart.git
cd PickSmart
```

2. Install backend dependencies:
```bash
pip install -r /chatbot-server/requirements.txt
```

3. Install frontend dependencies:
```bash
cd chatbot-app
npm install
```

4. Initialize Kafka services

5. Launch backend server:
```bash
uvicorn main:app --reload
```

6. Start frontend application:
```bash
npm start
```

## 💻 System Requirements
- Python 3.8+
- Node.js 14+
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 4 CPU cores recommended

## 📜 License
PickSmart is released under the MIT License. See the [LICENSE](https://github.com/phrugsa-limbunlom/PickSmart/blob/main/LICENSE) file for more details.
