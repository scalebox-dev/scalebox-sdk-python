#!/usr/bin/env python3
import asyncio
import os
import sys
import time
from typing import Tuple
import re


REPO_ROOT = "/root/scalebox"
TEST_FILE = os.path.join(REPO_ROOT, "test", "test_code_interpreter_sync_comprehensive.py")


def _extract_final_report(stdout_text: str) -> str:
    lines = stdout_text.splitlines()
    if not lines:
        return ""
    # Prefer capturing from the last report title to include full details
    title_indices = [i for i, line in enumerate(lines) if "CodeInterpreter" in line and "测试报告" in line]
    if title_indices:
        start_idx = title_indices[-1]
        return "\n".join(lines[start_idx:]).strip()
    # Fallback: last long '====' separator block
    sep_indices = [i for i, line in enumerate(lines) if line.strip().startswith("=") and set(line.strip()) == {"="} and len(line.strip()) >= 20]
    if sep_indices:
        start_idx = sep_indices[-1]
        return "\n".join(lines[start_idx:]).strip()
    return stdout_text.strip()


def _extract_sandbox_id(text: str) -> str:
    # Common explicit patterns
    patterns = [
        r"sandbox[_\s-]*id\s*[:=]\s*([A-Za-z0-9_\-]+)",
        r"Sandbox[_\s-]*ID\s*[:=]\s*([A-Za-z0-9_\-]+)",
        r"sandbox\s*:\s*([A-Za-z0-9_\-]+)",
        r"sandboxId\s*[:=]\s*([A-Za-z0-9_\-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1)
    # UUID-like fallback
    uuid_pat = r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
    m2 = re.search(uuid_pat, text)
    if m2:
        return m2.group(0)
    # sbx_* style fallback
    m3 = re.search(r"\bsbx_[A-Za-z0-9]+\b", text)
    if m3:
        return m3.group(0)
    return ""


async def run_once(run_id: int) -> Tuple[int, float, str, str]:
    start = time.perf_counter()
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        TEST_FILE,
        cwd=REPO_ROOT,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    duration = time.perf_counter() - start
    exit_code = process.returncode
    result = "PASS" if exit_code == 0 else "FAIL"
    stdout_text = stdout.decode(errors="ignore") if stdout else ""
    stderr_text = stderr.decode(errors="ignore") if stderr else ""
    report = _extract_final_report(stdout_text) or _extract_final_report(stderr_text)
    if not report:
        # Fallback to a brief tail if no recognizable report
        tail = (stdout_text or stderr_text).strip().splitlines()[-10:]
        report = "\n".join(tail).strip()
    # Determine if success rate is effectively 0%
    combined_text = "\n".join([report, stdout_text, stderr_text])
    zero_rate = False
    # Match ASCII/full-width colon and percent, and allow 0, 0.0, 0.00 etc.
    if re.search(r"成功率\s*[：:]\s*0(?:\.0+)?\s*[％%]", combined_text):
        zero_rate = True
    else:
        # Fallback by parsing totals if present (失败数 == 总测试数)
        total_m = re.search(r"总测试数\s*[：:]\s*(\d+)", combined_text)
        fail_m = re.search(r"失败数\s*[：:]\s*(\d+)", combined_text)
        if total_m and fail_m:
            try:
                total_n = int(total_m.group(1))
                fail_n = int(fail_m.group(1))
                if total_n > 0 and fail_n == total_n:
                    zero_rate = True
            except ValueError:
                pass

    # If success rate is 0%, mark as FAIL and attach detailed errors
    if zero_rate:
        result = "FAIL"
        stderr_lines = stderr_text.strip().splitlines()
        stdout_lines = stdout_text.strip().splitlines()
        # Extract sandbox id from combined text
        sandbox_id = _extract_sandbox_id(combined_text)
        detail = []
        if sandbox_id:
            detail.append(f"Sandbox ID: {sandbox_id}")
        if stderr_lines:
            detail.append("[stderr]")
            detail.extend(stderr_lines)
        if stdout_lines:
            detail.append("[stdout]")
            detail.extend(stdout_lines)
        if detail:
            report = f"{report}\n\n" + "\n".join(detail)
    return run_id, duration, result, report


async def run_concurrent(concurrency: int) -> None:
    if not os.path.isfile(TEST_FILE):
        print(f"Test file not found: {TEST_FILE}")
        sys.exit(2)

    tasks = [asyncio.create_task(run_once(i + 1)) for i in range(concurrency)]

    started_at = time.perf_counter()
    completed = 0
    passed = 0
    failed = 0

    for coro in asyncio.as_completed(tasks):
        run_id, duration, result, report = await coro
        completed += 1
        if result == "PASS":
            passed += 1
        else:
            failed += 1
        print(f"Run {run_id:03d}: {result} in {duration:.2f}s", flush=True)
        if report:
            print(report, flush=True)
            print("-" * 64, flush=True)

    total_time = time.perf_counter() - started_at
    print("-" * 64)
    print(f"Completed: {completed}, Passed: {passed}, Failed: {failed}, Total time: {total_time:.2f}s")


def main() -> None:
    # Default concurrency to 80, but allow override via CLI
    try:
        concurrency = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    except ValueError:
        print("First argument must be an integer concurrency level.")
        sys.exit(2)

    if concurrency <= 0:
        print("Concurrency must be a positive integer.")
        sys.exit(2)

    # Use Proactor on Windows; default loop elsewhere
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())  # type: ignore[attr-defined]

    asyncio.run(run_concurrent(concurrency))


if __name__ == "__main__":
    main()


