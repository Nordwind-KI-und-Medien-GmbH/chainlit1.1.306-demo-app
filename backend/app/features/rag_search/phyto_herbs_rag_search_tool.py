from langchain.tools import tool
from pydantic import BaseModel, Field

from app.core.services.azure_services.az_ai_search_svc.phyto_herbs_index import PhytoHerbsIndex


class SearchInput(BaseModel):
    query: str = Field(
        description="Gib eine semantische Suchanfrage ein, um gezielt Informationen über Pflanzen und deren phytotherapeutische Anwendung zu finden. Vermeide zu allgemeine oder vage Anfragen. Gute Beispiele: 'Wirkstoffe und Anwendungsgebiete von Johanniskraut.', 'Nebenwirkungen von Baldrian in der Phytotherapie.' Schlechte Beispiele: Ein-Wort-Anfragen oder zu allgemeine Suchen wie 'Pflanzen'."
    )


@tool("phyto-herbs-rag-search-tool", args_schema=SearchInput)
async def phyto_herbs_rag_search_tool(query: str) -> str:
    """
    Nutze dieses Tool, um gezielt Informationen zu Pflanzen und deren phytotherapeutischer Anwendung zu finden.

    Denke sorgfältig darüber nach, wie die gefundenen Informationen zur Anfrage des Nutzers passen. Antworte, sobald du relevante Informationen gefunden hast.

    Gib immer Referenzen als Markdown-Fußnoten an. Beispiel:

    Die Wirkstoffe von Johanniskraut sind X und Y. [^1]

    [^1]: [Quelle](https://beispiel.de/quelle)
    """
    try:
        phyto_index = PhytoHerbsIndex()
        results = await phyto_index.semantic_search(query=query, k=5)

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
            "response": "Bei der Suche ist ein Fehler aufgetreten.",
            "instructions": "Bitte informiere den Nutzer über den Fehler und schlage alternative Schritte vor.",
        }  # type: ignore
