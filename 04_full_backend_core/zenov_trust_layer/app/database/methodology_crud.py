from typing import Any, Optional

from ..storage import (
    methodology_change_impacts,
    methodology_registry,
    methodology_snapshots,
    save_methodology_impact_memory,
    save_methodology_memory,
    save_methodology_snapshot_memory,
)


def save_methodology(methodology: dict[str, Any]) -> None:
    save_methodology_memory(methodology)


def get_methodology(methodology_id: str, version: str) -> Optional[dict[str, Any]]:
    return methodology_registry.get(f"{methodology_id}:{version}")


def list_methodologies() -> list[dict[str, Any]]:
    return sorted(
        methodology_registry.values(),
        key=lambda item: (item.get("methodology_id", ""), item.get("version", "")),
    )


def save_methodology_snapshot(snapshot: dict[str, Any]) -> None:
    save_methodology_snapshot_memory(snapshot)


def list_methodology_snapshots() -> list[dict[str, Any]]:
    return sorted(methodology_snapshots.values(), key=lambda item: item.get("created_at", ""), reverse=True)


def save_methodology_impact(impact: dict[str, Any]) -> None:
    save_methodology_impact_memory(impact)


def get_methodology_impact(impact_id: str) -> Optional[dict[str, Any]]:
    return methodology_change_impacts.get(impact_id)


def list_methodology_impacts() -> list[dict[str, Any]]:
    return sorted(methodology_change_impacts.values(), key=lambda item: item.get("created_at", ""), reverse=True)
