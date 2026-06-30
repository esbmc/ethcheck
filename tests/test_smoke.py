"""End-to-end smoke test: run EthCheck against the bundled ``spec.py``.

Unlike the unit tests, this drives the *real* tool and a *real* ESBMC binary
over the self-contained ``ethcheck/spec.py`` fixture and checks the run-level
invariants:

* the banner and the "Verifying file:" header are printed;
* the process exits cleanly (0, or 3 when a counterexample is confirmed by
  pytest -- a legitimate outcome that stops the run early);
* every per-function verdict line belongs to a real spec function, and at least
  one function is classified into a verdict bucket (✓ / ✗ / ⚠ / Timeout).

The test is **gated on a usable ESBMC** (one with the Python frontend) and skips
itself otherwise -- so it is a no-op in CI, where the bundled ``bin/esbmc``
git-LFS object is only a pointer. It asserts pipeline-level invariants rather
than a fixed tally, so it stays robust across ESBMC versions and machine speed.
"""
import ast
import os
import re
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(REPO_ROOT, "ethcheck", "spec.py")
ANSI = re.compile(r"\x1b\[[0-9;]*[mK]")
# Generous ceiling: each function is capped at ESBMC's 10 s per-run timeout.
RUN_TIMEOUT = 300


def _is_usable_esbmc(path):
    """True only for a real, runnable ESBMC exposing the Python frontend."""
    if not path or not os.path.isfile(path) or not os.access(path, os.X_OK):
        return False
    with open(path, "rb") as handle:
        if handle.read(32).startswith(b"version https://git-lfs"):
            return False  # unresolved git-LFS pointer, not the real binary
    try:
        help_text = subprocess.run(
            [path, "--help"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=30, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return "--python" in help_text and "--generate-testcase" in help_text


def _find_esbmc():
    for candidate in (os.environ.get("ESBMC_PATH"),
                      shutil.which("esbmc"),
                      os.path.join(REPO_ROOT, "bin", "esbmc")):
        if _is_usable_esbmc(candidate):
            return candidate
    return None


def _spec_functions():
    with open(SPEC, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    return {node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)}


def _tally(output, functions):
    """Map each spec function that received a verdict to its bucket."""
    verdicts = {}
    for raw in output.splitlines():
        line = raw.strip()
        head = line.split(" ", 1)[0].rstrip(":")
        if head not in functions:
            continue
        if line.endswith(" ✓"):
            verdicts[head] = "passed"
        elif line.endswith(" ✗"):
            verdicts[head] = "failed"
        elif " ⚠" in line:
            verdicts[head] = "warned"
        elif line.endswith(": Timeout"):
            verdicts[head] = "timeout"
    return verdicts


def test_smoke_run_against_spec():
    esbmc = _find_esbmc()
    if esbmc is None:
        pytest.skip("no usable ESBMC with the Python frontend found")

    # PYTHONPATH makes `-m ethcheck.ethcheck` importable; the temp cwd keeps any
    # transient testcase.xml out of the repo.
    env = dict(os.environ, PYTHONPATH=REPO_ROOT)
    cmd = [sys.executable, "-m", "ethcheck.ethcheck",
           "--file", SPEC, "--esbmc", esbmc]
    try:
        proc = subprocess.run(
            cmd, cwd=os.environ.get("TMPDIR", "/tmp"), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            timeout=RUN_TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        pytest.skip("ESBMC too slow in this environment to finish the smoke run")

    out = ANSI.sub("", proc.stdout)

    assert "ETHCHECK" in out, out[-2000:]
    assert "Verifying file:" in out, out[-2000:]
    # 0 = ran to completion; 3 = a counterexample was confirmed by pytest.
    assert proc.returncode in (0, 3), f"rc={proc.returncode}\n{out[-2000:]}"

    functions = _spec_functions()
    verdicts = _tally(out, functions)
    assert verdicts, f"no function was classified\n{out[-2000:]}"
    # A full, non-aborted run must classify every function exactly once.
    if proc.returncode == 0:
        assert set(verdicts) == functions, sorted(functions - set(verdicts))
