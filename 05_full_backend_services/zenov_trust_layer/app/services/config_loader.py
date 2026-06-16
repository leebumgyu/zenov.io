from pathlib import Path
from typing import Any


def _parse_scalar(value: str) -> Any:
    raw = value.strip()
    if raw in {"", "null", "NULL", "None"}:
        return None
    if raw in {"true", "True"}:
        return True
    if raw in {"false", "False"}:
        return False
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    try:
        if "." in raw and raw.count(".") == 1:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def _simple_yaml_load(text: str) -> dict[str, Any]:
    parsed_lines: list[tuple[int, str]] = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        parsed_lines.append((indent, line.strip()))

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(parsed_lines):
            return {}, index
        is_list = parsed_lines[index][1].startswith("- ")
        container: Any = [] if is_list else {}
        while index < len(parsed_lines):
            current_indent, content = parsed_lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                break
            if is_list:
                if not content.startswith("- "):
                    break
                value = content[2:].strip()
                if value:
                    container.append(_parse_scalar(value))
                    index += 1
                else:
                    child, index = parse_block(index + 1, indent + 2)
                    container.append(child)
                continue
            if content.startswith("- "):
                break
            key, sep, value = content.partition(":")
            if not sep:
                index += 1
                continue
            key = key.strip()
            value = value.strip()
            if value:
                container[key] = _parse_scalar(value)
                index += 1
                continue
            next_index = index + 1
            if next_index >= len(parsed_lines) or parsed_lines[next_index][0] <= current_indent:
                container[key] = {}
                index += 1
                continue
            child, index = parse_block(next_index, parsed_lines[next_index][0])
            container[key] = child
        return container, index

    if not parsed_lines:
        return {}
    loaded, _ = parse_block(0, parsed_lines[0][0])
    return loaded if isinstance(loaded, dict) else {}


def load_yaml_config(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback

    try:
        import yaml
    except ImportError:
        with path.open("r", encoding="utf-8") as file:
            loaded = _simple_yaml_load(file.read()) or {}
        return {**fallback, **loaded}

    with path.open("r", encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or {}
    return {**fallback, **loaded}
