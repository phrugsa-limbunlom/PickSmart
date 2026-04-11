from types import SimpleNamespace

from src.services.vector_store import VectorStoreService


class FakeEmbeddings:
    def embed_text(self, text: str):
        return [0.1, 0.2]


class FakeCollection:
    def __init__(self):
        self.pipeline = None
        self.inserted = []
        self.deleted = []

    def aggregate(self, pipeline):
        self.pipeline = pipeline
        return [{"similarityScore": 0.9, "document": {"id": 1}}]

    def insert_one(self, vector_data):
        self.inserted.append(vector_data)
        return SimpleNamespace(inserted_id="abc")

    def delete_one(self, query):
        self.deleted.append(query)
        return SimpleNamespace(deleted_count=1)


class FakeRepo:
    def __init__(self, collection):
        self.collection = collection

    def get_collection(self):
        return self.collection


class ErrorCollection(FakeCollection):
    def aggregate(self, pipeline):
        raise RuntimeError("boom")


def test_search_similar_builds_pipeline() -> None:
    collection = FakeCollection()
    service = VectorStoreService(vector_db_repo=FakeRepo(collection), embeddings_service=FakeEmbeddings())

    results = service.search_similar(query="shoe", top_k=2, department="d1", region="r1")

    assert results == [{"similarityScore": 0.9, "document": {"id": 1}}]
    assert collection.pipeline is not None
    assert collection.pipeline[-1]["$match"] == {"department": "d1", "region": "r1"}


def test_insert_vector_returns_id() -> None:
    collection = FakeCollection()
    service = VectorStoreService(vector_db_repo=FakeRepo(collection), embeddings_service=FakeEmbeddings())

    result = service.insert_vector({"field": "value"})

    assert result == "abc"


def test_delete_document(monkeypatch) -> None:
    collection = FakeCollection()
    service = VectorStoreService(vector_db_repo=FakeRepo(collection), embeddings_service=FakeEmbeddings())

    monkeypatch.setattr("src.services.vector_store.ObjectId", lambda value: value)

    result = service.delete_document("doc-id")

    assert result is True
    assert collection.deleted == [{"_id": "doc-id"}]


def test_search_similar_handles_error() -> None:
    collection = ErrorCollection()
    service = VectorStoreService(vector_db_repo=FakeRepo(collection), embeddings_service=FakeEmbeddings())

    results = service.search_similar(query="shoe")

    assert results == []
