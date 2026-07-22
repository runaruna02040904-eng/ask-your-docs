from datetime import datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from skills.time_skill import TimeSkill, TimeInput


class TestTimeSkill:
    """Unit tests for TimeSkill."""

    @patch("skills.time_skill.datetime")
    async def test_execute_returns_formatted_time(self, mock_datetime):
        """execute() should return the current time in YYYY-MM-DD HH:MM:SS."""
        mock_datetime.now.return_value = datetime(2026, 7, 22, 11, 5, 30)

        skill = TimeSkill()
        result = await skill.run({})

        assert result == "2026-07-22 11:05:30"

    async def test_execute_output_format(self):
        """Output format should be exactly YYYY-MM-DD HH:MM:SS."""
        skill = TimeSkill()
        result = await skill.run({})

        # Verify structure without knowing the exact value
        parts = result.split(" ")
        assert len(parts) == 2, "Result must have date and time separated by space"

        date_part, time_part = parts
        assert len(date_part.split("-")) == 3, "Date must be YYYY-MM-DD"
        assert len(time_part.split(":")) == 3, "Time must be HH:MM:SS"

        # Verify each fragment is purely numeric
        assert all(p.isdigit() for p in date_part.split("-"))
        assert all(p.isdigit() for p in time_part.split(":"))

    async def test_execute_with_empty_dict(self):
        """An empty dict is valid input since TimeInput has no fields."""
        skill = TimeSkill()
        result = await skill.run({})
        assert isinstance(result, str)
        assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS" is fixed-length

    async def test_execute_with_extra_fields(self):
        """Extra fields should be silently dropped (Pydantic v2 default)."""
        skill = TimeSkill()
        try:
            result = await skill.run({"unexpected": "value"})
            assert isinstance(result, str)
        except ValidationError:
            pytest.fail("Extra fields should not cause validation errors.")


class TestTimeInput:
    """Unit tests for the TimeInput Pydantic model."""

    def test_construct_empty(self):
        """TimeInput should construct without any arguments."""
        m = TimeInput()
        assert isinstance(m, TimeInput)
        assert dict(m) == {}

    def test_construct_with_dict(self):
        """TimeInput should accept an empty dict."""
        m = TimeInput.model_validate({})
        assert isinstance(m, TimeInput)
