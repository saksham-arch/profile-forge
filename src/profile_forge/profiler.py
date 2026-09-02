import cProfile
from dataclasses import dataclass
import pstats
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class FunctionStat:
    filename: str
    line: int
    function: str
    primitive_calls: int
    total_calls: int
    self_seconds: float
    cumulative_seconds: float


def profile_callable(operation: Callable[[], T], limit: int = 20) -> tuple[T, list[FunctionStat]]:
    if limit < 1:
        raise ValueError("limit must be positive")
    profiler = cProfile.Profile()
    result = profiler.runcall(operation)
    raw_stats = pstats.Stats(profiler).stats
    records = [
        FunctionStat(
            filename=key[0],
            line=key[1],
            function=key[2],
            primitive_calls=value[0],
            total_calls=value[1],
            self_seconds=value[2],
            cumulative_seconds=value[3],
        )
        for key, value in raw_stats.items()
    ]
    records.sort(key=lambda item: (-item.cumulative_seconds, -item.self_seconds, item.function))
    return result, records[:limit]

