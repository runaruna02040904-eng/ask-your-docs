from datetime import datetime

from pydantic import BaseModel

from .base import BaseSkill


class TimeInput(BaseModel):
    """Input model for TimeSkill.

    An empty model — no arguments are required to fetch the current time.
    """


class TimeSkill(BaseSkill[TimeInput]):
    """Skill that returns the current system time.

    Useful for answering "what time is it" questions or injecting a
    timestamp into a workflow.

    Usage:
        skill = TimeSkill()
        result = await skill.run({})          # → "2026-07-22 11:00:00"
        result = await skill.run({"ignored": 1})  # extra fields are dropped
    """

    name: str = "time_skill"
    description: str = (
        "Return the current system time formatted as "
        "YYYY-MM-DD HH:MM:SS."
    )
    args_schema: type[TimeInput] = TimeInput

    async def execute(self, args: TimeInput) -> str:
        """Return the current time as a formatted string.

        Args:
            args: Unused; kept for interface compatibility.

        Returns:
            Current system time in ``YYYY-MM-DD HH:MM:SS`` format.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
