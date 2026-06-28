from scripts.evaluate.run import classify_pytest_exit


def test_evaluator_distinguishes_mission_failures_from_setup_errors() -> None:
    assert classify_pytest_exit(0) == "passed"
    assert classify_pytest_exit(1) == "intended_failure"
    assert classify_pytest_exit(2) == "setup_error"
    assert classify_pytest_exit(4) == "setup_error"
