"""Pure, dependency-free helpers for classifying ESBMC output (issue #4).

These decide whether an ESBMC run is a success, a genuine counterexample, or an
error that never reached a verdict. They are kept in their own module -- with no
third-party imports -- so they can be unit-tested without pulling in colorama,
pkg_resources, or the test-generation machinery. A missing runtime dependency
must not break the classification tests at collection time.
"""


def classify_esbmc_output(output):
    # Classify on ESBMC's verdict text, not the process exit code: ESBMC exits
    # non-zero both for a real counterexample and for an error (parse/type
    # error, unsupported construct, internal limitation) that never reaches a
    # verdict. The two cases must not be conflated.
    #
    # Match each verdict as a whole stripped line rather than a substring, so a
    # counterexample trace that merely *mentions* the phrase cannot be misread
    # as the verdict. Check FAILED first so a counterexample is never masked if
    # both verdict lines ever co-occur -- a bug finder must fail safe toward
    # reporting the violation.
    verdict_lines = {line.strip() for line in output.splitlines()}
    if "VERIFICATION FAILED" in verdict_lines:
        return "failed"
    if "VERIFICATION SUCCESSFUL" in verdict_lines:
        return "success"
    return "error"


def get_esbmc_error(output):
    for line in output.splitlines():
        if line.startswith("ERROR:"):
            return line.strip()
    return "ESBMC produced no verdict"


def get_counterexample(output):
    start_marker = "[Counterexample]"
    end_marker = "VERIFICATION FAILED"
    start_index = output.find(start_marker)
    end_index = output.find(end_marker)
    return output[start_index:end_index].strip() if start_index != -1 and end_index != -1 else ""
