from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from skills.generate_answer import GenerateAnswerSkill, GenerateAnswerInput


class TestGenerateAnswerSkill:
    """Unit tests for GenerateAnswerSkill."""

    @patch("langchain_openai.ChatOpenAI.invoke")
    @patch("app.config.DEEPSEEK_API_KEY", "test-key")
    @patch("app.config.DEEPSEEK_BASE_URL", "https://api.test.com/v1")
    async def test_execute_returns_answer(self, mock_llm_invoke):
        """Normal input should invoke the LLM and return the response content."""
        mock_response = MagicMock()
        mock_response.content = (
            "RAG stands for Retrieval-Augmented Generation."
        )
        mock_llm_invoke.return_value = mock_response

        skill = GenerateAnswerSkill()
        result = await skill.run({
            "context": "RAG is a technique that combines retrieval "
                       "with text generation.",
            "question": "What is RAG?",
        })

        assert result == "RAG stands for Retrieval-Augmented Generation."
        mock_llm_invoke.assert_called_once()
        # Verify the invoke received the formatted messages
        call_args = mock_llm_invoke.call_args[0][0]
        assert any("RAG is a technique" in str(m) for m in call_args)

    @patch("langchain_openai.ChatOpenAI.invoke")
    @patch("app.config.DEEPSEEK_API_KEY", "test-key")
    @patch("app.config.DEEPSEEK_BASE_URL", "https://api.test.com/v1")
    async def test_execute_empty_context(self, mock_llm_invoke):
        """Empty context should still produce an LLM response."""
        mock_response = MagicMock()
        mock_response.content = "文档中没有相关信息"
        mock_llm_invoke.return_value = mock_response

        skill = GenerateAnswerSkill()
        result = await skill.run({
            "context": "",
            "question": "What is RAG?",
        })

        assert result == "文档中没有相关信息"
        mock_llm_invoke.assert_called_once()

    @patch("langchain_openai.ChatOpenAI.invoke")
    @patch("app.config.DEEPSEEK_API_KEY", "test-key")
    @patch("app.config.DEEPSEEK_BASE_URL", "https://api.test.com/v1")
    async def test_execute_handles_llm_error(self, mock_llm_invoke):
        """LLM errors should propagate through run()."""
        mock_llm_invoke.side_effect = RuntimeError("API unavailable")

        skill = GenerateAnswerSkill()
        with pytest.raises(RuntimeError, match="API unavailable"):
            await skill.run({
                "context": "Some context.",
                "question": "Any question?",
            })

    async def test_execute_missing_context_raises_validation_error(self):
        """Missing 'context' should cause a Pydantic ValidationError."""
        skill = GenerateAnswerSkill()

        with pytest.raises(ValidationError) as exc_info:
            await skill.run({"question": "What is RAG?"})

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("context",) for e in errors)

    async def test_execute_missing_question_raises_validation_error(self):
        """Missing 'question' should cause a Pydantic ValidationError."""
        skill = GenerateAnswerSkill()

        with pytest.raises(ValidationError) as exc_info:
            await skill.run({"context": "Some context."})

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("question",) for e in errors)

    async def test_execute_empty_input_raises_validation_error(self):
        """Completely empty input should trigger validation errors."""
        skill = GenerateAnswerSkill()

        with pytest.raises(ValidationError):
            await skill.run({})


class TestGenerateAnswerInput:
    """Unit tests for the GenerateAnswerInput Pydantic model."""

    def test_valid_input(self):
        """Valid data should construct successfully."""
        m = GenerateAnswerInput(context="Some context.", question="A question?")
        assert m.context == "Some context."
        assert m.question == "A question?"

    def test_context_type_enforced(self):
        """Non-string context should be rejected."""
        with pytest.raises(ValidationError):
            GenerateAnswerInput(context=123, question="test")

    def test_question_type_enforced(self):
        """Non-string question should be rejected."""
        with pytest.raises(ValidationError):
            GenerateAnswerInput(context="test", question=456)
