from pathlib import Path
from datetime import datetime
import os
from typing import Dict, Optional

from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from init import DOCUMENT_INTELLIGENCE_API_KEY, DOCUMENT_INTELLIGENCE_ENDPOINT
from services.azure_services import AzureServices

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

azure_services = AzureServices()

async def file_loader(src_path: Path):

    documents = []

    for file_path in src_path.glob("**/*"):
        if file_path.is_file():
            loader = AzureAIDocumentIntelligenceLoader(
                api_endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,  # type: ignore
                api_key=DOCUMENT_INTELLIGENCE_API_KEY,
                file_path=file_path.as_posix(),
                api_model="prebuilt-layout",
                mode="markdown",
            )
            docs = loader.load()

            split_docs = text_splitter.transform_documents(docs)

            file_name = file_path.name.lower()
            file_chk_idx = 0
            for doc in split_docs:
                doc.metadata["url"] = file_path.as_posix()
                doc.metadata["title"] = f"{file_name}_{file_chk_idx}"
                documents.append(doc)
                file_chk_idx += 1

    if not documents:
        print(f"No documents found in {src_path}")
        return

    print(f"Found {len(documents)} documents in {src_path}")
    print(f"Uploading {len(documents)} documents to vector store...")
    await azure_services.rag_vector_store.aadd_documents(documents)

    # explicitly close the underlying SearchClient to avoid unclosed-session warnings
    await azure_services.rag_vector_store.async_client.close()

if __name__ == "__main__":
    # Example usage
    src_path = Path(r"<path to demo RAG File>")  # Replace with your actual path

    import asyncio
    asyncio.run(file_loader(src_path))
