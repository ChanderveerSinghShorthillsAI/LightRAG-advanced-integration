# def initialize_embedding(embedding_model:None, llm_provider: str):
#     """Initialize the embedding function."""
#     # logger.info(f"Embedding model handler: {embedding_model}")
    
#     if embedding_model:
#         llm_provider = llm_provider
#         embedding_dim = DEFAULT_EMBEDDING_DIM_LIST.get(embedding_model, None)
#         if(embedding_dim is None):
#             raise ValueError(f"Unsupported embedding model: {embedding_model}")
        
#     else:
#         llm_provider = DEFAULT_LLM_PROVIDER
#         embedding_dim = DEFAULT_EMBEDDING_DIM  # 1536 for Azure OpenAI
#         embedding_model_name = embedding_model if embedding_model else DEFAULT_EMBEDDING_MODEL

    
#     logger.info(f"Using embedding dimension: {embedding_dim} for provider: {llm_provider}")
#     return EmbeddingFunc(
#         embedding_dim=embedding_dim,
#         max_token_size=DEFAULT_MAX_TOKEN_SIZE,
#         func=get_embedding_func(llm_provider),
#     )

import logging

# Dummy/default values for demonstration
DEFAULT_EMBEDDING_DIM_LIST = {
    "nomic-embed-text": 768,
    "openai-ada": 1536,
    "azure-openai": 1536,
}
DEFAULT_EMBEDDING_DIM = 768
DEFAULT_LLM_PROVIDER = "ollama"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_MAX_TOKEN_SIZE = 8192

logger = logging.getLogger("lightrag")

# Dummy EmbeddingFunc and get_embedding_func for demonstration
class EmbeddingFunc:
    def __init__(self, embedding_dim, max_token_size, func):
        self.embedding_dim = embedding_dim
        self.max_token_size = max_token_size
        self.func = func

def get_embedding_func(provider):
    # Return a dummy embedding function for demonstration
    return lambda texts: [0.0] * DEFAULT_EMBEDDING_DIM

def initialize_embedding(embedding_model=None, llm_provider: str = DEFAULT_LLM_PROVIDER):
    """Initialize the embedding function."""
    if embedding_model:
        embedding_dim = DEFAULT_EMBEDDING_DIM_LIST.get(embedding_model, None)
        if embedding_dim is None:
            raise ValueError(f"Unsupported embedding model: {embedding_model}")
    else:
        llm_provider = DEFAULT_LLM_PROVIDER
        embedding_dim = DEFAULT_EMBEDDING_DIM
        embedding_model = DEFAULT_EMBEDDING_MODEL

    logger.info(f"Using embedding dimension: {embedding_dim} for provider: {llm_provider}")
    return EmbeddingFunc(
        embedding_dim=embedding_dim,
        max_token_size=DEFAULT_MAX_TOKEN_SIZE,
        func=get_embedding_func(llm_provider),
    )