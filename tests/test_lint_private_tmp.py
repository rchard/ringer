#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ringer import (  # noqa: E402
    AppConfig,
    ArtifactConfig,
    EngineConfig,
    EvalConfig,
    Manifest,
    engine_has_private_tmp,
    lint_manifest,
)

GOOD_CHECK = "test -s out.txt || { echo 'FAIL: out.txt missing'; exit 1; }"


class PrivateTmpLintTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.workdir = self.root / "work"

    def script(self, name: str, body: str) -> str:
        path = self.root / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)
        return str(path)

    def engine(self, bin_path: str, private_tmp: bool | None = None) -> EngineConfig:
        return EngineConfig(
            name="boxed",
            bin=bin_path,
            args_template=("{prompt}",),
            full_access_args=(),
            sandbox_args=(),
            private_tmp=private_tmp,
        )

    def config(self, engine: EngineConfig) -> AppConfig:
        return AppConfig(
            path=None,
            identity_default=None,
            state_dir=self.root / "state",
            dashboard_port_base=8787,
            hud_port=8700,
            hud_app_path=None,
            allow_full_access=True,
            eval=EvalConfig(backend="jsonl", jsonl_path=self.root / "eval.jsonl"),
            engines={engine.name: engine},
            artifact=ArtifactConfig(
                enabled=False,
                out_template=str(self.root / "live.html"),
                report_template=str(self.root / "report.html"),
                index_out=self.root / "index.html",
            ),
        )

    def findings(self, spec: str, engine: EngineConfig, **task_extra: object) -> list[str]:
        task = {
            "key": "t1",
            "spec": "Do the work described here carefully and completely. " + spec + " " * 40,
            "check": GOOD_CHECK,
            "engine": "boxed",
            "expect_files": ["out.txt"],
            "verified": "out.txt exists",
            **task_extra,
        }
        manifest = Manifest.from_obj(
            {"run_name": "pt", "workdir": str(self.workdir), "tasks": [task]}
        )
        found = lint_manifest(manifest, config=self.config(engine), allow_noncanonical_route=True)
        return [f for f in found if "private /tmp" in f]

    def boxed_bin(self) -> str:
        return self.script("boxed.sh", "#!/bin/sh\nexec bwrap --tmpfs /tmp \"$@\"\n")

    def plain_bin(self) -> str:
        return self.script("plain.sh", "#!/bin/sh\nexec true\n")

    def test_flagged_when_bin_has_tmpfs(self) -> None:
        found = self.findings("Run git apply /tmp/x/round1.patch now.", self.engine(self.boxed_bin()))
        self.assertEqual(len(found), 1)
        self.assertIn("/tmp/x/round1.patch", found[0])
        self.assertIn("boxed", found[0])

    def test_not_flagged_without_tmpfs(self) -> None:
        self.assertEqual(self.findings("Read /tmp/x/in.txt", self.engine(self.plain_bin())), [])

    def test_explicit_override(self) -> None:
        self.assertEqual(self.findings("Read /tmp/x/in.txt", self.engine(self.boxed_bin(), False)), [])
        self.assertEqual(len(self.findings("Read /tmp/x/in.txt", self.engine(self.plain_bin(), True))), 1)

    def test_full_access_not_flagged(self) -> None:
        self.assertEqual(
            self.findings("Read /tmp/x/in.txt", self.engine(self.boxed_bin()), full_access=True), []
        )

    def test_path_inside_workdir_not_flagged(self) -> None:
        self.workdir = Path(tempfile.mkdtemp(prefix="ringer-pt-", dir="/tmp"))
        self.addCleanup(self.workdir.rmdir)
        inner = f"{self.workdir}/in.txt"
        self.assertEqual(self.findings(f"Read {inner}.", self.engine(self.boxed_bin())), [])

    def test_path_outside_tmp_not_flagged(self) -> None:
        self.assertEqual(self.findings("Read /var/data/in.txt", self.engine(self.boxed_bin())), [])

    def test_missing_bin_does_not_raise(self) -> None:
        self.assertFalse(engine_has_private_tmp(self.engine(str(self.root / "nope"))))
        self.assertFalse(engine_has_private_tmp(self.engine("definitely-not-a-real-bin-xyz")))
        self.assertFalse(engine_has_private_tmp(self.engine(str(self.root))))

    def test_duplicate_paths_reported_once(self) -> None:
        found = self.findings("Read /tmp/a.txt then /tmp/a.txt and (/tmp/b.txt).", self.engine(self.boxed_bin()))
        self.assertEqual(len(found), 2)


if __name__ == "__main__":
    unittest.main()
