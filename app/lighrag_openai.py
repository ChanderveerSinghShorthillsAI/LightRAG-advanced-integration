import os  # for os.path , it means that we are using the os module to work with file paths
import asyncio  # for async functions
import logging  # for logging
import logging.config  # for logging configuration
import fitz  # PyMuPDF , it means that we are using the fitz module to work with PDF files

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import logger, set_verbose_debug

WORKING_DIR = (
    "./dickens"  # this means that we are using the working directory to store the data
)
PDF_FILE = "./book.pdf"  # <- Update this path to your actual PDF


def configure_logging():
    """Configure logging for the application"""
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


def extract_text_from_pdf(file_path): # it means that we are extracting text from a PDF file
    """Extracts all text from a PDF file using PyMuPDF"""
    doc = fitz.open(
        file_path
    )  # it means that we are opening the PDF file and creating a document object
    return "\n".join(
        [page.get_text() for page in doc]
    )  # it means that we are extracting the text from each page and joining them with a newline character


if not os.path.exists(
    WORKING_DIR
):  # it means that we are checking if the working directory exists
    os.mkdir(
        WORKING_DIR
    )  # it means that we are creating the working directory if it does not exist


async def initialize_rag():  # it means that we are initializing the LightRAG object
    """Initialize the LightRAG object with OpenAI models"""
    rag = LightRAG(  # it means that we are creating a LightRAG object
        working_dir=WORKING_DIR,  # it means that we are setting the working directory
        embedding_func=openai_embed,  # it means that we are setting the embedding function to OpenAI's embedding function
        llm_model_func=gpt_4o_mini_complete,  # it means that we are setting the LLM model function to OpenAI's LLM model function
    )
    await rag.initialize_storages()  # it means that we are initializing the storages for the LightRAG object , in detail it means that we are creating the storage directories and files for the LightRAG object
    await initialize_pipeline_status()  # it means that we are initializing the pipeline status for the LightRAG object , we are doing this to check if the pipeline is running or not
    return rag  # it means that we are returning the LightRAG object
    # this function initializes the LightRAG object with the specified working directory, embedding function, and LLM model function. It also initializes the storages and pipeline status for the LightRAG object.


# async def main():
#     try:
#         rag = await initialize_rag() # it means that we are initializing the LightRAG object

#         pdf_text = extract_text_from_pdf(PDF_FILE) # it means that we are extracting the text from the PDF file
#         await rag.ainsert(pdf_text) # This inserts the extracted PDF text into the LightRAG knowledge base, updating its index.

#         query = "What are the top insights from the document?" # it means that we are setting the query to ask for the top insights from the document

#         for mode in ["naive", "local", "global", "hybrid"]: # it means that we are iterating over the different query modes , the modes are naive, local, global, and hybrid , which means that we are using different query modes to get the results , naive means that naive means that we are using the naive query mode, local means that we are using the local query mode, global means that we are using the global query mode, and hybrid means that we are using the hybrid query mode
#             print(f"\n=====================\nQuery mode: {mode}\n=====================")
#             response = await rag.aquery(query, param=QueryParam(mode=mode)) # it means that we are querying the LightRAG object with the query and the query mode , and in return we are getting the response from the LightRAG object
#             print(response) # it means that we are printing the response from the LightRAG object

#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         if 'rag' in locals():
#             await rag.finalize_storages()

# ...existing code...


async def main():
    try:
        rag = await initialize_rag() # it means that we are initializing the LightRAG object
        pdf_text = extract_text_from_pdf(PDF_FILE) # it means that we are extracting the text from the PDF file
        await rag.ainsert(pdf_text) # it means that we are inserting the PDF text into the LightRAG object

        print("You can now ask questions about your knowledge base.")
        print(
            "Type your question and press Enter. Type 'exit', 'quit', 'q', or press Ctrl+C to exit.\n"
        )

        while True:
            try:
                user_query = input("Your question: ").strip()
                if user_query.lower() in {"exit", "quit", "q"}:
                    print("Exiting...")
                    break
                if not user_query:
                    continue
                # You can change the mode here if you want, e.g., mode="hybrid"
                response = await rag.aquery(user_query, param=QueryParam(mode="hybrid")) # it means that we are querying the LightRAG object with the user query and the query mode . in detail it first embeds the user query and then queries the LightRAG object with the user query and the query mode , and in return we are getting the response from the LightRAG object
                print(f"Answer: {response}\n")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if "rag" in locals():
            await rag.finalize_storages() # it means that we are finalizing the storages for the LightRAG object , in detail it means that we are closing the storage directories and files for the LightRAG object


# ...existing code...


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
    print("\nDone!")
