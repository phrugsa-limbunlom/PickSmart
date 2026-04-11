from src.adapters.vector.mongodb_provider import MongoDBVectorProvider


class FakeMongoClient:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.admin = self
        self._db = {}

    def command(self, name: str):
        return {"ok": 1}

    def __getitem__(self, name: str):
        return {"name": name}


def test_mongodb_provider_creates_uri_and_client(monkeypatch) -> None:
    def fake_client(*args, **kwargs):
        return FakeMongoClient(*args, **kwargs)

    monkeypatch.setattr("src.adapters.vector.mongodb_provider.MongoClient", fake_client)

    provider = MongoDBVectorProvider(
        username="user",
        password="pass",
        cluster="cluster",
        database="db",
    )

    db = provider.get_database()

    assert db["name"] == "db"
    assert "mongodb+srv://" in provider._uri
