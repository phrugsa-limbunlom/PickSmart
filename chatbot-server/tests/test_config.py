from types import SimpleNamespace

from src import config as config_module


class FakeModelProvider:
    def __init__(self, path: str):
        self.path = path

    def get_model_name(self) -> str:
        return "model-x"


class FakeGroqProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key


class FakeMongoProvider:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_database(self):
        return SimpleNamespace(name="db")


class FakeVectorRepo:
    def __init__(self, mongo_db):
        self.mongo_db = mongo_db

    def initialize(self):
        return None


class FakeEmbeddings:
    def __init__(self, provider_type: str):
        self.provider_type = provider_type


class FakeVectorStoreService:
    def __init__(self, vector_db_repo, embeddings_service):
        self.vector_db_repo = vector_db_repo
        self.embeddings_service = embeddings_service


class FakeHybridSearch:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeSourceSearch:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeChatService:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_config_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("TAVILY_API_KEY", "t")
    monkeypatch.setenv("COHERE_API_KEY", "c")
    monkeypatch.setenv("MONGO_DB_USERNAME", "u")
    monkeypatch.setenv("MONGO_DB_PASSWORD", "p")
    monkeypatch.setenv("MONGO_DB_CLUSTER", "cl")
    monkeypatch.setenv("MONGO_DB_NAME", "db")

    cfg = config_module.Config()

    assert cfg.groq_api_key == "g"
    assert cfg.tavily_api_key == "t"
    assert cfg.cohere_api_key == "c"
    assert cfg.mongo_username == "u"
    assert cfg.mongo_password == "p"
    assert cfg.mongo_cluster == "cl"
    assert cfg.mongo_database == "db"


def test_dependency_container_builds_services(monkeypatch) -> None:
    monkeypatch.setattr(config_module, "CustomModelProvider", FakeModelProvider)
    monkeypatch.setattr(config_module, "default_model_path", lambda: "model.yaml")
    monkeypatch.setattr(config_module, "GroqProvider", FakeGroqProvider)
    monkeypatch.setattr(config_module, "MongoDBVectorProvider", FakeMongoProvider)
    monkeypatch.setattr(config_module, "VectorDBRepository", FakeVectorRepo)
    monkeypatch.setattr("src.services.embeddings.EmbeddingsService", FakeEmbeddings)
    monkeypatch.setattr(config_module, "VectorStoreService", FakeVectorStoreService)
    monkeypatch.setattr(config_module, "TavilyHybridSearchProvider", FakeHybridSearch)
    monkeypatch.setattr(config_module, "TavilySourceSearchProvider", FakeSourceSearch)
    monkeypatch.setattr(config_module, "ChatService", FakeChatService)

    container = config_module.DependencyContainer()

    assert container.llm_client.api_key == container.config.groq_api_key
    assert container.vector_store.vector_db_repo.mongo_db.name == "db"

    chat_service = container.get_chat_service()
    assert isinstance(chat_service, FakeChatService)


def test_get_dependency_container_is_singleton(monkeypatch) -> None:
    monkeypatch.setattr(config_module, "DependencyContainer", lambda: "instance")
    if hasattr(config_module.get_dependency_container, "_instance"):
        delattr(config_module.get_dependency_container, "_instance")

    first = config_module.get_dependency_container()
    second = config_module.get_dependency_container()

    assert first == "instance"
    assert second == "instance"
