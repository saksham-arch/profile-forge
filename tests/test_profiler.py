import unittest

from profile_forge import profile_callable
from profile_forge.__main__ import load_target


def profiled_operation() -> int:
    return sum(range(100))


class ProfilerTests(unittest.TestCase):
    def test_returns_result_and_structured_records(self) -> None:
        result, records = profile_callable(profiled_operation, limit=50)
        self.assertEqual(result, 4950)
        functions = {record.function for record in records}
        self.assertIn("profiled_operation", functions)
        self.assertTrue(all(record.cumulative_seconds >= 0 for record in records))
        self.assertTrue(all(record.self_per_call_seconds >= 0 for record in records))

    def test_respects_limit(self) -> None:
        _, records = profile_callable(profiled_operation, limit=1)
        self.assertEqual(len(records), 1)

    def test_validates_limit_and_target_specification(self) -> None:
        with self.assertRaises(ValueError):
            profile_callable(profiled_operation, limit=0)
        with self.assertRaises(ValueError):
            load_target("missing_separator")

    def test_profiles_repeated_invocations(self) -> None:
        calls = 0

        def operation() -> int:
            nonlocal calls
            calls += 1
            return calls

        result, records = profile_callable(operation, limit=50, repeat=3)
        self.assertEqual(result, 3)
        self.assertEqual(calls, 3)
        operation_stat = next(item for item in records if item.function == "operation")
        self.assertEqual(operation_stat.total_calls, 3)
        self.assertAlmostEqual(
            operation_stat.self_per_call_seconds * operation_stat.total_calls,
            operation_stat.self_seconds,
        )
        self.assertAlmostEqual(
            operation_stat.cumulative_per_primitive_call_seconds
            * operation_stat.primitive_calls,
            operation_stat.cumulative_seconds,
        )

    def test_rejects_invalid_repeat(self) -> None:
        with self.assertRaises(ValueError):
            profile_callable(profiled_operation, repeat=0)

    def test_supports_self_time_and_call_count_rankings(self) -> None:
        _, by_self = profile_callable(profiled_operation, limit=50, sort_by="self")
        _, by_calls = profile_callable(profiled_operation, limit=50, sort_by="calls")
        self.assertEqual(
            [item.self_seconds for item in by_self],
            sorted((item.self_seconds for item in by_self), reverse=True),
        )
        self.assertEqual(
            [item.total_calls for item in by_calls],
            sorted((item.total_calls for item in by_calls), reverse=True),
        )

    def test_rejects_unknown_ranking(self) -> None:
        with self.assertRaises(ValueError):
            profile_callable(profiled_operation, sort_by="unknown")

    def test_filters_records_by_literal_filename_text(self) -> None:
        _, records = profile_callable(
            profiled_operation,
            limit=50,
            filename_contains="test_profiler.py",
        )
        self.assertIn("profiled_operation", {item.function for item in records})
        self.assertTrue(
            all("test_profiler.py" in item.filename for item in records)
        )

    def test_filename_filter_is_applied_before_limit(self) -> None:
        _, records = profile_callable(
            profiled_operation,
            limit=1,
            filename_contains="test_profiler.py",
        )
        self.assertEqual(len(records), 1)
        self.assertIn("test_profiler.py", records[0].filename)

    def test_rejects_empty_filename_filter(self) -> None:
        with self.assertRaises(ValueError):
            profile_callable(profiled_operation, filename_contains="")


if __name__ == "__main__":
    unittest.main()
