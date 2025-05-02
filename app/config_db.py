# from app.db.astradb.base_astra import get_astra_vector_db_storage_kwargs
from base_weaviate import get_weaviate_vector_db_storage_kwargs

from app.utils.aws.s3manager import S3Manager
from app.core.settings import settings
import numpy as np
import json
import asyncio
# from utils.logger import logger

def get_vector_db_kwargs_for_store_class(vector_store_class):
    try:
        store_mapping = {
            # "AstraDBVectorStorage": get_astra_vector_db_storage_kwargs,
            "WeaviateDBVectorStorage": get_weaviate_vector_db_storage_kwargs
        }
    
        return store_mapping.get(vector_store_class)()
    except KeyError:
        raise ValueError(f"Unsupported vector store class: {vector_store_class}")


def get_db_storage_class(storage_value, default_storage, config_class):
    # Config class will come.
    if storage_value != default_storage and config_class.validate_storage_db(storage_value):
        return config_class.get_db_class(storage_value)
    else:
        return storage_value
    
async def get_route(query, storage_value, default_storage, config_class, llm_model_name):
    if storage_value != default_storage and config_class.validate_storage_db(storage_value):
        from handler import initialize_embedding #to fix circular imports problem

        # logger.info("Calculating closest database for query routing...")
        embedding_func = initialize_embedding(llm_model_name)
        # Generate embedding for the query
        embeddings_list = await asyncio.gather(
            embedding_func([query])  # Ensure query is passed as a list
        )

    # ✅ Flatten the embedding result
        query_embedding = np.concatenate(embeddings_list).flatten()
        
        # Fetch centroid data from S3
        bucket_name = settings.aws_s3_bucket_name
        client = S3Manager(bucket_name)
        centroid_key = "centroids/databases.json"
        
        try:
            response = client.get_object(centroid_key)
            centroid_data = json.loads(response.decode("utf-8"))
        except Exception as e:
            # logger.error(f"Failed to fetch centroid data: {e}")
            return default_storage
        
        if "databases" not in centroid_data or not centroid_data["databases"]:
            # logger.warning("No centroid data found, using default storage.")
            return default_storage
        
        # Compute distances to each centroid
        min_distance = float("inf")
        closest_db = default_storage
        
        for db_name, db_info in centroid_data["databases"].items():
            centroid = np.array(db_info["centroid"])
            distance = np.linalg.norm(query_embedding - centroid)
            
            if distance < min_distance:
                min_distance = distance
                closest_db = db_name
        # logger.info("This is the routed vector storage: %s", config_class.get_db_class(closest_db))
        return config_class.get_db_class(closest_db)
    else:
        # logger.info("This is the routed vector storage: %s", storage_value)
        return storage_value