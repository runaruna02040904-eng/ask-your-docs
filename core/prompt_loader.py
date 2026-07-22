from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

_YAML_PATH = (
    Path(__file__).resolve().parent.parent / "prompts" / "generate_answer.yaml"
)


@lru_cache(maxsize=1)
def _load_yaml() -> Dict[str, Any]:
    """Load and cache the full YAML file contents.

    Returns:
        The parsed YAML dictionary.  The result is cached via
        ``lru_cache`` so repeated calls return without re-reading
        the file.
    """
    with open(_YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt(version: str) -> Dict[str, str]:
    """Load a prompt template version from ``generate_answer.yaml``.

    Args:
        version: The version key to look up (e.g. ``"v1"``, ``"v2"``).

    Returns:
        A dictionary with keys ``"system"`` and ``"human"`` containing
        the corresponding prompt text.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        KeyError: If *version* does not exist under
            ``generate_answer`` in the YAML file.
    """
    if not _YAML_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {_YAML_PATH}"
        )

    data = _load_yaml()

    try:
        prompt_data = data["generate_answer"][version]
    except KeyError:
        available = list(data.get("generate_answer", {}).keys())
        raise KeyError(
            f"Prompt version '{version}' not found in "
            f"{_YAML_PATH.name}. Available versions: {available}"
        )

    return {
        "system": prompt_data.get("system", ""),
        "human": prompt_data.get("human", ""),
    }
