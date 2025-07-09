import pytest, coverage
import io, contextlib

def run_tests_and_collect(source_file: str, test_file: str) -> dict:
    """
    Run the given test file (pytest) and measure coverage on the source_file.
    Returns a dictionary with keys: 'all_passed' (bool), 'coverage' (float),
    'uncovered_lines' (list of (lineno, code) tuples for source_file), and 'error_message' (str if any failure).
    """
    cov = coverage.Coverage(source=[source_file])  # limit coverage to the target source file
    cov.start()
    # Use pytest to run the test file. Capture output to get failure info.
    error_message = ""
    exit_code = 0
    # Temporarily redirect stdout/stderr to capture pytest output
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        # Run pytest on the specific test file
        exit_code = pytest.main([test_file, "-q"])
    cov.stop()
    cov.save()
    coverage_percent = 0.0
    uncovered = []
    try:
        analysis = cov.analysis2(source_file)
        # analysis2 returns (filename, executed_lines, missing_lines, excluded_lines)
        _, _, missing, _ = analysis
        # Calculate coverage percentage
        total_lines = len(analysis[1]) + len(missing)
        coverage_percent = 0.0 if total_lines == 0 else (len(analysis[1]) / total_lines)
        if missing:
            # Read source lines to get actual code for missing lines
            with open(source_file, 'r') as f:
                source_lines = f.readlines()
            for lineno in missing:
                code_line = source_lines[lineno-1].strip('\n')
                uncovered.append((lineno, code_line))
    except Exception as e:
        print(f"[Warning] Could not analyze coverage: {e}")

    all_passed = (exit_code == 0)
    if not all_passed:
        # If tests failed, get the captured output (which includes tracebacks)
        error_message = buf.getvalue()
    buf.close()
    return {
        "all_passed": all_passed,
        "coverage": coverage_percent,
        "uncovered_lines": uncovered,
        "error_message": error_message
    }
