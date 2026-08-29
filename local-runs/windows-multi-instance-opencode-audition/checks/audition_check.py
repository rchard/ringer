#!/usr/bin/env python3
"""Validate one cell of the Windows multi-instance opencode audition.

Ringer's own check-command timeout is a hard 60s (CHECK_TIMEOUT_S in
ringer.py), and real `opencode` subprocess invocations have enough startup
latency that re-executing proof.py here would blow that budget. So the
worker must run proof.py THEMSELVES during their own session (which has a
much longer timeout_s) and save both its raw output and a structured
result JSON; this check only reads and independently verifies those files,
which is fast.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPORT_HEADINGS = (
    "Model Self-Report",
    "Findings",
    "Design Decisions",
    "Limitations",
)
MAX_REPORT_WORDS = 1800


def fail(name: str, detail: str) -> str:
    return f"FAIL [{name}]: {detail}"


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def has_heading(text: str, heading: str) -> bool:
    return bool(re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.IGNORECASE | re.MULTILINE))


def output_tail(text: str, limit: int = 3000) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[-limit:]


def sha256_of(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--launch-ps1", required=True, type=Path)
    parser.add_argument("--proof", required=True, type=Path)
    parser.add_argument("--proof-log", required=True, type=Path)
    parser.add_argument("--proof-result", required=True, type=Path)
    parser.add_argument("--expected-model", required=True)
    parser.add_argument("--session-validator", required=True)
    parser.add_argument("--real-config-path", required=True, type=Path)
    parser.add_argument("--real-config-sha256", required=True)
    parser.add_argument("--real-auth-path", required=True, type=Path)
    parser.add_argument("--real-auth-sha256", required=True)
    args = parser.parse_args()

    failures: list[str] = []

    def check_untouched() -> None:
        real_cfg_now = sha256_of(args.real_config_path)
        if real_cfg_now != args.real_config_sha256:
            failures.append(
                fail(
                    "modified_real_config",
                    f"{args.real_config_path} changed (sha256 {real_cfg_now} != baseline {args.real_config_sha256}). "
                    "The worker touched the user's real opencode config -- this is a hard safety violation.",
                )
            )
        real_auth_now = sha256_of(args.real_auth_path)
        if real_auth_now != args.real_auth_sha256:
            failures.append(
                fail(
                    "modified_real_auth",
                    f"{args.real_auth_path} changed (sha256 {real_auth_now} != baseline {args.real_auth_sha256}). "
                    "The worker touched the user's real opencode auth file -- this is a hard safety violation.",
                )
            )

    check_untouched()

    report = args.report
    if not report.is_file():
        failures.append(fail("missing_report", f"{report} does not exist"))
        report_text = ""
    elif report.stat().st_size == 0:
        failures.append(fail("empty_report", f"{report} is empty"))
        report_text = ""
    else:
        report_text = report.read_text(encoding="utf-8", errors="replace")

    if report_text:
        if word_count(report_text) > MAX_REPORT_WORDS:
            failures.append(fail("too_long", f"report exceeds {MAX_REPORT_WORDS} words"))
        if not re.search(r"^#\s+Research Report\s*$", report_text, re.IGNORECASE | re.MULTILINE):
            failures.append(fail("missing_title", "report.md must start with '# Research Report'"))
        for heading in REPORT_HEADINGS:
            if not has_heading(report_text, heading):
                failures.append(fail("missing_section", f"report.md missing '## {heading}'"))
        if "c:\\temp\\model" not in report_text.lower():
            failures.append(fail("missing_directory_discussion", "report.md must discuss the C:\\temp\\modelN directory pattern"))
        if "agent" not in report_text.lower() or "provider" not in report_text.lower():
            failures.append(fail("missing_agent_provider_discussion", "report.md must discuss the agent-to-provider/model binding mechanism"))

    launch = args.launch_ps1
    if not launch.is_file():
        failures.append(fail("missing_launch_ps1", f"{launch} does not exist"))
    elif launch.stat().st_size == 0:
        failures.append(fail("empty_launch_ps1", f"{launch} is empty"))
    else:
        ps1_lower = launch.read_text(encoding="utf-8", errors="replace").lower()
        if "opencode" not in ps1_lower:
            failures.append(fail("ps1_missing_opencode", "launch.ps1 never invokes opencode"))
        if "--agent" not in ps1_lower:
            failures.append(fail("ps1_missing_agent_flag", "launch.ps1 must pass --agent per instance"))
        if "--dir" not in ps1_lower:
            failures.append(fail("ps1_missing_dir_flag", "launch.ps1 must pass --dir per instance"))
        if "c:\\temp\\model" not in ps1_lower:
            failures.append(fail("ps1_missing_directory_pattern", "launch.ps1 must reference the C:\\temp\\modelN directory pattern"))
        if not re.search(r"new-item|mkdir|\bmd\b", ps1_lower):
            failures.append(fail("ps1_missing_mkdir", "launch.ps1 must create the per-instance directories"))
        if not re.search(r"start-job|start-process|start-threadjob|foreach-object\s+-parallel", ps1_lower):
            failures.append(
                fail(
                    "ps1_not_concurrent",
                    "launch.ps1 shows no parallel-launch construct (Start-Job / Start-Process / Start-ThreadJob / ForEach-Object -Parallel) -- looks serial",
                )
            )

    if not args.proof.is_file() or args.proof.stat().st_size == 0:
        failures.append(fail("missing_proof_script", f"{args.proof} does not exist or is empty"))

    proof_log = args.proof_log
    if not proof_log.is_file() or proof_log.stat().st_size == 0:
        failures.append(fail("missing_proof_log", f"{proof_log} missing or empty -- worker must run proof.py themselves and save its output here"))
    else:
        log_text = proof_log.read_text(encoding="utf-8", errors="replace")
        if "PROOF OK" not in log_text:
            failures.append(fail("proof_log_no_marker", f"proof log never shows 'PROOF OK':\n{output_tail(log_text)}"))

    result = args.proof_result
    if not result.is_file() or result.stat().st_size == 0:
        failures.append(fail("missing_proof_result", f"{result} missing or empty -- proof.py must write structured JSON evidence"))
    else:
        try:
            data = json.loads(result.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError as exc:
            failures.append(fail("proof_result_invalid_json", f"{result} is not valid JSON: {exc}"))
            data = None
        if data is not None:
            routing = data.get("routing")
            if not isinstance(routing, dict) or len(routing) < 3:
                failures.append(fail("proof_result_missing_routing", "proof-result.json must have a 'routing' object with an entry per agent/instance (>=3)"))
            else:
                for agent_name, entry in routing.items():
                    if not isinstance(entry, dict):
                        failures.append(fail("proof_result_bad_entry", f"routing entry for {agent_name} is not an object"))
                        continue
                    expected_port = entry.get("expected_port")
                    hit_port = entry.get("hit_port")
                    if expected_port is None or hit_port is None:
                        failures.append(fail("proof_result_missing_ports", f"routing entry for {agent_name} missing expected_port/hit_port"))
                    elif expected_port != hit_port:
                        failures.append(
                            fail(
                                "proof_result_misrouted",
                                f"agent {agent_name} was supposed to hit port {expected_port} but hit {hit_port} -- agent-to-provider binding did not route correctly",
                            )
                        )
            overlap = data.get("overlap_confirmed")
            if overlap is not True:
                failures.append(fail("proof_result_no_overlap", "proof-result.json must set overlap_confirmed: true, with the timing evidence that earned it"))
            isolated = data.get("directories_isolated")
            if isolated is not True:
                failures.append(fail("proof_result_not_isolated", "proof-result.json must set directories_isolated: true, with evidence no instance wrote into another's directory"))

    session_result = subprocess.run(
        args.session_validator,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if session_result.returncode != 0:
        failures.append(
            fail(
                "session_validator_failed",
                f"command exited {session_result.returncode}: {args.session_validator}\n{output_tail(session_result.stdout)}",
            )
        )

    check_untouched()

    if failures:
        for item in failures:
            print(item)
        return 1
    print(f"PASS [windows_opencode_audition]: {args.expected_model} produced a valid design, a concurrent launch.ps1, and structured proof evidence showing correct routing, overlap, and isolation, with the real opencode config/auth left untouched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
