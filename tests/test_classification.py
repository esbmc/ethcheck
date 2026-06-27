"""Unit tests for EthCheck's ESBMC-output classification (issue #4).

These cover the pure helpers that decide whether an ESBMC run is a success, a
genuine counterexample, or an error that never reached a verdict -- the bug was
that errors were reported as counterexamples.
"""
from ethcheck.ethcheck import classify_esbmc_output, get_esbmc_error, get_counterexample

SUCCESS = "Solving with solver\nVERIFICATION SUCCESSFUL\n"
FAILED = "[Counterexample]\nState 1 ...\nVERIFICATION FAILED\nBug found (k = 1)\n"
INT_OVERFLOW = ("Converting\nERROR: Python int overflow: 2 ** 64 = "
                "18446744073709551616 does not fit in 64-bit int.\n")
OBJECT_SIZE = "ERROR: __ESBMC_get_object_size: cannot determine the size of a non-array object\n"


def test_success_is_classified_success():
    assert classify_esbmc_output(SUCCESS) == "success"


def test_failed_is_classified_failed():
    assert classify_esbmc_output(FAILED) == "failed"


def test_error_outputs_are_classified_error_not_failed():
    # The core of issue #4: an ESBMC error must not be read as a counterexample.
    assert classify_esbmc_output(INT_OVERFLOW) == "error"
    assert classify_esbmc_output(OBJECT_SIZE) == "error"


def test_empty_output_is_error():
    assert classify_esbmc_output("") == "error"


def test_failed_takes_precedence_when_both_markers_present():
    # Fail safe: a counterexample must never be masked by a SUCCESSFUL string.
    both = "VERIFICATION SUCCESSFUL\n...\nVERIFICATION FAILED\n"
    assert classify_esbmc_output(both) == "failed"


def test_get_counterexample_extracts_from_merged_stdout_stderr():
    # verify_function feeds get_counterexample the merged stdout+stderr.
    merged = "progress line\n" + "[Counterexample]\nState 1 x=-1\nVERIFICATION FAILED\n"
    cex = get_counterexample(merged)
    assert "State 1 x=-1" in cex
    assert "progress line" not in cex      # text before the start marker is dropped
    assert "VERIFICATION FAILED" not in cex  # the end marker is excluded


def test_get_esbmc_error_returns_first_error_line():
    assert get_esbmc_error(INT_OVERFLOW).startswith("ERROR: Python int overflow")
    assert get_esbmc_error(OBJECT_SIZE).startswith("ERROR: __ESBMC_get_object_size")


def test_get_esbmc_error_without_error_line_is_generic():
    assert get_esbmc_error(SUCCESS) == "ESBMC produced no verdict"
