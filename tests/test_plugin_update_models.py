from __future__ import annotations

import unittest

from scripts.plugin_update_flow.models import (
    Artifact,
    ExitCode,
    RunReport,
    SemVer,
)


class SemVerTests(unittest.TestCase):
    def test_orders_release_and_prerelease_versions(self) -> None:
        self.assertLess(SemVer.parse("1.1.0"), SemVer.parse("1.1.1"))
        self.assertLess(SemVer.parse("1.2.0-beta.2"), SemVer.parse("1.2.0"))
        self.assertLess(SemVer.parse("1.2.0-beta.2"), SemVer.parse("1.2.0-beta.10"))

    def test_rejects_non_semver_and_numeric_prerelease_with_leading_zero(self) -> None:
        for value in ("v1.2.3", "1.2", "1.2.3-01"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                SemVer.parse(value)

    def test_build_metadata_does_not_change_equality_or_hash(self) -> None:
        left = SemVer.parse("1.2.3+build.1")
        right = SemVer.parse("1.2.3+build.2")

        self.assertEqual(left, right)
        self.assertEqual(hash(left), hash(right))


class ReportTests(unittest.TestCase):
    def test_serializes_stable_schema_without_enum_objects(self) -> None:
        baseline = Artifact("old", "a" * 40, "1.1.0", "sha256:old")
        target = Artifact("origin/main", "b" * 40, "1.1.1", "sha256:new")
        report = RunReport.new("run-1", "test", baseline, target)
        report.result = "passed"

        value = report.to_dict()

        self.assertEqual(1, value["schemaVersion"])
        self.assertEqual("1.1.1", value["target"]["version"])
        self.assertEqual("not-requested", value["promotion"]["result"])
        self.assertEqual(0, ExitCode.SUCCESS)


if __name__ == "__main__":
    unittest.main()
