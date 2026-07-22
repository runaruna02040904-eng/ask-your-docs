from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from pydantic import ValidationError

from skills.add_document import AddDocumentSkill, AddDocumentInput


class TestAddDocumentSkill:
    """Unit tests for AddDocumentSkill."""

    @patch("langchain_text_splitters.RecursiveCharacterTextSplitter")
    @patch("langchain_community.vectorstores.Chroma")
    @patch("langchain_huggingface.HuggingFaceEmbeddings")
    @patch("app.config.PERSIST_DIR", "./test_chroma", create=True)
    async def test_execute_returns_chunk_count(
        self,
        mock_embeddings_cls,
        mock_chroma_cls,
        mock_text_splitter_cls,
    ):
        """Successfully indexing documents should return the number of chunks."""
        # Arrange
        fake_chunks = [MagicMock(), MagicMock(), MagicMock()]
        mock_text_splitter = mock_text_splitter_cls.return_value
        mock_text_splitter.create_documents.return_value = fake_chunks

        skill = AddDocumentSkill()
        raw_args = {
            "content": "Some document text to index.",
            "user_id": 1,
            "filename": "test.txt",
        }

        # Act
        result = await skill.run(raw_args)

        # Assert
        assert result == 3

        mock_text_splitter_cls.assert_called_once_with(
            chunk_size=500,
            chunk_overlap=100,
            separators=[
                "\n\n", "\n", "\u3002", "\uff01", "\uff1f",
                "\uff1b", "\uff0c", " ", "",
            ],
        )
        mock_text_splitter.create_documents.assert_called_once_with(
            ["Some document text to index."]
        )

        # Each fake chunk should have had metadata.source set
        for c in fake_chunks:
            assert c.metadata["source"] == "test.txt"

        mock_chroma_cls.assert_called_once_with(
            collection_name="user_1",
            embedding_function=mock_embeddings_cls.return_value,
            persist_directory="./test_chroma",
        )

    @patch("langchain_text_splitters.RecursiveCharacterTextSplitter")
    @patch("langchain_community.vectorstores.Chroma")
    @patch("langchain_huggingface.HuggingFaceEmbeddings")
    @patch("app.config.PERSIST_DIR", "./chroma_data", create=True)
    async def test_execute_default_filename(
        self,
        mock_embeddings_cls,
        mock_chroma_cls,
        mock_text_splitter_cls,
    ):
        """Omitting filename should default to 'upload'."""
        fake_chunks = [MagicMock(), MagicMock()]
        mock_text_splitter = mock_text_splitter_cls.return_value
        mock_text_splitter.create_documents.return_value = fake_chunks

        skill = AddDocumentSkill()
        result = await skill.run({
            "content": "Hello world.",
            "user_id": 5,
        })

        assert result == 2
        for c in fake_chunks:
            assert c.metadata["source"] == "upload"

    @patch("langchain_text_splitters.RecursiveCharacterTextSplitter")
    @patch("langchain_community.vectorstores.Chroma")
    @patch("langchain_huggingface.HuggingFaceEmbeddings")
    @patch("app.config.PERSIST_DIR", "./chroma_data", create=True)
    async def test_execute_empty_content_raises_error(
        self,
        mock_embeddings_cls,
        mock_chroma_cls,
        mock_text_splitter_cls,
    ):
        """Empty content should propagate a ValueError through run()."""
        skill = AddDocumentSkill()

        with pytest.raises(ValueError, match="Document content cannot be empty"):
            await skill.run({
                "content": "   ",
                "user_id": 1,
            })

        # Chroma should never have been touched.
        mock_chroma_cls.assert_not_called()

    @patch("langchain_text_splitters.RecursiveCharacterTextSplitter")
    @patch("langchain_community.vectorstores.Chroma")
    @patch("langchain_huggingface.HuggingFaceEmbeddings")
    @patch("app.config.PERSIST_DIR", "./chroma_data", create=True)
    async def test_execute_whitespace_only_content(
        self,
        mock_embeddings_cls,
        mock_chroma_cls,
        mock_text_splitter_cls,
    ):
        """Whitespace-only content should also raise ValueError."""
        skill = AddDocumentSkill()

        with pytest.raises(ValueError, match="Document content cannot be empty"):
            await skill.run({
                "content": "\n  \t  \n",
                "user_id": 1,
            })

        mock_chroma_cls.assert_not_called()

    async def test_run_missing_content_raises_validation_error(self):
        """Missing 'content' should cause a Pydantic ValidationError."""
        skill = AddDocumentSkill()

        with pytest.raises(ValidationError) as exc_info:
            await skill.run({"user_id": 1})

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("content",) for e in errors)

    async def test_run_missing_user_id_raises_validation_error(self):
        """Missing 'user_id' should cause a Pydantic ValidationError."""
        skill = AddDocumentSkill()

        with pytest.raises(ValidationError) as exc_info:
            await skill.run({"content": "text"})

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("user_id",) for e in errors)


class TestAddDocumentInput:
    """Unit tests for the AddDocumentInput Pydantic model."""

    def test_valid_input(self):
        """Valid data should construct successfully."""
        m = AddDocumentInput(content="Hello", user_id=1)
        assert m.content == "Hello"
        assert m.user_id == 1
        assert m.filename == "upload"

    def test_custom_filename(self):
        """Custom filename should be accepted."""
        m = AddDocumentInput(content="Hello", user_id=1, filename="custom.pdf")
        assert m.filename == "custom.pdf"

    def test_content_type_enforced(self):
        """Numeric content should be rejected."""
        with pytest.raises(ValidationError):
            AddDocumentInput(content=123, user_id=1)

    def test_user_id_type_enforced(self):
        """String user_id should be rejected."""
        with pytest.raises(ValidationError):
            AddDocumentInput(content="Hello", user_id="not-a-number")
