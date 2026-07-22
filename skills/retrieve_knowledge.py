from pydantic import BaseModel, Field

from app.rag_engine import retrieve_context

from .base import BaseSkill


class RetrievalArgs(BaseModel):
    """Input model for RetrieveKnowledgeSkill.

    Attributes:
        query: The search query string used to retrieve relevant
            document chunks.
        user_id: The identifier of the user making the request, used
            to scope or filter results when applicable.
    """

    query: str = Field(
        ...,
        description="Search query for document retrieval.",
    )
    user_id: int = Field(
        ...,
        description="User identifier for result scoping.",
    )


class RetrieveKnowledgeSkill(BaseSkill[RetrievalArgs]):
    """Skill that retrieves relevant document chunks from ChromaDB.

    Delegates to the existing :func:`retrieve_context` function from
    ``app.rag_engine`` so the skill layer stays a thin wrapper around
    the current retrieval pipeline.

    Usage:
        skill = RetrieveKnowledgeSkill()
        result = await skill.run({"query": "如何配置网关", "user_id": 42})
    """

    name: str = "retrieve_knowledge"
    description: str = (
        "Retrieve document chunks from ChromaDB relevant to a given "
        "query for a specific user."
    )
    args_schema: type[RetrievalArgs] = RetrievalArgs

    async def execute(self, args: RetrievalArgs) -> list[dict]:
        """Execute the ChromaDB retrieval.

        Args:
            args: Validated retrieval parameters including *query*
                and *user_id*.

        Returns:
            A list of document chunk dictionaries returned by
            :func:`retrieve_context`.
        """
        return retrieve_context(
            query=args.query,
            user_id=args.user_id,
        )
