"""StateManager: schema-validated, atomically-written repo memory (L34).

Two hard mechanisms:
- Schema-first: a bad write is a REFUSED write (validate before persist).
- Atomic write: temp -> fsync -> os.replace, so a reader never sees a torn
  file. A half-written state is worse than no state (L26: silent corruption
  beats no crash) — the agent would resume against a lying state.
"""
from __future__ import annotations
import json
import os
import re
import tempfile
from pathlib import Path

LAB = Path(__file__).parent


class SchemaError(Exception):
    pass


def validate(data, schema, path="$"):
    t = schema.get("type")
    if t == "object":
        if not isinstance(data, dict):
            raise SchemaError(f"{path}: expected object")
        for k in schema.get("required", []):
            if k not in data:
                raise SchemaError(f"{path}: missing required '{k}'")
        for k, sub in schema.get("properties", {}).items():
            if k in data:
                validate(data[k], sub, f"{path}.{k}")
    elif t == "array":
        if not isinstance(data, list):
            raise SchemaError(f"{path}: expected array (null forbidden)")
        if "items" in schema:
            for i, item in enumerate(data):
                validate(item, schema["items"], f"{path}[{i}]")
    elif t == "string":
        if not isinstance(data, str):
            raise SchemaError(f"{path}: expected string")
        if "enum" in schema and data not in schema["enum"]:
            raise SchemaError(f"{path}: '{data}' not in enum {schema['enum']}")
        if "pattern" in schema and not re.match(schema["pattern"], data):
            raise SchemaError(f"{path}: '{data}' fails pattern {schema['pattern']}")
    elif t == "integer":
        if not isinstance(data, int) or isinstance(data, bool):
            raise SchemaError(f"{path}: expected integer")
    elif t == "boolean":
        if not isinstance(data, bool):
            raise SchemaError(f"{path}: expected boolean")


def atomic_write(target: Path, data: dict):
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)  # atomic on POSIX and Windows
    except Exception:
        os.unlink(tmp)
        raise


class StateManager:
    def __init__(self, state_path, schema_path):
        self.state_path = Path(state_path)
        self.schema = json.loads(Path(schema_path).read_text())

    def load(self):
        data = json.loads(self.state_path.read_text())
        validate(data, self.schema)   # refuse to load bad state
        return data

    def commit(self, data):
        validate(data, self.schema)   # a bad write is a refused write
        atomic_write(self.state_path, data)


if __name__ == "__main__":
    sm = StateManager(LAB / "agent_state.json", LAB / "agent_state.schema.json")

    print("=== load + validate real state ===")
    st = sm.load()
    print("  OK — active_task_id:", st["active_task_id"], "| schema v", st["schema_version"])

    print("\n=== bad write: action='edited' (not in enum) ===")
    bad = json.loads((LAB / "agent_state.json").read_text())
    bad["touched_files"].append({"path": "x.py", "action": "edited"})
    try:
        sm.commit(bad)
        print("  BUG: accepted a bad write")
    except SchemaError as e:
        print("  REFUSED:", e)

    print("\n=== bad write: active_task_id='xyz' (fails pattern ^T\\d+$) ===")
    bad2 = json.loads((LAB / "agent_state.json").read_text())
    bad2["active_task_id"] = "xyz"
    try:
        sm.commit(bad2)
        print("  BUG: accepted a bad write")
    except SchemaError as e:
        print("  REFUSED:", e)

    print("\n(real agent_state.json untouched — bad writes never reached disk)")
