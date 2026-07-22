import pytest
from unittest.mock import patch

from pydantic import ValidationError

from skills.retrieve_knowledge import RetrieveKnowledgeSkill


class TestRetrieveKnowledgeSkill:
    """Unit tests for RetrieveKnowledgeSkill."""

    @patch("skills.retrieve_knowledge.retrieve_context")
    async def test_execute_with_valid_input(self, mock_retrieve_context):
        """Normal input should invoke retrieve_context and return its result."""
        mock_retrieve_context.return_value = "Relevant document chunk."

        skill = RetrieveKnowledgeSkill()
        result = await skill.run({"query": "什么是 RAG", "user_id": 42})

        mock_retrieve_context.assert_called_once_with(
            question="什么是 RAG",
            user_id=42,
        )
        assert result == "Relevant document chunk."

    @patch("skills.retrieve_knowledge.retrieve_context")
    async def test_execute_multiple_chunks_context(self, mock_retrieve_context):
        """Multiple document chunks should be joined back as a single string."""
        mock_retrieve_context.return_value = "Chunk A\n\nChunk B\n\nChunk C"

        skill = RetrieveKnowledgeSkill()
        result = await skill.run({"query": "RAG pipeline", "user_id": 7})

        assert result == "Chunk A\n\nChunk B\n\nChunk C"
        mock_retrieve_context.assert_called_once_with(
            question="RAG pipeline",
            user_id=7,
        )

    async def test_run_with_missing_query_raises_validation_error(self):
        """Missing 'query' should cause a Pydantic ValidationError."""
        skill = RetrieveKnowledgeSkill()

        with pytest.raises(ValidationError) as exc_info:
            await skill.run({"user_id": 42})

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("query",) for e in errors)

    async def test_run_with_missing_user_id_raises_validation_error(self):
        """Missing 'user_id' should cause a Pydantic ValidationError."""
        skill = RetrieveKnowledgeSkill()

        with pytest.raises(ValidationError) as exc_info:
            await skill.run({"query": "test"})

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("user_id",) for e in errors)

    async def test_run_with_empty_dict_raises_validation_error(self):
        """Empty input should trigger validation errors for both fields."""
        skill = RetrieveKnowledgeSkill()

        with pytest.raises(ValidationError):
            await skill.run({})

    async def test_run_with_extra_fields_succeeds(self):
        """Extra fields in the input dict should be silently dropped."""
        skill = RetrieveKnowledgeSkill()

        # Pydantic v2 strips extra fields by default; we just check no error.
        try:
            result = await skill.run({
                "query": "hello",
                "user_id": 1,
                "extra_field": "ignored",
            })
        except ValidationError:
            pytest.fail("Extra fields should not cause validation errors.")


class TestRetrievalArgs:
    """Unit tests for the RetrievalArgs Pydantic model."""

    def test_valid_args(self):
        """Valid data should construct successfully."""
        from skills.retrieve_knowledge import RetrievalArgs

        args = RetrievalArgs(query="test query", user_id=99)
        assert args.query == "test query"
        assert args.user_id == 99

    def test_query_type_enforced(self):
        """Passing a numeric query should raise."""
        from skills.retrieve_knowledge import RetrievalArgs

        with pytest.raises(ValidationError):
            RetrievalArgs(query=123, user_id=1)

    def test_user_id_type_enforced(self):
        """Passing a string user_id should raise."""
        from skills.retrieve_knowledge import RetrievalArgs

        with pytest.raises(ValidationError):
            RetrievalArgs(query="test", user_id="not-an-int")
