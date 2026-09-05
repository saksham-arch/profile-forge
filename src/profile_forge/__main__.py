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
    args = parser.parse_args()
    _, records = profile_callable(
        load_target(args.target), args.limit, repeat=args.repeat
    )
    print(json.dumps([asdict(record) for record in records], indent=2))


if __name__ == "__main__":
    main()
