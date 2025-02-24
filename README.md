<h1 align="center"> PickSmart 🛒 </h1>
<div align="center">
<img alt="Langchain" src="https://img.shields.io/badge/-Langchain-013243?style=flat&logo=langchain&logoColor=white"> <img alt="Langgraph" src="https://img.shields.io/badge/-Langgraph-013243?style=flat&logo=Langgraph&logoColor=white"> <img alt="Tavily" src="https://img.shields.io/badge/-Tavily-231F20?style=flat&logo=Tavily&logoColor=white"> <img alt="Chroma" src="https://img.shields.io/badge/-Chroma-231F20?style=flat&logo=chroma&logoColor=white"><img alt="Tavily" src="https://img.shields.io/badge/-Groq-231F20?style=flat&logo=Groq&logoColor=white"><img alt="FastAPI" src="https://img.shields.io/badge/-Fastapi-009688?style=flat&logo=Fastapi&logoColor=white"> <img alt="Kafka" src="https://img.shields.io/badge/-Kafka-231F20?style=flat&logo=kafka&logoColor=white">
</div>
<br>
<p align="center">
AI-powered shopping assistant platform for real-time product search with contextual question-answering and personalized product recommendations empowered by the intelligent search and analyst agent:
</p>
<br>

![image](https://github.com/user-attachments/assets/3d2d0ca7-cfa9-4fec-8b2c-c802e5134411)


## 📌 Overview

PickSmart is a distributed and AI-powered product discovery platform that leverages the large language model and distributed system to provide real-time product search, contextual question-answering, and personalized product recommendations. The system integrates a Retrieval-Augmented Generation (RAG) architecture with a search agent for product discovery across multiple e-commerce marketplaces.


## 🚀 Usage
- Ask a question about a product.
- Search multiple marketplaces and rank the results.
- Receive personalized recommendations.


## ⚡Core Capabilities

- **Natural Language Query Processing**: Advanced query decomposition and semantic analysis
- **Vector Database Integration**: Efficient data ingestion and storage for embedding-based semantic retrieval.
- **Distributed Real-time Search**: Multi-marketplace product discovery with parallel processing
- **Intelligent Product Ranking**: AI-powered relevance scoring and personalization
- **Context-Aware Recommendations**: Detailed answers with product suggestions
- **Scalable Data Processing**: Event-driven architecture for high-throughput data handling


## 🎥 Demo


https://github.com/user-attachments/assets/47f57b9d-7c8b-4d37-8943-06d1eba58961



## 🛠️ Tech Stack
- **Frontend**: React
- **Backend**: FastAPI
- **Streaming**: Kafka
- **RAG System**: LangChain, Chroma (vector store)
- **Agents**: LangGraph, Tavily (search)
- **API Client**: Groq API


## 📐Technical Architecture

### Frontend Layer
- **Framework**: React.js with TypeScript
- **State Management**: Redux for predictable state container
- **API Integration**: Axios for HTTP client

### Backend Services
- **API Framework**: FastAPI with asynchronous request handling and high-performance routing
- **Message Broker**: Apache Kafka for event streaming and distributed processing
- **Vector Store**: Chroma DB for efficient similarity search and embedding storage
- **Search Engine**: Tavily API integration for enhanced web search capabilities

### AI Components
- **LLM Integration**: Groq API for high-performance inference
- **Agent Framework**: LangChain for composable AI components
- **Workflow Orchestration**: LangGraph for agent coordination and planning
- **Embedding Models**: Support for multiple embedding architectures
- **RAG System**: Custom implementation with semantic caching

### Agent Architecture

The system implements a search and analyze agent with a multi-step workflow using LangGraph for orchestration:

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

Agent responsibilities include:
1. **Query Analysis Agent**: Semantic decomposition and intent classification
2. **Search Orchestration Agent**: Distributed marketplace search coordination
3. **Ranking Agent**: Multi-criteria product evaluation and scoring
4. **E-commerce Discovery Agent**: Discovery product sources across multiple e-commerce platforms to provide direct purchase links
   
## ⚙️ Configuration

### Environment Variables
Create ```.env``` file under ```chatbot-server``` folder and add API keys as below:

```env
GROQ_API_KEY="<API_KEY>"
TAVILY_API_KEY="<API_KEY>"
```
- To get Groq api key: https://console.groq.com/keys
- To get Tavily api key: https://tavily.com/

### Model Configuration

Configure the LLM model and Embedding models in ```model.yaml``` file:
```yaml
LLM: <LLM_MODEL>
EMBEDDING: <EMBEDDING_MODEL>
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
