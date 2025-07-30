from pathlib import Path
from datetime import datetime
import os
import sys
from typing import Dict, Optional

sys.path.append(os.path.dirname(Path(os.path.abspath(__file__)).parent))

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv(override=True, verbose=True, dotenv_path="backend/.env")

from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.core.config import simple_rag_config
from app.core.services.azure_services.az_ai_search_svc.simple_rag_index import SimpleRagIndex

import mimetypes

# Add all supported mimetypes so the app functions on app services
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"
)
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"
)
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"
)
mimetypes.add_type("text/plain", ".txt")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/bmp", ".bmp")
mimetypes.add_type("image/tiff", ".tiff")
mimetypes.add_type("image/heif", ".heif")
mimetypes.add_type("text/html", ".html")


text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4o",
    chunk_size=700,
    chunk_overlap=70,
)

async def file_loader(src_path: Path):

    documents = []

    for file_path in src_path.glob("**/*"):
        if file_path.is_file():
            # Check if this file is already indexed by filtering on metadata containing the uri as a substring
            filter_str = f"uri eq '{file_path.as_posix()}'"
            indexed_file_chunks = await SimpleRagIndex().asimilarity_search(
                query="*",  # or any dummy query, since we only care about filter
                k=1,
                filters=filter_str
            )
            if indexed_file_chunks:
                print(f"Skipping {file_path} (already indexed)")
                continue

            file_ext = file_path.suffix.lower()
            txt_file_path = file_path.with_suffix('.txt')
            docs = []
            # If it's a .txt file, just load as plain text
            if file_ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                docs = [Document(page_content=content, metadata={"url": file_path.as_posix(), "title": file_path.name.lower()})]
            # If not a .txt file, and a .txt with same name doesn't exist, use DocIntelLoader
            elif not txt_file_path.exists():
                loader = AzureAIDocumentIntelligenceLoader(
                    api_endpoint=simple_rag_config.DOCUMENT_INTELLIGENCE_ENDPOINT,  # type: ignore
                    api_key=simple_rag_config.DOCUMENT_INTELLIGENCE_API_KEY,
                    file_path=file_path.as_posix(),
                    api_model="prebuilt-layout",
                    mode="markdown",
                )
                docs = loader.load()
                # Persist each doc as a txt file with the same name as the source file (but .txt)
                with open(txt_file_path, "w", encoding="utf-8") as f:
                    for doc in docs:
                        f.write(doc.page_content + "\n")
            # Split and augment metadata for all docs
            file_name = file_path.name.lower()
            split_docs = text_splitter.transform_documents(docs)
            for idx, doc in enumerate(split_docs):
                doc.metadata["uri"] = file_path.as_posix()
                doc.metadata["title"] = f"{file_name}_{idx}"
                documents.append(doc)

    if not documents:
        print(f"No documents found in {src_path}")
        return

    print(f"Found {len(documents)} documents in {src_path}")
    print(f"Uploading {len(documents)} documents to vector store...")
    await SimpleRagIndex().aadd_documents(documents)

    # explicitly close the underlying SearchClient to avoid unclosed-session warnings
    # await SimpleRagIndex().async_client.close()

if __name__ == "__main__":
    # Example usage
    src_path = Path("backend", "admin_tools", "simple_rag_demo_data")  # Replace with your actual path
    if not src_path.exists():
        print(f"Source path {src_path} does not exist.")
        print("current working directory:", os.getcwd())
        sys.exit(1)
    import asyncio
    asyncio.run(file_loader(src_path))
