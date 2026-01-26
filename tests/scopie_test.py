from src.scopie import is_allowed, validate_actions, validate_permissions, ScopieError
import json
import pytest
from typing import Dict, Any, List

data = {}
with open("tests/scenarios.json") as f:
    data = json.load(f)


def generate_test_parameters(values: List[Dict[str, Any]], *keys: str):
    params = [
        pytest.param(
            id=value.get("id"),
            *[value.get(k) for k in keys],
        )
        for value in values
    ]

    return pytest.mark.parametrize(", ".join(keys), params)


@generate_test_parameters(
    data["isAllowedTests"], "actions", "permissions", "variables", "result", "error"
)
def test_is_allowed(actions, permissions, variables, result, error):
    if variables is None:
        variables = {}

    try:
        actual = is_allowed(actions, permissions, **variables)
        assert actual == result
        assert error is None
    except ScopieError as e:
        assert error == e.msg


@generate_test_parameters(data["validateActionsTests"], "actions", "error")
def test_validate_actions(actions: List[str], error: str):
    actual = validate_actions(actions)
    assert actual == error


@generate_test_parameters(data["validatePermissionsTests"], "permissions", "error")
def test_validate_permissions(permissions: List[str], error: str):
    actual = validate_permissions(permissions)
    assert actual == error


@generate_test_parameters(
    data["benchmarks"], "actions", "permissions", "variables", "result"
)
def test_benchmarks(actions, permissions, variables, result):
    if variables is None:
        variables = {}

    actual = is_allowed(actions, permissions, **variables)
    assert actual == result


@generate_test_parameters(
    data["benchmarks"], "actions", "permissions", "variables", "result"
)
@pytest.mark.benchmark(
    max_time=0,
    min_rounds=10_000,
    warmup=True,
    warmup_iterations=50,
    calibration_precision=100,
)
def test_benchmarks_as_benchmarks(benchmark, actions, permissions, variables, result):
    if variables is None:
        variables = {}

    actual = benchmark(
        is_allowed, actions=actions, permissions=permissions, **variables
    )
    assert actual == result
