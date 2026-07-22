from pydantic import BaseModel, Field

from .base import BaseSkill


class AddDocumentInput(BaseModel):
    """Input model for AddDocumentSkill.

    Attributes:
        content: The raw document text to be chunked and indexed.
        user_id: Owner of the document; used to scope the Chroma
            collection.
        filename: Optional source filename, stored as metadata on
            each chunk.  Defaults to ``"upload"``.
    """

    content: str = Field(
        ...,
        description="Raw document text to chunk and store.",
    )
    user_id: int = Field(
        ...,
        description="User identifier for collection scoping.",
    )
    filename: str = Field(
        "upload",
        description="Source filename stored in chunk metadata.",
    )


class AddDocumentSkill(BaseSkill[AddDocumentInput]):
    """Skill that chunks raw text and indexes it into ChromaDB.

    Uses ``RecursiveCharacterTextSplitter`` to split the content and
    ``HuggingFaceEmbeddings`` (``all-MiniLM-L6-v2``) to vectorise
    each chunk before persisting to a user-scoped Chroma collection.

    Usage:
        skill = AddDocumentSkill()
        count = await skill.run({
            "content": "Long document text ...",
            "user_id": 42,
            "filename": "report.pdf",
        })
        print(count)  # number of chunks indexed
    """

    name: str = "add_document"
    description: str = (
        "Split document text into chunks and index them into "
        "ChromaDB with vector embeddings for later retrieval."
    )
    args_schema: type[AddDocumentInput] = AddDocumentInput

    async def execute(self, args: AddDocumentInput) -> int:
        """Chunk and index the document into ChromaDB.

        Args:
            args: Validated input containing *content*, *user_id*,
                and optional *filename*.

        Returns:
            Number of text chunks successfully indexed.

        Raises:
            ValueError: If *content* is empty or only whitespace.
        """
        if not args.content.strip():
            raise ValueError("Document content cannot be empty.")

        # Local imports to avoid circular dependencies at module level.
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        try:
            from app.config import PERSIST_DIR
        except ImportError:
            # Fallback default path when PERSIST_DIR is not yet
            # defined in app.config.
            import os
            PERSIST_DIR = os.getenv(
                "CHROMA_PERSIST_DIR", "./chroma_data"
            )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", "\u3002", "\uff01", "\uff1f",
                         "\uff1b", "\uff0c", " ", ""],
        )
        chunks = text_splitter.create_documents([args.content])

        for chunk in chunks:
            chunk.metadata["source"] = args.filename

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
        )

        vectorstore = Chroma(
            collection_name=f"user_{args.user_id}",
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR,
        )
        vectorstore.add_documents(chunks)

        return len(chunks)
