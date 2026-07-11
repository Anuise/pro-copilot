import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / ".harness" / "task.example.json"
SCHEMA = ROOT / ".harness" / "schema.json"
PHASES = ("intake", "design", "plan", "implement", "verify", "review", "done", "blocked")
STANDARD_PHASES = PHASES[:-1]


def type_matches(expected: str, value: Any) -> bool:
    types = {
        "array": list,
        "integer": int,
        "null": type(None),
        "object": dict,
        "string": str,
    }
    return isinstance(value, types[expected]) and not (expected == "integer" and isinstance(value, bool))


def validate_schema(schema: dict[str, Any], value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    expected_types = expected if isinstance(expected, list) else [expected] if expected else []
    if expected_types and not any(type_matches(item, value) for item in expected_types):
        return [f"{path} 型別必須是 {' 或 '.join(expected_types)}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path} 必須是 {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} 必須是允許值之一")
    if isinstance(value, str) and len(value.strip()) < schema.get("minLength", 0):
        errors.append(f"{path} 不得空白")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path} 至少需要 {schema['minItems']} 項")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_schema(item_schema, item, f"{path}[{index}]"))
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"缺少必要欄位：{path}.{key}")
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys():
                errors.append(f"不允許額外欄位：{path}.{key}")
        for key in value.keys() & properties.keys():
            errors.extend(validate_schema(properties[key], value[key], f"{path}.{key}"))
    return errors


def validate_phase_history(history: list[str], phase: str) -> list[str]:
    if history[0] != "intake" or history[-1] != phase:
        return ["phase_history 必須從 intake 開始，並以目前 phase 結束"]

    last_work_phase = "intake"
    for previous, current in zip(history, history[1:]):
        if current == "blocked":
            if previous in ("blocked", "done"):
                return ["phase_history 的 blocked 轉換無效"]
            last_work_phase = previous
        elif previous == "blocked":
            if current != last_work_phase:
                return ["phase_history 解除 blocked 後必須返回原階段"]
        elif previous not in STANDARD_PHASES or STANDARD_PHASES.index(current) != STANDARD_PHASES.index(previous) + 1:
            return ["phase_history 不得跳過或倒退標準階段"]
    return []


def supports_semantic_validation(state: Any) -> bool:
    if not isinstance(state, dict):
        return False
    try:
        return all(
            (
                isinstance(state["phase"], str),
                isinstance(state["phase_history"], list) and bool(state["phase_history"]),
                all(isinstance(item, str) for item in state["phase_history"]),
                isinstance(state["requirements"], dict),
                isinstance(state["requirements"]["success_criteria"], list),
                isinstance(state["design"], dict),
                isinstance(state["design"]["approach"], str),
                isinstance(state["plan"], list),
                isinstance(state["changes"], dict),
                isinstance(state["changes"]["files"], list),
                isinstance(state["changes"]["summary"], str),
                isinstance(state["verification"], list),
                all(isinstance(item, dict) and isinstance(item["status"], str) for item in state["verification"]),
                isinstance(state["review"], dict),
                isinstance(state["review"]["status"], str),
                isinstance(state["review"]["notes"], str),
                isinstance(state["open_items"], list),
            )
        )
    except (KeyError, TypeError):
        return False


def validate(state: Any) -> list[str]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = validate_schema(schema, state)
    if not supports_semantic_validation(state):
        return errors

    phase = state["phase"]
    history = state["phase_history"]
    effective_phase = history[-2] if phase == "blocked" and len(history) > 1 else phase
    requirements = state["requirements"]
    design = state["design"]
    changes = state["changes"]
    review = state["review"]
    verification = state["verification"]
    errors.extend(validate_phase_history(history, phase))

    if effective_phase != "intake":
        if not requirements["success_criteria"]:
            errors.append("design 之後必須填寫 requirements.success_criteria")

    if effective_phase in ("plan", "implement", "verify", "review", "done"):
        if not design["approach"].strip():
            errors.append("plan 之後必須填寫 design.approach")

    if effective_phase in ("implement", "verify", "review", "done") and not state["plan"]:
        errors.append("implement 之後必須填寫 plan")

    if effective_phase in ("verify", "review", "done"):
        if not changes["files"]:
            errors.append("verify 之後必須填寫 changes.files")
        if not changes["summary"].strip():
            errors.append("verify 之後必須填寫 changes.summary")

    if effective_phase in ("review", "done") and (not verification or verification[-1]["status"] != "pass"):
        errors.append("review 之後最後一筆 verification 必須是 pass")

    if phase == "done":
        if review["status"] != "pass":
            errors.append("done 必須設定 review.status 為 pass")
        if not review["notes"].strip():
            errors.append("done 必須填寫 review.notes")
        if state["open_items"]:
            errors.append("done 不得保留 open_items")

    return errors


def init_task(target: Path) -> int:
    if target.exists():
        print(f"錯誤：{target} 已存在，拒絕覆寫", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(EXAMPLE, target)
    print(f"已建立 harness 狀態檔：{target}")
    return 0


def check_task(target: Path) -> int:
    try:
        state = json.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"錯誤：找不到狀態檔 {target}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"錯誤：JSON 格式無效（第 {error.lineno} 行，第 {error.colno} 欄）", file=sys.stderr)
        return 1

    errors = validate(state)
    if errors:
        for error in errors:
            print(f"錯誤：{error}", file=sys.stderr)
        return 1

    print(f"harness 檢查通過：{target}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="通用 AI 開發 harness 狀態工具")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "check"):
        subcommand = commands.add_parser(command)
        subcommand.add_argument("path", type=Path)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    if arguments.command == "init":
        return init_task(arguments.path)
    return check_task(arguments.path)


if __name__ == "__main__":
    raise SystemExit(main())
