import argparse
from dataclasses import asdict
import importlib
import json
from typing import Callable

from .profiler import profile_callable


def load_target(specification: str) -> Callable[[], object]:
    try:
        module_name, attribute = specification.split(":", maxsplit=1)
    except ValueError as error:
        raise ValueError("target must use module:function syntax") from error
    target = getattr(importlib.import_module(module_name), attribute)
    if not callable(target):
        raise TypeError("target must be callable")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile a zero-argument Python callable")
    parser.add_argument("target", help="module:function")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument(
        "--filename-contains",
        help="keep records whose source filename contains this literal text",
    )
    parser.add_argument(
        "--function-contains",
        help="keep records whose profiler function label contains this literal text",
    )
    parser.add_argument(
        "--minimum-self-seconds",
        type=float,
        default=0,
        help="keep records with at least this much total self time",
    )
    parser.add_argument(
        "--minimum-cumulative-seconds",
        type=float,
        default=0,
        help="keep records with at least this much cumulative time",
    )
    parser.add_argument(
        "--sort-by",
        choices=("cumulative", "self", "calls"),
        default="cumulative",
    )
    args = parser.parse_args()
    _, records = profile_callable(
        load_target(args.target),
        args.limit,
        repeat=args.repeat,
        sort_by=args.sort_by,
        filename_contains=args.filename_contains,
        function_contains=args.function_contains,
        minimum_self_seconds=args.minimum_self_seconds,
        minimum_cumulative_seconds=args.minimum_cumulative_seconds,
    )
    print(json.dumps([asdict(record) for record in records], indent=2))


if __name__ == "__main__":
    main()
