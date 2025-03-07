import logging
import os
import time

from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

logger = logging.getLogger(__name__)

class VectorStoreService:

    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model

    def load_vector_store(self, urls):
        # embedding
        logger.info("Creating Embedding")
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        logger.info("Finish creating Embedding")

        vector_retrievers = {}
        for url in urls:
            domain = url.replace("https://www.", "").split('.')[0]

            loader = WebBaseLoader([url])
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = text_splitter.split_documents(documents)

            current_dir = os.path.dirname(os.path.abspath(__file__))

            persistent_directory = os.path.join(current_dir, "db", f"chroma_db_{domain}")

            if not os.path.exists(persistent_directory):
                logger.info(f"Creating vector store : {persistent_directory}")
                Chroma.from_documents(docs, embeddings, persist_directory=persistent_directory)
                logger.info(f"Finish creating vector store : {persistent_directory}")
            else:
                logger.info(f"Vector store : {persistent_directory} already exists")

            logger.info(f"Loading the existing vector store from {persistent_directory}")

            vector_store = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

            vector_retriever = vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 3, "score_threshold": 0.5}
            )

            vector_retrievers.update({domain: vector_retriever})

        return vector_retrievers

    def create_vector_index(self, uri, db):

        client = MongoClient(uri)

        collection_name = "embedded_picksmart"
        collection = db.get_collection(collection_name)

        collection_list = db.list_collection_names()

        for collection in collection_list:
            if collection == collection_name:
                logger.info(f"Collection '{collection}' already exists. Skip creating vector index.")
                client.close()
            return client

        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": "product_title_embedding",
                        "numDimensions": 1024,
                        "similarity": "cosine",
                        "quantization": "scalar"
                    }
                ]
            },
            name="pick_smart_vector_index",
            type="vectorSearch",
        )
        result = collection.create_search_index(model=search_index_model)
        logger.info("New search index named " + result + " is building.")

        # Wait for initial sync to complete
        logger.info("Polling to check if the index is ready. This may take up to a minute.")

        predicate = None
        if predicate is None:
            predicate = lambda index: index.get("queryable") is True
        while True:
            indices = list(collection.list_search_indexes(result))
            if len(indices) and predicate(indices[0]):
                break
            time.sleep(5)

        logger.info(result + " is ready for querying.")

        client.close()

        return client