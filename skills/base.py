import logging
from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseSkill(ABC, Generic[T]):
    """Abstract base class for all skills.

    Subclasses must define three class-level attributes and implement
    the :meth:`execute` method.

    Class Attributes:
        name: Human-readable skill name.
        description: Brief description of what the skill does.
        args_schema: A Pydantic model class used to validate and parse
            incoming arguments.

    Usage:
        class MySkill(BaseSkill[MyArgs]):
            name = "my_skill"
            description = "Does something useful."
            args_schema = MyArgs

            async def execute(self, args: MyArgs) -> str:
                ...

        result = await MySkill().run({"param": "value"})
    """

    name: str
    description: str
    args_schema: Type[T]

    @abstractmethod
    async def execute(self, args: T) -> object:
        """Execute the skill logic.

        Args:
            args: Validated Pydantic model instance matching *args_schema*.

        Returns:
            The result of the skill execution.
        """
        ...

    async def run(self, raw_args: dict) -> object:
        """Validate inputs, execute the skill, and handle errors.

        This is the single public entry point for callers. It:

        1. Validates *raw_args* against *args_schema*.
        2. Delegates to :meth:`execute` with the validated model.
        3. Catches and logs any :class:`ValidationError` or unexpected
           exception, then re-raises.

        Args:
            raw_args: Unvalidated dictionary of skill arguments.

        Returns:
            The result produced by :meth:`execute`.

        Raises:
            ValidationError: If *raw_args* does not match *args_schema*.
            Exception: Any exception raised by :meth:`execute`.
        """
        try:
            validated = self.args_schema.model_validate(raw_args)
        except ValidationError:
            logger.exception(
                "Argument validation failed for skill '%s'",
                self.name,
            )
            raise

        try:
            result = await self.execute(validated)
        except Exception:
            logger.exception(
                "Skill '%s' execution failed with args: %s",
                self.name,
                raw_args,
            )
            raise

        return result
