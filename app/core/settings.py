from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "OptimizeRAG API Service"

    # ARYN
    aryn_api_key: str = "dummy"

    # AWS
    aws_access_key_id: str = "dummy"
    aws_secret_access_key: str = "dummy"
    aws_s3_bucket_name: str = "dummy"
    aws_region: str = "us-east-1"
    aws_default_region: str = "us-east-1"

    # Azure
    azure_openai_endpoint: str = "https://dummy.openai.azure.com/"
    azure_openai_api_key: str = "dummy"
    azure_openai_api_version: str = "2023-05-15"
    azure_openai_deployment: str = "gpt-4"
    azure_embedding_deployment: str = "embedding-model"
    azure_embedding_api_version: str = "2023-05-15"
    azure_document_intelligence_api_key: str = "dummy"
    azure_document_intelligence_endpoint: str = "https://dummy-docai.azure.com/"

    # Llama
    llama_cloud_api_key: str = "dummy"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # NEO4J
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""

    # ASTRA DB
    astradb_application_token: str = "dummy"
    astradb_api_endpoint: str = "https://dummy-astra.io"
    astradb_embedding_dimensions: int = 1536

    # WEAVIATE DB
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: str = "dummy"
    weaviate_embedding: int = 1536

    # Teams
    teams_webhook_url: str = "https://dummy-teams-webhook"

    # MongoDB
    connection_string: str = "mongodb://localhost:27017"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()