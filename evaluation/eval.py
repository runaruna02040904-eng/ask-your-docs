#!/usr/bin/env python3
"""Evaluate the AskYourDocs Agent against a set of test cases.

For each test case the Agent is invoked, then a DeepSeek LLM judges
the answer quality on a 1-5 scale.  The script exits with code 1 if
the average score falls below 3.5.
"""

import json
import logging
import re
import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from core.agent import default_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

TEST_CASES_PATH = Path(__file__).parent / "test_cases.json"

JUDGE_PROMPT = """You are a strict answer quality evaluator for a
document-based Q&A system.  Given a user question, a piece of reference
context (hint), and the system's answer, rate the answer on a scale
of 1 to 5 using the criteria below.

Criteria:
- 5 – Correct, complete, and concise; grounded in the context.
- 4 – Mostly correct with minor omissions or imprecision.
- 3 – Partially correct but misses key details or is slightly vague.
- 2 – Largely incorrect or irrelevant to the question.
- 1 – Completely wrong, nonsensical, or empty.

Output only a single integer (1-5) on its own line.

Question: {question}
Reference context hint: {context_hint}
System answer: {answer}

Score:"""


def load_test_cases(path: Path) -> list[dict]:
    """Load test cases from a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        A list of test-case dictionaries.

    Raises:
        FileNotFoundError: If *path* does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with open(path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    if not isinstance(cases, list):
        raise TypeError(
            f"Expected a JSON array at top level, got {type(cases).__name__}."
        )
    return cases


def judge_answer(
    question: str,
    context_hint: str,
    answer: str,
    llm: ChatOpenAI,
) -> int:
    """Ask the LLM to score a single answer.

    Args:
        question: The user's original question.
        context_hint: Reference context snippet for scoring.
        answer: The answer produced by the Agent.
        llm: A ChatOpenAI instance configured as the judge.

    Returns:
        An integer score between 1 and 5 (inclusive).
    """
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=JUDGE_PROMPT),
        HumanMessage(
            content=(
                "Question: {question}\n"
                "Reference context hint: {context_hint}\n"
                "System answer: {answer}"
            )
        ),
    ])
    chain = prompt | llm
    response = chain.invoke({
        "question": question,
        "context_hint": context_hint,
        "answer": answer,
    })

    content = response.content.strip()
    match = re.search(r"\b([1-5])\b", content)
    if match:
        return int(match.group(1))

    logger.warning(
        "Could not parse score from LLM response: %r", content
    )
    return 3  # conservative fallback


def main() -> None:
    """Run the evaluation and exit with the appropriate code."""
    if not TEST_CASES_PATH.exists():
        logger.error("Test cases file not found: %s", TEST_CASES_PATH)
        sys.exit(1)

    cases = load_test_cases(TEST_CASES_PATH)
    logger.info("Loaded %d test case(s).", len(cases))

    judge_llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=DEEPSEEK_API_KEY,
        openai_api_base=DEEPSEEK_BASE_URL,
        temperature=0,
    )

    scores: list[int] = []
    results: list[dict] = []

    for i, case in enumerate(cases, start=1):
        question = case.get("question", "")
        user_id = case.get("user_id", 1)
        context_hint = case.get("context_hint", "")

        if not question:
            logger.warning("Skipping case %d: missing 'question'.", i)
            continue

        logger.info("[%d/%d] Question: %s", i, len(cases), question)

        try:
            answer = default_agent.invoke(user_input=question, user_id=user_id)
        except Exception:
            logger.exception(
                "[%d/%d] Agent.invoke failed, skipping.",
                i,
                len(cases),
            )
            continue

        score = judge_answer(question, context_hint, answer, judge_llm)
        scores.append(score)
        results.append({"question": question, "answer": answer, "score": score})

        logger.info("  Score: %d/5 | Answer: %s", score, answer[:80])

    # --- Report ---
    if not scores:
        logger.error("No test cases were successfully evaluated.")
        sys.exit(1)

    average = sum(scores) / len(scores)
    print("\n" + "=" * 50)
    print(f"  Total cases evaluated : {len(scores)}")
    print(f"  Average score         : {average:.2f} / 5")
    print(f"  Threshold             : 3.50 / 5")
    print("=" * 50)

    if average < 3.5:
        logger.error(
            "Average score %.2f is below threshold 3.50 — failing.",
            average,
        )
        sys.exit(1)

    logger.info("Evaluation passed (avg = %.2f).", average)


if __name__ == "__main__":
    main()
