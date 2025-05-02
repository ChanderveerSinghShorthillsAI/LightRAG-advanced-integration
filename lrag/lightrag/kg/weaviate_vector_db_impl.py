import weaviate
from weaviate.exceptions import WeaviateBaseError
from weaviate.auth import AuthApiKey
from dataclasses import dataclass
from dotenv import load_dotenv
from weaviate.classes.config import DataType 
from or_lib.base import BaseKVStorage, BaseVectorStorage  
from weaviate.classes.query import Filter, MetadataQuery
from logging import getLogger
import asyncio
import numpy as np
import os
import weaviate.classes as wvc

from app.utils.aws.s3manager  import S3Manager
from app.core.settings import settings  # Adjusted import path
import json 

load_dotenv()
logger = getLogger("weaviate-vectordb")

@dataclass
class WeaviateDBBase:
    """Base class for WeaviateDB storage handling shared initialization."""

    def __post_init__(self):
        self.weaviate_url = os.getenv("WEAVIATE_URL")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        self.embedding_dimensions = int(os.getenv("WEAVIATE_EMBEDDING") or 768)
        print(self.weaviate_url)
        print(self.api_key)
        print(self.embedding_dimensions)

        logger.info(f"WEAVIATE_URL: {self.weaviate_url}, EMBEDDING_DIMENSIONS: {self.embedding_dimensions}")

        if not all([self.weaviate_url, self.api_key, self.embedding_dimensions]):
            raise ValueError("Weaviate URL, API Key, and Embedding Dimensions are required.")

        self._client = self._get_or_create_collection()
        self._max_batch_size = int(os.getenv("EMBEDDING_BATCH_NUM") or 100)

    def _get_client(self):
        try:
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.weaviate_url,
                auth_credentials=AuthApiKey(self.api_key),
                skip_init_checks=True  
            )
            print(client)
            print("naruto")
            if not client.is_ready():
                print("not ready")
                raise WeaviateBaseError("Client is not ready")
            
            logger.info("✅ Successfully connected to Weaviate Cloud!")
            return client

        except WeaviateBaseError as e:
            logger.error(f"Failed to connect to Weaviate Cloud: {e}")
            raise

    def _get_or_create_collection(self):
        """Retrieve or create a collection in Weaviate."""
        client = self._get_client()
        # if self._client is None:
        #     self._client = self._get_client()
        existing_collections = client.collections.list_all()

        if self.namespace and self.namespace.lower():
            existing_collections = [col.lower() for col in existing_collections]
            if self.namespace.lower() not in existing_collections:
                client.collections.create(
                    name=self.namespace,
                    properties=[{"name": "content", "data_type": DataType.TEXT}], 
                    vectorizer_config=None,  
                )

        return client


class WeaviateDBKVStorage(BaseKVStorage, WeaviateDBBase):
    """Weaviate Key-Value Storage Implementation."""

    async def all_keys(self) -> list[str]:
        try:
            result = self._client.collections.get(self.namespace).query.fetch_objects(
                include_properties=["_id"]
            )
            return [obj["_id"] for obj in result.objects]
        except Exception as e:
            logger.error(f"Error retrieving all keys: {e}")
            return []

    async def get_by_id(self, id: str):
        try:
            return self._client.collections.get(self.namespace).data.get_object_by_id(id) or None
        except Exception as e:
            logger.error(f"Error retrieving ID {id}: {e}")
            return None

    async def filter_keys(self, data: list[str]) -> set[str]:
        return {chunk_id for chunk_id in data if not self._client.collections.get(self.namespace).data.get_object_by_id(chunk_id)}

    async def upsert(self, data: dict[str, dict]):
        if not data:
            return

        collection = self._client.collections.get(self.namespace)

        for key, value in data.items():
            collection.data.insert(
                properties={"content": value["content"]},
                uuid=key
            )

    async def drop(self):
        self._client.collections.delete(self.namespace)

    async def index_done_callback(self):
        self._client.close()

    async def get_by_ids(self, ids: list[str]):
        try:
            results = self._client.collections.get(self.namespace).data.get_objects_by_ids(ids)
            return [result for result in results if result is not None]
        except Exception as e:
            logger.error(f"Error retrieving IDs {ids}: {e}")
            return []
    async def get_docs_by_status(self, status: str):
        pass
    async def close(self):
        if hasattr(self, '_client') and self._client is not None:
            self._client.close()

from dataclasses import dataclass, field
from typing import Any

@dataclass(unsafe_hash=True)
class WeaviateDBVectorStorage(BaseVectorStorage, WeaviateDBBase):
    

    
    async def upsert(self, data: dict[str, dict]):
        if not data:
            logger.warning("Attempted to insert empty data into vector DB.")
            return []

        logger.info(f"Inserting {len(data)} vectors into {self.namespace} in Weaviate.")
        
        formatted_data = [
            {
                "__id__": k,
                **{k1: v1 for k1, v1 in v.items()},
            }
            for k, v in data.items()
        ]
        contents = [v["content"] for v in formatted_data]

        # Batch process embeddings
        logger.info(f"[DEBUG] Generating embeddings for {len(contents)} chunks")
        batches = [contents[i: i + self._max_batch_size] for i in range(0, len(contents), self._max_batch_size)]
        embeddings_list = await asyncio.gather(*[self.embedding_func(batch) for batch in batches])
        embeddings = np.concatenate(embeddings_list)
        logger.info(f"[DEBUG] Generated {len(embeddings)} embeddings")

        collection = self._client.collections.get(self.namespace)

        try:
            with collection.batch.dynamic() as batch:
                for i, data_row in enumerate(formatted_data):
                    batch.add_object(
                        properties=data_row,
                        vector=embeddings[i].tolist()
                    )
        except Exception as e:
            logger.error(f"Failed to upload data to Weaviate: {e}")

        
        return formatted_data
       
    async def upsert_with_centroid(self, data: dict[str, dict]):
        if not data:
            logger.warning("Attempted to insert empty data into vector DB.")
            return []

        logger.info(f"Inserting {len(data)} vectors into {self.namespace} in Weaviate.")

        formatted_data = [
            {
                "__id__": k,
                **{k1: v1 for k1, v1 in v.items()},
            }
            for k, v in data.items()
        ]
        contents = [v["content"] for v in formatted_data]

        # Batch process embeddings
        batches = [contents[i: i + self._max_batch_size] for i in range(0, len(contents), self._max_batch_size)]
        embeddings_list = await asyncio.gather(*[self.embedding_func(batch) for batch in batches])
        embeddings = np.concatenate(embeddings_list)

        collection = self._client.collections.get(self.namespace)

        try:
            with collection.batch.dynamic() as batch:
                for i, data_row in enumerate(formatted_data):
                    batch.add_object(
                        properties=data_row,
                        vector=embeddings[i].tolist()
                    )
        except Exception as e:
            logger.error(f"Failed to upload data to Weaviate: {e}")

        # Fetch existing centroid from S3
        logger.info("Fetching existing centroid from S3...")
        bucket_name = settings.aws_s3_bucket_name
        client = S3Manager(bucket_name)
        centroid_key = "centroids/databases.json"

        try:
            response = client.get_object(centroid_key)
            centroid_data = json.loads(response.decode("utf-8"))

            if "databases" not in centroid_data:
                centroid_data = {"databases": {}}

            if "weaviate" in centroid_data["databases"]:
                old_centroid = np.array(centroid_data["databases"]["weaviate"]["centroid"])
                old_embeddings_count = centroid_data["databases"]["weaviate"]["num_embeddings"]
                logger.info("Fetched existing centroid for Weaviate with %d embeddings", old_embeddings_count)
            else:
                logger.info("No existing centroid found for Weaviate, initializing new centroid")
                old_centroid = None
                old_embeddings_count = 0
        except Exception as e:
            if "does not exist" in str(e):
                logger.info("No existing centroid file found, initializing new structure")
                centroid_data = {"databases": {}}
                old_centroid = None
                old_embeddings_count = 0
            else:
                raise

        # Compute new centroid
        logger.info("Computing new centroid...")
        new_embeddings_count = len(embeddings)
        if old_centroid is not None and old_embeddings_count > 0:
            sum_old_embeddings = old_centroid * old_embeddings_count
            sum_new_embeddings = np.sum(embeddings, axis=0)
            total_embeddings_count = old_embeddings_count + new_embeddings_count
            updated_centroid = (sum_old_embeddings + sum_new_embeddings) / total_embeddings_count
        else:
            updated_centroid = np.mean(embeddings, axis=0)
            total_embeddings_count = new_embeddings_count

        self.centroid = updated_centroid

        # Update the Weaviate entry in databases.json
        centroid_data["databases"]["weaviate"] = {
            "centroid": updated_centroid.tolist(),
            "num_embeddings": total_embeddings_count
        }

        # Upload updated centroid data back to S3
        client.put_object(
            centroid_key,
            json.dumps(centroid_data, indent=4, ensure_ascii=False).encode("utf-8")
        )
        logger.info("Centroid for Weaviate successfully updated in S3")

        

        return formatted_data
    
    async def query(self, query: str, top_k=5, ids=None):
        logger.info(f"[DEBUG] Querying Weaviate with query: {query}, top_k: {top_k}")
        try:
            
            if not self._client.is_ready():
                logger.info("Weaviate client is closed or not ready. Reconnecting...")
                self._client = self._get_client()
                
            embedding = await self.embedding_func([query])
            logger.info(f"[DEBUG] Generated query embedding: {embedding[0][:10]}...")

            if embedding is None or not isinstance(embedding, (list, np.ndarray)) or len(embedding) == 0:
                raise ValueError("Embedding function returned an empty or invalid embedding.")

            # Ensure embedding is a 1D list
            if isinstance(embedding, np.ndarray):
                embedding = embedding.squeeze().tolist()  # Convert NumPy array to list
            elif isinstance(embedding, list) and len(embedding) > 0:
                embedding = embedding[0] if isinstance(embedding[0], list) else embedding

            if not isinstance(embedding, list) or not all(isinstance(i, (float, int)) for i in embedding):
                raise ValueError("Final embedding is not a valid list of floats.")

            collection = self._client.collections.get(self.namespace)
            result = collection.query.near_vector(
                near_vector=embedding,
                limit=top_k,
                return_metadata=MetadataQuery(distance=True)
            )
            logger.info(f"[DEBUG] Weaviate query returned {len(result.objects)} objects")
            if not hasattr(result, "objects") or not isinstance(result.objects, list):
                return []  

            response = []
            for res in result.objects:
                if hasattr(res, "uuid") and hasattr(res, "metadata") and hasattr(res.metadata, "distance"):
                    response.append({
                        "id": str(res.uuid),  
                        "distance": res.metadata.distance,
                        "$similarity":res.metadata.distance,
                        **res.properties
                    })
            logger.info(f"[DEBUG] Processed {len(response)} query results")
            return response

        except Exception as e:
            logger.error(f"Error in query: {e}")
            return []

    async def index_done_callback(self):
        logger.info("Index done callback called, keeping Weaviate client open.")
        # await self.close()


    async def close(self):
        if hasattr(self, '_client') and self._client is not None:
            self._client.close()

    async def delete_entity(self, entity_id: str):
        """Delete an entity from Weaviate by ID."""
        collection = self._client.collections.get(self.namespace)
        try:
            collection.data.delete(entity_id)
            logger.info(f"Deleted entity {entity_id} from {self.namespace}")
        except Exception as e:
            logger.error(f"Failed to delete entity {entity_id}: {e}")

    async def delete_entity_relation(self, entity_id: str, relation: str):
        """Delete a relation from an entity."""
        logger.warning("delete_entity_relation method is not implemented.")
        raise NotImplementedError("delete_entity_relation method is not implemented.")

    async def get_by_id(self, entity_id: str):
        """Retrieve an entity by ID."""
        collection = self._client.collections.get(self.namespace)
        try:
            return collection.data.get_by_id(entity_id)
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            return None

    async def get_by_ids(self, entity_ids: list):
        """Retrieve multiple entities by their IDs."""
        collection = self._client.collections.get(self.namespace)
        try:
            return collection.data.get_many(entity_ids)
        except Exception as e:
            logger.error(f"Failed to get entities {entity_ids}: {e}")
            return None
