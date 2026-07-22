import asyncio
import logging
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from skills.base import BaseSkill
from skills.retrieve_knowledge import RetrieveKnowledgeSkill
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

logger = logging.getLogger(__name__)


class ChatState(TypedDict):
    """State definition persisted across agent graph nodes.

    Attributes:
        question: The user's original input question.
        user_id: Identifier used to scope vector-store queries.
        context: Raw document chunks retrieved from ChromaDB.
        answer: The final generated answer.
        history: Turn-level conversation history for follow-up context.
        iteration: Current iteration count; checked against *max_iterations*.
    """

    question: str
    user_id: int
    context: str
    answer: str
    history: List[Dict[str, Any]]
    iteration: int


class Agent:
    """LangGraph-based agent that orchestrates Skill instances.

    Builds a :class:`StateGraph` whose nodes dispatch to registered
    :class:`BaseSkill` subclasses.  Security boundaries are hard-coded:

    * *max_iterations* (5) — caps the number of retrieve–generate cycles.
    * *timeout* (30 s) — upper bound for a single :meth:`invoke` call.
    * *allowed_tools* — a whitelist populated automatically by
      :meth:`add_skill`; every node dispatch is checked against it.

    Usage:
        agent = Agent()
        agent.add_skill(RetrieveKnowledgeSkill())
        answer = agent.invoke("什么是 RAG？", user_id=1)
        print(answer)
    """

    max_iterations: int = 5
    timeout: int = 30

    def __init__(self) -> None:
        self._skills: Dict[str, BaseSkill] = {}
        self._allowed_tools: List[str] = []
        self._graph: StateGraph | None = None
        self._build_graph()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_skill(self, skill: BaseSkill) -> None:
        """Register a skill and add its name to the tool whitelist.

        After registration the caller must rebuild the graph if they
        want the new skill to appear as a routing target.

        Args:
            skill: A concrete :class:`BaseSkill` instance.

        Raises:
            TypeError: If *skill* does not carry the required class
                attributes (``name``, ``description``, ``args_schema``).
        """
        if not all(hasattr(skill, attr) for attr in ("name", "description", "args_schema")):
            raise TypeError(
                f"'{type(skill).__name__}' is missing required BaseSkill attributes; "
                f"ensure it defines 'name', 'description', and 'args_schema'."
            )
        self._skills[skill.name] = skill
        self._allowed_tools.append(skill.name)
        self._build_graph()
        logger.info("Skill '%s' registered and graph rebuilt.", skill.name)

    def invoke(self, user_input: str, user_id: int) -> str:
        """Run the full agent pipeline and return the final answer.

        Args:
            user_input: The user's question text.
            user_id: User identifier for data isolation.

        Returns:
            The generated answer string.

        Raises:
            RuntimeError: If the underlying graph has not been built.
            TimeoutError: If execution exceeds *timeout* seconds.
        """
        if self._graph is None:
            raise RuntimeError("Agent graph has not been built.")

        initial_state: ChatState = {
            "question": user_input,
            "user_id": user_id,
            "context": "",
            "answer": "",
            "history": [],
            "iteration": 0,
        }

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            final_state: ChatState = loop.run_until_complete(
                asyncio.wait_for(
                    self._graph.ainvoke(initial_state),
                    timeout=self.timeout,
                )
            )
        except asyncio.TimeoutError:
            logger.error(
                "Agent.invoke timed out after %d s (user_input='%s')",
                self.timeout,
                user_input,
            )
            raise TimeoutError(
                f"Agent execution exceeded {self.timeout}s timeout."
            )
        finally:
            loop.close()

        return final_state["answer"]

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(self) -> None:
        """(Re)build the :class:`StateGraph` from the currently registered skills.

        The graph follows a linear retrieve → generate → (continue?) pattern:

        * ``retrieve`` — calls the ``retrieve_knowledge`` skill.
        * ``generate`` — calls the ``generate_answer`` skill or its fallback.
        * Conditional edge — loops back to ``retrieve`` while
          *iteration < max_iterations*, otherwise terminates.
        """
        workflow = StateGraph(ChatState)

        workflow.add_node("retrieve", self._dispatch_retrieve)
        workflow.add_node("generate", self._dispatch_generate)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_conditional_edges(
            "generate",
            self._should_continue,
            {"continue": "retrieve", "end": END},
        )

        self._graph = workflow.compile()

    # ------------------------------------------------------------------
    # Graph nodes
    # ------------------------------------------------------------------

    def _validate_tool(self, skill_name: str) -> None:
        """Check *skill_name* against the tool whitelist.

        Args:
            skill_name: Name of the skill being dispatched.

        Raises:
            PermissionError: If the skill is not in the whitelist.
        """
        if skill_name not in self._allowed_tools:
            raise PermissionError(
                f"Skill '{skill_name}' is not in the allowed tool whitelist. "
                f"Allowed: {list(self._allowed_tools)}"
            )

    def _dispatch_retrieve(self, state: ChatState) -> ChatState:
        """Graph node: retrieve relevant document chunks.

        Dispatches to the registered ``retrieve_knowledge`` skill after
        validating the tool whitelist.
        """
        skill_name = "retrieve_knowledge"
        self._validate_tool(skill_name)

        skill = self._skills.get(skill_name)
        if skill is None:
            raise RuntimeError(
                f"Skill '{skill_name}' is whitelisted but not registered."
            )

        raw_args = {
            "query": state["question"],
            "user_id": state["user_id"],
        }

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(skill.run(raw_args))
        finally:
            loop.close()

        context = result if isinstance(result, str) else "\n\n".join(
            d.get("page_content", str(d)) for d in (result or [])
        )
        state["context"] = context
        state["iteration"] += 1
        return state

    def _dispatch_generate(self, state: ChatState) -> ChatState:
        """Graph node: generate the final answer.

        If a ``generate_answer`` skill is registered and whitelisted, it
        is used.  Otherwise a built-in fallback calls the configured LLM
        directly (mirroring the original ``rag_engine.generate_node``).
        """
        skill_name = "generate_answer"
        skill = self._skills.get(skill_name)

        if skill is not None and skill_name in self._allowed_tools:
            raw_args = {
                "context": state["context"],
                "question": state["question"],
            }
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(skill.run(raw_args))
            finally:
                loop.close()
            state["answer"] = str(result)
            return state

        # Fallback: direct LLM call (original generate_node behaviour)
        logger.debug(
            "No 'generate_answer' skill registered; using built-in LLM fallback."
        )
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
                    "Strictly use the following context to answer the question. "
                    "If the context cannot answer, say the document does not "
                    "contain relevant information.\n\nContext:\n{context}"
                )
            ),
            HumanMessage(content="{question}"),
        ])
        chain = prompt | llm
        response = chain.invoke({
            "context": state["context"],
            "question": state["question"],
        })
        state["answer"] = response.content
        return state

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def _should_continue(self, state: ChatState) -> str:
        """Decide whether to loop back for another retrieval or stop.

        Returns:
            ``"continue"`` if *iteration < max_iterations*,
            ``"end"`` otherwise.
        """
        if state["iteration"] >= self.max_iterations:
            logger.warning(
                "Max iterations (%d) reached; terminating.",
                self.max_iterations,
            )
            return "end"
        return "continue"

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def allowed_tools(self) -> List[str]:
        """Read-only view of the tool whitelist."""
        return list(self._allowed_tools)

    @property
    def registered_skills(self) -> Dict[str, str]:
        """Map of registered skill names to their descriptions."""
        return {name: sk.description for name, sk in self._skills.items()}


# ------------------------------------------------------------------
# Default agent instance (for optional drop-in compatibility)
# ------------------------------------------------------------------
default_agent = Agent()
default_agent.add_skill(RetrieveKnowledgeSkill())
