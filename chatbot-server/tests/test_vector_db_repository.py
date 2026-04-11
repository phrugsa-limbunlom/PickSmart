from types import SimpleNamespace

from src.repositories.vector_db_repository import VectorDBRepository


class FakeCollection:
    def __init__(self):
        self.created = False
        self.search_indexes = []
        self.created_model = None

    def list_search_indexes(self, name=None):
        if name is None:
            return self.search_indexes
        return [idx for idx in self.search_indexes if idx.get("name") == name]

    def create_search_index(self, model):
        self.created_model = model
        self.search_indexes.append({"name": model.name, "queryable": True})
        return model.name


class FakeMongoDB:
    def __init__(self):
        self.collections = {}

    def list_collection_names(self):
        return list(self.collections.keys())

    def create_collection(self, name):
        self.collections[name] = FakeCollection()

    def get_collection(self, name):
        if name not in self.collections:
            self.collections[name] = FakeCollection()
        return self.collections[name]


def test_initialize_creates_collection_and_index(monkeypatch) -> None:
    mongo_db = FakeMongoDB()
    repo = VectorDBRepository(mongo_db)

    monkeypatch.setattr(repo, "_wait_for_index", lambda collection, index_name: None)

    repo.initialize()

    collection = mongo_db.get_collection(repo.collection_name)
    assert collection.created_model is not None


def test_create_vector_index_skips_existing(monkeypatch) -> None:
    mongo_db = FakeMongoDB()
    repo = VectorDBRepository(mongo_db)
    collection = mongo_db.get_collection(repo.collection_name)
    collection.search_indexes = [{"name": repo.index_name}]

    monkeypatch.setattr(repo, "_wait_for_index", lambda collection, index_name: None)

    repo.create_vector_index()

    assert collection.created_model is None
