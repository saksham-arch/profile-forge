# profile-forge

A small, dependency-free wrapper around Python's deterministic `cProfile`
profiler. It converts profiler records into structured JSON sorted by
cumulative time, while keeping call counts and source locations visible.

```bash
PYTHONPATH=src python3 -m profile_forge package.module:function --limit 20
python3 -m unittest discover -s tests
```

The target must be a zero-argument callable. Profiling changes execution
characteristics, so these results identify investigation targets rather than
production timing claims.

