"""Unit tests for ``verify_function`` with a stubbed ESBMC/pytest subprocess.

These lock in the success/error/failed branching introduced for issue #4 and
the ``testcase.xml`` cleanup hardened in PR #6, without needing a real ESBMC
binary. ``subprocess.run`` is replaced by a fake that recognises the ESBMC
invocation and the pytest confirmation call by their argv, so each branch of
``verify_function`` can be driven deterministically.
"""
import subprocess

import pytest

from ethcheck import ethcheck as ec


class FakeCompleted:
    """Minimal stand-in for subprocess.CompletedProcess."""

    def __init__(self, stdout="", stderr=""):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = 0


def fake_subprocess_run(esbmc_stdout="", esbmc_stderr="", esbmc_timeout=False,
                        generates_testcase=False, pytest_outcome="pass"):
    """Build a stub for ``subprocess.run`` used inside ``verify_function``.

    The ESBMC call and the pytest confirmation call are told apart by argv
    (``pytest`` is always invoked as ``['pytest', <file>]``). When
    ``generates_testcase`` is set, the ESBMC stub drops a ``testcase.xml`` in
    the cwd, modelling ``--generate-testcase`` finding a trace. This mirrors
    reality: ``verify_function`` removes any stale ``testcase.xml`` *before*
    invoking ESBMC, so only the binary recreating it drives the confirmation
    branch -- a pre-seeded file would be deleted on entry.
    """
    def _run(cmd, *_args, **_kwargs):
        if cmd and cmd[0] == "pytest":
            if pytest_outcome == "pass":
                return FakeCompleted()
            raise subprocess.CalledProcessError(1, cmd, output="E   assert ...\n")
        # ESBMC invocation.
        if esbmc_timeout:
            raise subprocess.TimeoutExpired(cmd, 10)
        if generates_testcase:
            with open("testcase.xml", "w", encoding="utf-8") as fh:
                fh.write("<testcase/>")
        return FakeCompleted(stdout=esbmc_stdout, stderr=esbmc_stderr)

    return _run


@pytest.fixture
def run_in_tmp(tmp_path, monkeypatch):
    """Run with cwd in an isolated dir so the cwd-relative ``testcase.xml`` is
    real and its cleanup can be asserted. ESBMC's arg-type introspection is
    stubbed out so no source file needs to exist."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(ec, "get_function_arg_types", lambda *a, **k: [])
    return tmp_path


COMMAND = ["/usr/bin/esbmc", "--incremental-bmc", "--generate-testcase", "spec.py"]


def test_success_prints_check_and_runs_no_pytest(run_in_tmp, monkeypatch, capsys):
    monkeypatch.setattr(ec.subprocess, "run",
                        fake_subprocess_run(esbmc_stderr="VERIFICATION SUCCESSFUL\n"))
    ec.verify_function("foo", COMMAND)
    out = capsys.readouterr().out
    assert "foo ✓" in out
    assert "✗" not in out


def test_error_prints_warning_not_counterexample(run_in_tmp, monkeypatch, capsys):
    esbmc = "ERROR: Python int overflow: 2 ** 64 ...\n"
    monkeypatch.setattr(ec.subprocess, "run", fake_subprocess_run(esbmc_stdout=esbmc))
    ec.verify_function("bar", COMMAND)
    out = capsys.readouterr().out
    assert "bar ⚠" in out
    assert "ESBMC could not analyze" in out
    assert "✗" not in out


def test_timeout_prints_timeout(run_in_tmp, monkeypatch, capsys):
    monkeypatch.setattr(ec.subprocess, "run", fake_subprocess_run(esbmc_timeout=True))
    ec.verify_function("slow", COMMAND)
    assert "slow: Timeout" in capsys.readouterr().out


def test_failed_without_testcase_prints_counterexample(run_in_tmp, monkeypatch, capsys):
    # No testcase.xml on disk -> the trace is printed, pytest is never invoked.
    esbmc = "[Counterexample]\nState 1 x=-1\nVERIFICATION FAILED\n"
    monkeypatch.setattr(ec.subprocess, "run", fake_subprocess_run(esbmc_stdout=esbmc))
    ec.verify_function("buggy", COMMAND)
    out = capsys.readouterr().out
    assert "buggy ✗" in out
    assert "ESBMC command:" in out


def test_failed_pytest_pass_prints_check_and_removes_testcase(run_in_tmp, monkeypatch, capsys):
    # ESBMC found a trace and emitted testcase.xml, but pytest does not confirm
    # the bug -> report ✓ and clean up testcase.xml so it can't mis-test later.
    monkeypatch.setattr(ec, "generate_python_script", lambda *a, **k: None)
    esbmc = "[Counterexample]\nState 1\nVERIFICATION FAILED\n"
    monkeypatch.setattr(ec.subprocess, "run",
                        fake_subprocess_run(esbmc_stdout=esbmc, generates_testcase=True,
                                            pytest_outcome="pass"))
    ec.verify_function("notabug", COMMAND)
    out = capsys.readouterr().out
    assert "notabug ✓" in out
    assert not (run_in_tmp / "testcase.xml").exists()


def test_failed_pytest_confirms_returns_failed_and_removes_testcase(run_in_tmp, monkeypatch, capsys):
    # ESBMC trace + pytest reproduces it -> confirmed counterexample. verify_function
    # reports ✗ and returns 'failed'; the process exit code (3) is the caller's job
    # via exit_code_for, so a confirmed bug does not abort the batch mid-run.
    monkeypatch.setattr(ec, "generate_python_script", lambda *a, **k: None)
    esbmc = "[Counterexample]\nState 1\nVERIFICATION FAILED\n"
    monkeypatch.setattr(ec.subprocess, "run",
                        fake_subprocess_run(esbmc_stdout=esbmc, generates_testcase=True,
                                            pytest_outcome="fail"))
    assert ec.verify_function("realbug", COMMAND) == "failed"
    assert "realbug ✗" in capsys.readouterr().out
    # Cleanup must still run on the failure path (finally).
    assert not (run_in_tmp / "testcase.xml").exists()


def test_failed_testcase_generation_valueerror_removes_testcase(run_in_tmp, monkeypatch, capsys):
    def _raise(*_a, **_k):
        raise ValueError("cannot build testcase")

    monkeypatch.setattr(ec, "generate_python_script", _raise)
    esbmc = "[Counterexample]\nState 1\nVERIFICATION FAILED\n"
    monkeypatch.setattr(ec.subprocess, "run",
                        fake_subprocess_run(esbmc_stdout=esbmc, generates_testcase=True))
    ec.verify_function("ungen", COMMAND)
    out = capsys.readouterr().out
    assert "ungen ✗" in out
    assert not (run_in_tmp / "testcase.xml").exists()
