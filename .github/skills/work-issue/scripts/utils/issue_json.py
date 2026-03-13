import json
import sys
from typing import Any, Dict


def read_issue_json(input_value: str) -> Dict[str, Any]:
    if input_value == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("No JSON was provided on stdin")
        return json.loads(raw)

    with open(input_value, "rb") as file:
        payload = file.read()

    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return json.loads(payload.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

    raise ValueError("Unable to parse issue JSON from file")
