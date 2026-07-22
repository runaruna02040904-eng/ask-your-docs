import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger(__name__)

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "agent.log"


class AgentCallbackHandler(BaseCallbackHandler):
    """LangChain callback handler that logs tool events to a JSON file.

    Each tool invocation produces one JSON line in ``logs/agent.log``:

    * **on_tool_start** — records the tool name, input, and a UTC
      timestamp.
    * **on_tool_end** — records the output and elapsed duration.
    * **on_tool_error** — records the error message.

    Durations are calculated by comparing the *run_id* of matching
    start / end calls.
    """

    def __init__(self, log_path: Optional[str] = None) -> None:
        super().__init__()

        self._log_path: Path = (
            Path(log_path) if log_path else _LOG_FILE
        )
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._file: TextIO = open(
            self._log_path, "a", encoding="utf-8"
        )

        # Tracks start timestamps keyed by run_id (str).
        self._start_times: Dict[str, datetime] = {}

        # Tracks tool names keyed by run_id (str).
        self._tool_names: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Context manager support for clean resource release
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying log file handle."""
        if self._file and not self._file.closed:
            self._file.close()

    def __enter__(self) -> "AgentCallbackHandler":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write(self, record: Dict[str, Any]) -> None:
        """Write a single JSON record on its own line.

        Args:
            record: Dictionary to serialise as JSON.
        """
        self._file.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._file.flush()

    def _utcnow(self) -> datetime:
        """Return the current UTC datetime."""
        return datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # LangGraph / LangChain callback hooks
    # ------------------------------------------------------------------

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Log the start of a tool invocation.

        Args:
            serialized: Serialised tool definition (includes ``"name"``).
            input_str: The raw string input to the tool.
            run_id: Unique identifier for this run.
            parent_run_id: Identifier of the parent run, if any.
            tags: Tags associated with this run.
            metadata: Metadata attached to the run.
            inputs: Structured input dictionary (if available).
        """
        tool_name = serialized.get("name", "unknown")
        now = self._utcnow()

        self._start_times[str(run_id)] = now
        self._tool_names[str(run_id)] = tool_name

        record: Dict[str, Any] = {
            "event": "tool_start",
            "timestamp": now.isoformat(),
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "tool": tool_name,
            "input": input_str,
            "tags": tags or [],
        }
        self._write(record)

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Log the completion of a tool invocation.

        Args:
            output: The value returned by the tool.
            run_id: Unique identifier for this run.
            parent_run_id: Identifier of the parent run, if any.
        """
        now = self._utcnow()
        start_time = self._start_times.pop(str(run_id), None)
        tool_name = self._tool_names.pop(str(run_id), "unknown")

        duration_ms: Optional[float] = None
        if start_time:
            duration_ms = (now - start_time).total_seconds() * 1000

        record: Dict[str, Any] = {
            "event": "tool_end",
            "timestamp": now.isoformat(),
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "tool": tool_name,
            "output": str(output),
            "duration_ms": duration_ms,
        }
        self._write(record)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Log a tool error.

        Args:
            error: The exception that was raised.
            run_id: Unique identifier for this run.
            parent_run_id: Identifier of the parent run, if any.
        """
        now = self._utcnow()
        start_time = self._start_times.pop(str(run_id), None)
        tool_name = self._tool_names.pop(str(run_id), "unknown")

        duration_ms: Optional[float] = None
        if start_time:
            duration_ms = (now - start_time).total_seconds() * 1000

        record: Dict[str, Any] = {
            "event": "tool_error",
            "timestamp": now.isoformat(),
            "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "tool": tool_name,
            "error": f"{type(error).__name__}: {error}",
            "duration_ms": duration_ms,
        }
        self._write(record)

    def flush(self) -> None:
        """Flush the log file buffer."""
        if self._file and not self._file.closed:
            self._file.flush()
