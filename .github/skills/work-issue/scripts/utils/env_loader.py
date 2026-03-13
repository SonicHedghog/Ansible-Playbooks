import os
from pathlib import Path
from typing import Optional


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
        return value[1:-1]
    return value


def _apply_env_file(file_path: Path, *, override: bool = False) -> bool:
    if not file_path.exists() or not file_path.is_file():
        return False

    loaded_any = False
    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        if not key:
            continue

        value = _strip_quotes(raw_value)
        if override or key not in os.environ:
            os.environ[key] = value
        loaded_any = True

    return loaded_any


def load_env(start_dir: Optional[Path] = None, *, override: bool = False) -> Optional[Path]:
    base_dir = (start_dir or Path.cwd()).resolve()

    for directory in [base_dir, *base_dir.parents]:
        env_path = directory / ".env"
        if _apply_env_file(env_path, override=override):
            return env_path

    return None
