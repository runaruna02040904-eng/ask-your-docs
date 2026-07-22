import asyncio
import logging

from pydantic import BaseModel, Field

from .base import BaseSkill

logger = logging.getLogger(__name__)


class AskHumanInput(BaseModel):
    """Input model for AskHumanSkill.

    Attributes:
        reason: The justification for requesting human approval,
            e.g. why the action requires manual review.
    """

    reason: str = Field(
        ...,
        description="Reason for requesting human approval.",
    )


class AskHumanSkill(BaseSkill[AskHumanInput]):
    """Skill that simulates a human-in-the-loop approval workflow.

    Logs the approval reason (simulating a notification to a human
    reviewer), waits 30 seconds for the simulated review, and
    returns the approval result.

    Usage:
        skill = AskHumanSkill()
        result = await skill.run(
            {"reason": "Approve deletion of document #42"}
        )
        # → {"approved": True}
    """

    name: str = "ask_human"
    description: str = (
        "Simulate a human-in-the-loop approval.  Logs the request, "
        "waits 30 seconds for a simulated review, then returns the "
        "approval decision."
    )
    args_schema: type[AskHumanInput] = AskHumanInput

    async def execute(self, args: AskHumanInput) -> dict[str, bool]:
        """Simulate sending a notification and awaiting human approval.

        Args:
            args: Validated input containing the *reason* for the
                approval request.

        Returns:
            A dictionary with a single key ``"approved"`` whose value
            is ``True`` if the simulated human approved, ``False``
            otherwise.
        """
        logger.info("=" * 60)
        logger.info("HUMAN APPROVAL REQUESTED")
        logger.info("Reason: %s", args.reason)
        logger.info("Waiting 30 seconds for simulated review …")
        logger.info("=" * 60)

        await asyncio.sleep(30)

        logger.info("Simulated human approved the request.")
        return {"approved": True}
