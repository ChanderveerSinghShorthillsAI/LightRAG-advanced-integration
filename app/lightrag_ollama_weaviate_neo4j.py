import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import logging
import logging.config
import fitz
from lrag.lightrag import LightRAG, QueryParam
from lrag.lightrag.llm.ollama import ollama_model_complete, ollama_embedding
from lrag.lightrag.utils import logger, set_verbose_debug, EmbeddingFunc
WORKING_DIR = "./dickens"
PDF_FILE = "./book3.txt"  # Update as needed

def configure_logging():
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "lightrag"]:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers = []
        logger_instance.filters = []

    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "lightrag_demo.log"))
    print(f"\nLightRAG demo log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": "%(levelname)s: %(message)s"},
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "file": {
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": log_file_path,
                    "maxBytes": log_max_bytes,
                    "backupCount": log_backup_count,
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "lightrag": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )
    logger.setLevel(logging.INFO)
    set_verbose_debug(os.getenv("VERBOSE_DEBUG", "false").lower() == "true")



def extract_text_from_pdf(file_path):
        if file_path.endswith(".pdf"):
            doc = fitz.open(file_path)
            return "\n".join([page.get_text() for page in doc])
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        else:
            raise ValueError("Unsupported file format. Only .pdf and .txt are supported.")


os.makedirs(WORKING_DIR, exist_ok=True)


from lrag.lightrag.kg.weaviate_vector_db_impl import WeaviateDBVectorStorage


from sentence_transformers import SentenceTransformer

# Load the model once (global scope is efficient)
e5_model = SentenceTransformer("intfloat/e5-base-v2")


from app.core.settings import settings

def get_embedding_func():
    async def embed(texts):
        formatted = [
            f"query: {t}" if len(t.strip().split()) < 10 else f"passage: {t}"
            for t in texts
        ]
        return e5_model.encode(formatted, show_progress_bar=False)
    return embed

from lrag.lightrag.kg.weaviate_vector_db_impl import WeaviateDBVectorStorage



async def initialize_rag():
    try:
        embedding_func = get_embedding_func()
        print("Embedding function created successfully.")
    except Exception as e:
        print(f"Error creating embedding function: {e}")
        raise

    try:
        rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=ollama_model_complete,
            llm_model_name="qwen2:0.5b",
            llm_model_kwargs={
                "host": "http://localhost:11434",
                "options": {"num_ctx": 2048 , "temperature": 0.3}
            },
            cosine_better_than_threshold=0.5,
            vector_storage="WeaviateDBVectorStorage",  # ✅ Pass the class name as a string
            vector_db_storage_cls_kwargs={
                "namespace": "my_weaviate_namespace",  # Configuration for WeaviateDBVectorStorage
                "embedding_func": EmbeddingFunc(
                    embedding_dim=768,
                    max_token_size=8192,
                    func=embedding_func,
                ),
                "WEAVIATE_URL": "https://8b03ytqqre7ziuzeqatha.c0.asia-southeast1.gcp.weaviate.cloud",
                "WEAVIATE_API_KEY": "KtsoVLh3l4ZNjPzfXFcbaTyE0Yp2DBtw6zAg",
                "EMBEDDING_DIMENSIONS": 768,
                "global_config": {  # Pass global_config here
                    "type": "unhashed",
                }
            },
            embedding_func=EmbeddingFunc(# This seems redundant if also passed in cls_kwargs
                embedding_dim=768,
                max_token_size=8192,
                func=embedding_func,
            ),
            graph_storage="Neo4JStorage",
            # global_config={},  # Pass this if used internally
           
        )
        print("LightRAG instance created successfully.")
    except Exception as e:
        print(f"Error creating LightRAG instance: {e}")
        raise

    try:
        await rag.initialize_storages()
        print("Storages initialized successfully.")
    except Exception as e:
        print(f"Error initializing storages: {e}")
        raise
    # await rag.initialize_storages()
    finally:
        if "rag" in locals():
            print("[DEBUG] Finalizing storages...")
            # await rag.finalize_storages()
    return rag


# from lightrag.vectorstore.weaviate_storage import WeaviateStorage

async def main():
    try:
        try:
            rag = await initialize_rag()
        except Exception as e:
            print(f"Error initializing RAG: {e}")
            return
        
        pdf_text = extract_text_from_pdf(PDF_FILE)
        print(f"[DEBUG] Extracted {len(pdf_text)} characters from PDF")
        # await rag.ainsert(pdf_text)
        chunks = [pdf_text[i:i+100] for i in range(0, len(pdf_text), 100)]
        print(f"[DEBUG] Manually created {len(chunks)} chunks")
        await rag.ainsert_custom_chunks(full_text=pdf_text, text_chunks=chunks)
        print("[DEBUG] Finished inserting into RAG. Try a query now.")
        # After inserting, check how many chunks are in the vector store
        if hasattr(rag, "text_chunks"):
            all_chunks = await rag.text_chunks.get_by_ids([])
            print(f"[DEBUG] Number of chunks in text_chunks: {len(all_chunks)}")
        else:
            print("[DEBUG] rag.text_chunks not found!")
        # all_chunks = await rag.chunks_vdb.query("who is silas")
        # print(all_chunks)
        query_result = await rag.chunks_vdb.query("who is silas", top_k=5)
        print(f"[DEBUG] Raw vector search result (manual): {query_result}")
        print("You can now ask questions about your knowledge base.")
        print("Type your question and press Enter. Type 'exit', 'quit', 'q', or press Ctrl+C to exit.\n")
        while True:
            try:
                user_query = input("Your question: ").strip()
                if user_query.lower() in {"exit", "quit", "q"}:
                    print("Exiting...")
                    break
                if not user_query:
                    continue
                # response = await rag.aquery(user_query, param=QueryParam(mode="naive"))
                # print(f"Answer: {response}\n")
                print(f"[DEBUG] Querying: {user_query}")

                response = await rag.aquery(user_query, param=QueryParam(mode="naive" , top_k=5))
                # response = await rag.aquery("who is silas", param=QueryParam(mode="naive"))
                print(f"[DEBUG] Raw response: {response}")
                print(f"Answer: {response}\n")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break
        # response = await rag.aquery("who is silas", param=QueryParam(mode="naive"))
        # print(f"[DEBUG] Raw response: {response}")
        # print(f"Answer: {response}\n")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if "rag" in locals():
            await rag.finalize_storages()



if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
    print("\nDone!")
