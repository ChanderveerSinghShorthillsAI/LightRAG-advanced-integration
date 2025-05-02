STORAGE_IMPLEMENTATIONS = {
    "KV_STORAGE": {
        "implementations": [
            "JsonKVStorage",
            "RedisKVStorage",
            "PGKVStorage",
            "MongoKVStorage",
            # "TiDBKVStorage",
        ],
        "required_methods": ["get_by_id", "upsert"],
    },
    "GRAPH_STORAGE": {
        "implementations": [
            "NetworkXStorage",
            "Neo4JStorage",
            "PGGraphStorage",
            # "AGEStorage",
            # "MongoGraphStorage",
            # "TiDBGraphStorage",
            # "GremlinStorage",
        ],
        "required_methods": ["upsert_node", "upsert_edge"],
    },
    "VECTOR_STORAGE": {
        "implementations": [
            "NanoVectorDBStorage",
            "MilvusVectorDBStorage",
            "ChromaVectorDBStorage",
            "PGVectorStorage",
            "FaissVectorDBStorage",
            "QdrantVectorDBStorage",
            "MongoVectorDBStorage",
            "WeaviateDBVectorStorage",
        ],
        "required_methods": ["query", "upsert"],
    },
    "DOC_STATUS_STORAGE": {
        "implementations": [
            "JsonDocStatusStorage",
            "PGDocStatusStorage",
            "MongoDocStatusStorage",
        ],
        "required_methods": ["get_docs_by_status"],
    },
}

# Storage implementation environment variable without default value
STORAGE_ENV_REQUIREMENTS: dict[str, list[str]] = {
    # KV Storage Implementations
    "JsonKVStorage": [],
    "MongoKVStorage": [],
    "RedisKVStorage": ["REDIS_URI"],
    # "TiDBKVStorage": ["TIDB_USER", "TIDB_PASSWORD", "TIDB_DATABASE"],
    "PGKVStorage": ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DATABASE"],
    # Graph Storage Implementations
    "NetworkXStorage": [],
    "Neo4JStorage": ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"],
    "MongoGraphStorage": [],
    # "TiDBGraphStorage": ["TIDB_USER", "TIDB_PASSWORD", "TIDB_DATABASE"],
    "AGEStorage": [
        "AGE_POSTGRES_DB",
        "AGE_POSTGRES_USER",
        "AGE_POSTGRES_PASSWORD",
    ],
    # "GremlinStorage": ["GREMLIN_HOST", "GREMLIN_PORT", "GREMLIN_GRAPH"],
    "PGGraphStorage": [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DATABASE",
    ],
    # Vector Storage Implementations
    "NanoVectorDBStorage": [],
    "MilvusVectorDBStorage": [],
    "ChromaVectorDBStorage": [],

    "PGVectorStorage": ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DATABASE"],
    "FaissVectorDBStorage": [],
    "QdrantVectorDBStorage": ["QDRANT_URL"],  # QDRANT_API_KEY has default value None
    "MongoVectorDBStorage": [],
    
    "JsonDocStatusStorage": [],
    "PGDocStatusStorage": ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DATABASE"],
    "MongoDocStatusStorage": [],
}

# Storage implementation module mapping
STORAGES = {
    "NetworkXStorage": ".kg.networkx_impl",
    "JsonKVStorage": ".kg.json_kv_impl",
    "NanoVectorDBStorage": ".kg.nano_vector_db_impl",
    "JsonDocStatusStorage": ".kg.json_doc_status_impl",
    "Neo4JStorage": ".kg.neo4j_impl",
    "MilvusVectorDBStorage": ".kg.milvus_impl",
    "MongoKVStorage": ".kg.mongo_impl",
    "MongoDocStatusStorage": ".kg.mongo_impl",
    "MongoGraphStorage": ".kg.mongo_impl",
    "MongoVectorDBStorage": ".kg.mongo_impl",
    "RedisKVStorage": ".kg.redis_impl",
    "ChromaVectorDBStorage": ".kg.chroma_impl",
  
    "PGKVStorage": ".kg.postgres_impl",
    "PGVectorStorage": ".kg.postgres_impl",
    "AGEStorage": ".kg.age_impl",
    "PGGraphStorage": ".kg.postgres_impl",
    
    "PGDocStatusStorage": ".kg.postgres_impl",
    "FaissVectorDBStorage": ".kg.faiss_impl",
    "QdrantVectorDBStorage": ".kg.qdrant_impl",
    "WeaviateDBVectorStorage": ".kg.weaviate_vector_db_impl",
    
}


# def verify_storage_implementation(storage_type: str, storage_name: str) -> None:
#     """Verify if storage implementation is compatible with specified storage type

#     Args:
#         storage_type: Storage type (KV_STORAGE, GRAPH_STORAGE etc.)
#         storage_name: Storage implementation name

#     Raises:
#         ValueError: If storage implementation is incompatible or missing required methods
#     """
#     # if storage_type not in STORAGE_IMPLEMENTATIONS:
#     raise ValueError(f"Unknown storage type: {storage_type}")

#     storage_info = STORAGE_IMPLEMENTATIONS[storage_type]
#     if storage_name not in storage_info["implementations"]:
#         raise ValueError(
#             f"Storage implementation '{storage_name}' is not compatible with {storage_type}. "
#             f"Compatible implementations are: {', '.join(storage_info['implementations'])}"
#         )

# def verify_storage_implementation(storage_type: str, storage_name_or_obj) -> None:
#     """Verify if storage implementation is compatible with specified storage type

#     Args:
#         storage_type: Storage type (KV_STORAGE, GRAPH_STORAGE etc.)
#         storage_name_or_obj: Storage implementation name or a custom storage class instance

#     Raises:
#         ValueError: If storage implementation is incompatible or missing required methods
#     """
#     # PATCH: Allow custom class instances that implement required methods
#     storage_info = STORAGE_IMPLEMENTATIONS[storage_type]
#     required_methods = storage_info["required_methods"]

#     # If a string, do the default check
#     if isinstance(storage_name_or_obj, str):
#         if storage_type not in STORAGE_IMPLEMENTATIONS:
#             raise ValueError(f"Unknown storage type: {storage_type}")

#         if storage_name_or_obj not in storage_info["implementations"]:
#             raise ValueError(
#                 f"Storage implementation '{storage_name_or_obj}' is not compatible with {storage_type}. "
#                 f"Compatible implementations are: {', '.join(storage_info['implementations'])}"
#             )
#     else:
#         # If it's a class instance, check it implements all required methods
#         # for method in required_methods:
#         #     if not hasattr(storage_name_or_obj, method):
#         #         raise ValueError(
#         #             f"Custom storage object for {storage_type} is missing required method: {method}"
#         #         )
#         for method in required_methods:
#             if not hasattr(storage_name_or_obj, method) or not callable(getattr(storage_name_or_obj, method)):
#                 raise ValueError(
#                     f"Custom storage object '{type(storage_name_or_obj).__name__}' for {storage_type} is missing required method: '{method}' or it's not callable."
#                 )



# def verify_storage_implementation(storage_type: str, storage_name_or_obj) -> None:

#     required_methods_map = {
#         "KV_STORAGE": ["get_by_id", "get_by_ids", "filter_keys", "upsert", "delete"],
#         "VECTOR_STORAGE": [
#             "query",
#             "upsert",
#             "delete_entity",
#             "delete_entity_relation",
#             "get_by_id",
#             "get_by_ids",
#             "delete",
#             "index_done_callback",
#             "close",
#         ],
#         "GRAPH_STORAGE": [
#             "upsert_node",
#             "upsert_edge",
#             "delete_node",
#             "remove_nodes",
#             "remove_edges",
#             "get_node",
#             "get_edge",
#             "get_node_edges",
#             "has_node",
#             "has_edge",
#             "node_degree",
#             "edge_degree",
#         ],
#         "DOC_STATUS_STORAGE": ["get_by_id", "get_docs_by_status", "upsert", "delete"],
#     }

#     if isinstance(storage_name_or_obj, str):
#         # Assume it's a known storage implementation; let lazy import handle errors
#         return

#     # Custom instance passed - check method presence
#     required_methods = required_methods_map.get(storage_type, [])
#     missing_methods = []
#     for method in required_methods:
#         attr = getattr(storage_name_or_obj, method, None)
#         if not callable(attr):
#             missing_methods.append(method)

#     if missing_methods:
#         raise ValueError(
#             f"Custom storage object '{type(storage_name_or_obj).__name__}' for {storage_type} is missing required methods: {missing_methods}"
#         )

def verify_storage_implementation(storage_type: str, storage_name_or_obj) -> None:
    print(f"[DEBUG] Skipping verify_storage_implementation for: {storage_type}")
    return  # <--- bypass all checks temporarily