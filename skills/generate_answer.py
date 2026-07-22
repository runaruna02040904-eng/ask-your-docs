from pydantic import BaseModel, Field

from .base import BaseSkill


class GenerateAnswerInput(BaseModel):
    """Input model for GenerateAnswerSkill.

    Attributes:
        context: Retrieved document chunks used as reference.
        question: The user's original query.
    """

    context: str = Field(
        ...,
        description="Retrieved document context for answering.",
    )
    question: str = Field(
        ...,
        description="The user's query to answer.",
    )


class GenerateAnswerSkill(BaseSkill[GenerateAnswerInput]):
    """Skill that generates an answer from context using DeepSeek LLM.

    Builds a LangChain prompt that instructs the model to answer strictly
    based on the provided context.  If the context does not contain the
    answer, the model responds with "文档中没有相关信息".

    Usage:
        skill = GenerateAnswerSkill()
        answer = await skill.run({
            "context": "Retrieved document text ...",
            "question": "什么是 RAG？",
        })
    """

    name: str = "generate_answer"
    description: str = (
        "Generate a concise answer from the provided document context "
        "using the DeepSeek LLM via ChatOpenAI."
    )
    args_schema: type[GenerateAnswerInput] = GenerateAnswerInput

    async def execute(self, args: GenerateAnswerInput) -> str:
        """Generate an answer based on context and question.

        Local imports avoid circular module dependencies.  The LLM is
        invoked with a zero-temperature setting for deterministic output.

        Args:
            args: Validated input with *context* and *question*.

        Returns:
            The generated answer string.
        """
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.messages import SystemMessage, HumanMessage

        from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

        llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=DEEPSEEK_API_KEY,
            openai_api_base=DEEPSEEK_BASE_URL,
            temperature=0,
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=(
                    "You are a document-based intelligent assistant. "
                    "Strictly use the following context to answer the "
                    "question. If the context cannot answer, say "
                    "'文档中没有相关信息'.\n\n"
                    "Context:\n{context}"
                )
            ),
            HumanMessage(content="{question}"),
        ])

        chain = prompt | llm
        response = chain.invoke({
            "context": args.context,
            "question": args.question,
        })

        return response.content
