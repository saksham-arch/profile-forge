import cProfile
from dataclasses import dataclass
import pstats
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class FunctionStat:
    filename: str
    line: int
    function: str
    primitive_calls: int
    total_calls: int
    self_seconds: float
    self_per_call_seconds: float
    cumulative_seconds: float
    cumulative_per_primitive_call_seconds: float


def profile_callable(
    operation: Callable[[], T],
    limit: int = 20,
    *,
    repeat: int = 1,
    sort_by: str = "cumulative",
    filename_contains: Optional[str] = None,
) -> tuple[T, list[FunctionStat]]:
    if limit < 1:
        raise ValueError("limit must be positive")
    if repeat < 1:
        raise ValueError("repeat must be positive")
    if sort_by not in {"cumulative", "self", "calls"}:
        raise ValueError("sort_by must be cumulative, self, or calls")
    if filename_contains == "":
        raise ValueError("filename_contains must not be empty")
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        for _ in range(repeat):
            result = operation()
    finally:
        profiler.disable()
    raw_stats = pstats.Stats(profiler).stats
    records = [
        FunctionStat(
            filename=key[0],
            line=key[1],
            function=key[2],
            primitive_calls=value[0],
            total_calls=value[1],
            self_seconds=value[2],
            self_per_call_seconds=value[2] / value[1],
            cumulative_seconds=value[3],
            cumulative_per_primitive_call_seconds=value[3] / value[0],
        )
        for key, value in raw_stats.items()
        if filename_contains is None or filename_contains in key[0]
    ]
    sort_keys = {
        "cumulative": lambda item: (
            -item.cumulative_seconds,
            -item.self_seconds,
            item.filename,
            item.line,
            item.function,
        ),
        "self": lambda item: (
            -item.self_seconds,
            -item.cumulative_seconds,
            item.filename,
            item.line,
            item.function,
        ),
        "calls": lambda item: (
            -item.total_calls,
            -item.cumulative_seconds,
            item.filename,
            item.line,
            item.function,
        ),
    }
    records.sort(key=sort_keys[sort_by])
    return result, records[:limit]
