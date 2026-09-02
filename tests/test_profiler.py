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

    def test_respects_limit(self) -> None:
        _, records = profile_callable(profiled_operation, limit=1)
        self.assertEqual(len(records), 1)

    def test_validates_limit_and_target_specification(self) -> None:
        with self.assertRaises(ValueError):
            profile_callable(profiled_operation, limit=0)
        with self.assertRaises(ValueError):
            load_target("missing_separator")


if __name__ == "__main__":
    unittest.main()
