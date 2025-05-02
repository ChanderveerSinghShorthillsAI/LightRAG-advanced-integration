from core.settings import settings


def get_weaviate_vector_db_storage_kwargs():
    return {
        "WEAVIATE_URL": settings.weaviate_url,
        "WEAVIATE_API_KEY": settings.weaviate_api_key,
        "EMBEDDING_DIMENSIONS": settings.weaviate_embedding,
    }

    