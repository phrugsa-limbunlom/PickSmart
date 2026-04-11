<h1 align="center"> PickSmart 🛒 </h1>
<div align="center">
<img alt="Langchain" src="https://img.shields.io/badge/-Langchain-013243?style=flat&logo=langchain&logoColor=white"> <img alt="Langgraph" src="https://img.shields.io/badge/-Langgraph-013243?style=flat&logo=Langgraph&logoColor=white"> <img alt="Tavily" src="https://img.shields.io/badge/-Tavily-231F20?style=flat&logo=Tavily&logoColor=white"> <img alt="MongoDB" src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white"><img alt="Tavily" src="https://img.shields.io/badge/-Groq-231F20?style=flat&logo=Groq&logoColor=white"><img alt="FastAPI" src="https://img.shields.io/badge/-Fastapi-009688?style=flat&logo=Fastapi&logoColor=white">
</div>
<br>
<p align="center">
AI-powered shopping assistant platform for real-time product search with contextual question-answering and personalized product recommendations empowered by the intelligent search and analyst agent:
</p>
<br>

## 🎥 Overview

![Demo](./assets/picksmart.png)

![PickSmart Demo](./assets/picksmart-demo.gif)


PickSmart is an AI-powered product discovery platform that leverages large language models and intelligent agents to provide real-time product search, contextual question-answering, and personalized product recommendations. The system integrates a Retrieval-Augmented Generation (RAG) architecture with a search agent, also known as Hybrid RAG, for product discovery across multiple e-commerce marketplaces.


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

## 🛠️ Tech Stack
- **Frontend**: React, Vite
- **Backend**: FastAPI
- **Build Tool**: Vite (migrated from CRA)
- **Containerization**: Docker
- **RAG System**: LangChain, MongoDB (vector store)
- **Agents**: LangGraph, Tavily (search)

## 📐System Architecture

PickSmart employs a modern distributed architecture that combines frontend and backend services through containerized deployment. The system is designed for scalability, maintainability, and real-time responsiveness.

### Frontend Layer
- **Framework**: React.js with TypeScript
- **State Management**: Redux for predictable state container
- **API Integration**: Axios for HTTP client
- **Styling**: Custom CSS with modern SaaS design principles

### Backend Services
- **API Framework**: FastAPI with asynchronous request handling and high-performance routing
- **Vector Store**: MongoDB for efficient similarity search and embedding storage
- **Search Engine**: Tavily API integration for real-time and accurate web search capabilities

### AI Components
- **LLM Integration**: Groq API for high-performance inference
- **Agent Framework**: LangChain for composable AI components
- **Workflow Orchestration**: LangGraph for agent coordination and planning
- **RAG System**: MongoDB for vector index implementation and semantic retrieval

### Agent Workflow

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

This project contains a Vite React frontend and a FastAPI backend.

```bash
PickSmart
├── docker-compose.yaml             # Multi-service local deployment
├── LICENSE                         # Project license
├── README.md                       # Project documentation
├── assets                          # Demo images and screenshots
├── chatbot-app                     # Frontend application (React + Vite)
│   ├── Dockerfile                  # Frontend container definition
│   ├── index.html                  # Vite HTML entry point
│   ├── package.json                # Frontend dependencies and scripts
│   ├── vite.config.js              # Vite runtime configuration
│   ├── public                      # Public static assets
│   │   ├── index.html              # Root HTML template
│   │   ├── manifest.json           # PWA manifest
│   │   └── robots.txt              # SEO robots file
│   └── src                         # Frontend source code
│       ├── App.css                 # Main UI styles
│       ├── App.jsx                 # Main app component
│       ├── App.test.js             # Frontend test file
│       ├── index.css               # Global styles
│       ├── main.jsx                # React entry point
│       ├── reportWebVitals.js      # Performance monitoring helper
│       └── setupTests.js           # Jest test configuration
└── chatbot-server                  # Backend application (FastAPI)
    ├── Dockerfile                  # Backend container definition
    ├── model.yaml                  # LLM model configuration
    ├── requirements.txt            # Python dependencies
    ├── __init__.py
    └── src                         # Backend source code
        ├── __init__.py
        ├── config.py               # Application configuration
        ├── main.py                 # FastAPI entry point
        ├── adapters                # External service integrations
        │   ├── model_provider.py   # LLM provider bridge
        │   ├── llm/                # Language model adapters
        │   │   └── groq_provider.py
        │   ├── search/             # Search engine adapters
        │   │   └── tavily_provider.py
        │   └── vector/             # Vector database adapters
        │       └── mongodb_provider.py
        ├── api                     # REST API endpoints
        │   ├── routes.py           # API route definitions
        │   └── vector_search.py    # Vector search endpoints
        ├── interfaces              # Abstract base classes
        │   ├── base.py             # Common interface
        │   ├── chat.py             # Chat interface
        │   └── vector_store.py     # Vector store interface
        ├── models                  # Data models and schemas
        │   ├── agent_models.py     # Agent state models
        │   ├── schemas.py          # Pydantic schemas
        │   └── vector_db.py        # Vector DB models
        ├── repositories            # Data access layer
        │   ├── in_memory.py        # In-memory storage
        │   └── vector_db_repository.py  # Database repository
        ├── services                # Business logic
        │   ├── chat.py             # Chat service
        │   ├── embeddings.py       # Embedding service
        │   ├── prompt_messages.py  # Prompt utilities
        │   ├── search_agent.py     # Search agent logic
        │   └── vector_store.py     # Vector store service
        └── utils                   # Utility functions
            └── file_utils.py       # File handling utilities
```
   
## ⚙️ Configuration

### Environment Variables
Create ```.env.local``` file under ```chatbot-app```  and add following host to connect to your local host

```env
VITE_BACKEND_URL=http://localhost:8000
```

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

- **Docker**: Multi-service orchestration with Docker Compose
- **Environment Variables**: Managed via `.env` files, using `VITE_BACKEND_URL` for frontend-backend communication

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
4. Launch backend server:
```bash
uvicorn src.main:app --reload --env-file .env
```
5. Start frontend application:
```bash
npm run dev
```

## 💻 System Requirements
- Python 3.8+
- Node.js 14+
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 4 CPU cores recommended

## � Getting Started

### Quick Start with Docker

The fastest way to get PickSmart running is with Docker Compose

1. Clone the repository and navigate to the project
   ```bash
   git clone https://github.com/phrugsa-limbunlom/PickSmart.git
   cd PickSmart
   ```

2. Set up your environment variables (see Configuration section)

3. Start all services
   ```bash
   docker-compose up --build
   ```

4. Access the application
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📚 API Documentation

The PickSmart backend provides comprehensive REST API documentation through Swagger UI. Once the backend is running, navigate to `http://localhost:8000/docs` to explore all available endpoints.

Key API endpoints

- `POST /api/chat` - Submit a product query and receive AI-powered responses
- `GET /api/health` - Check backend service health
- `POST /api/vector-search` - Perform direct vector similarity searches

## 🔧 Development

### Backend Development

To develop the backend without Docker

1. Install Python dependencies
   ```bash
   pip install -r chatbot-server/requirements.txt
   ```

2. Set up your `.env` file in the `chatbot-server` directory

3. Run the FastAPI development server
   ```bash
   cd chatbot-server
   uvicorn src.main:app --reload --env-file .env
   ```

The server will start with hot-reload enabled for development.

### Frontend Development

To develop the frontend with live reload

1. Install Node dependencies
   ```bash
   cd chatbot-app
   npm install
   ```

2. Set up your `.env.local` file with the backend URL

3. Start the development server
   ```bash
   npm run dev
   ```

## 🐛 Troubleshooting

### Docker Compose fails to start

If you encounter exit code 1 when running Docker Compose

- Verify all required environment variables are set in `.env` files
- Ensure the MongoDB connection string is valid
- Check that required API keys are active and have proper permissions
- Run `docker-compose logs` to view detailed error messages

### Backend cannot connect to MongoDB

- Verify MongoDB credentials in the `.env` file
- Ensure MongoDB Atlas network access includes your IP
- Test the connection string independently
- Check that the `MONGO_DATABASE` environment variable matches an existing database

### Frontend cannot reach backend

- Ensure `VITE_BACKEND_URL` in `.env.local` matches your backend URL
- Verify the backend service is running and accessible
- Check browser console for CORS errors
- Confirm the backend is listening on the correct port

### API Keys not working

- Verify API keys are correctly copied without extra spaces
- Check that API keys have the necessary permissions in their respective services
- Ensure API keys are not expired or revoked
- Confirm rate limits have not been exceeded

## 📜 License
PickSmart is released under the MIT License. See the [LICENSE](https://github.com/phrugsa-limbunlom/PickSmart/blob/main/LICENSE) file for more details.