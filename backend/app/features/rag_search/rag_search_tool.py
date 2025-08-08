from app.core.services.azure_services.az_ai_search_svc.simple_rag_index import (
    SimpleRagIndex,
)
from langchain.tools import tool
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(
        description="Enter a semantic search query to find relevant information from the knowledge base. Avoid too general or vague queries. Good examples: 'How to implement authentication in web applications', 'Best practices for database design'. Bad examples: Single-word queries or too general searches like 'programming'."
    )


@tool("simple-rag-search-tool", args_schema=SearchInput)
async def simple_rag_search_tool(query: str) -> str:
    """
    Use this tool to find relevant information from the knowledge base.

    Think carefully about how the found information relates to the user's query. Respond as soon as you find relevant information.

    Always provide references as Markdown footnotes. Example:

    The best practices for authentication are X and Y. [^1]

    [^1]: [Source](https://example.com/source)
    """
    try:
        simple_rag_index = SimpleRagIndex()
        results = await simple_rag_index.asimilarity_search(query=query, k=5)

        return [
            {
                "page_content": doc.page_content,
                "url": doc.metadata.get("url", ""),
                "title": doc.metadata.get("title", ""),
            }
            for doc in results
        ]  # type: ignore
    except Exception:
        return {
            "response": "An error occurred during the search.",
            "instructions": "Please inform the user about the error and suggest alternative steps.",
        }  # type: ignore
