# profile-forge

A small, dependency-free wrapper around Python's deterministic `cProfile`
profiler. It converts profiler records into structured JSON sorted by
cumulative time, while keeping call counts and source locations visible.

```bash
PYTHONPATH=src python3 -m profile_forge package.module:function --limit 20 --repeat 5
PYTHONPATH=src python3 -m profile_forge package.module:function --sort-by self
PYTHONPATH=src python3 -m profile_forge package.module:function --sort-by self-per-call
PYTHONPATH=src python3 -m profile_forge package.module:function --filename-contains package/
PYTHONPATH=src python3 -m profile_forge package.module:function --function-contains parse
PYTHONPATH=src python3 -m profile_forge package.module:function --minimum-self-seconds 0.001
PYTHONPATH=src python3 -m profile_forge package.module:function --minimum-cumulative-seconds 0.005
PYTHONPATH=src python3 -m unittest discover -s tests
```

The target must be a zero-argument callable. Repeated invocations accumulate in
one profile and the final return value is preserved. Profiling changes execution
characteristics, so these results identify investigation targets rather than
production timing claims.

Function records include total self and cumulative time alongside per-call
values. Self time is divided by total calls; cumulative time is divided by
primitive calls, matching the distinction used by `pstats` for recursive code.
Records can be ranked by cumulative time, self time, total calls, self time per
call, or cumulative time per primitive call. Per-call rankings surface costly
individual invocations while total-time rankings surface aggregate cost; both
can be useful, and neither establishes that the first record is a defect.
Ranking changes which records are selected by `--limit`; it does not change the
underlying profile.
`--filename-contains` applies a literal, case-sensitive source-filename filter
before ranking and `--limit`. It can focus output on application modules, but
excluded library and runtime work still contributes to the profiled execution.
`--function-contains` similarly applies a literal, case-sensitive filter to the
function label supplied by Python's profiler. It can isolate named functions,
but it does not follow their callers or callees and labels for built-ins may use
Python's profiler-specific notation.
`--minimum-self-seconds` removes records below a caller-selected total self-time
floor before ranking and limiting. It is a display filter, not a significance
test, and appropriate thresholds depend on workload duration and profiler
overhead.
`--minimum-cumulative-seconds` applies the same kind of caller-selected floor
to cumulative time. It can retain wrappers that spend little time in their own
body but lead to expensive downstream calls. Cumulative time overlaps across
the call tree, so matching records must not be added together as independent
costs.
