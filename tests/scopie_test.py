from src.scopie.scopie import is_allowed, ScopieError
import json
import pytest


data = {}
with open("tests/scenarios.json") as f:
    data = json.load(f)


def generate_test_parameters(values):
    return [
        pytest.param(
            value["scopes"],
            value["rules"],
            value.get("variables"),
            value.get("result"),
            value.get("error"),
            id=value["id"],
        )
        for value in values
    ]


@pytest.mark.parametrize(
    "scopes, rules, variables, result, error",
    generate_test_parameters(data["isAllowedTests"]),
)
def test_is_allowed(scopes, rules, variables, result, error):
    if variables is None:
        variables = {}

    try:
        actual = is_allowed(scopes, rules, **variables)
        assert actual == result
        assert error is None
    except ScopieError as e:
        assert error == e.msg


def generate_benchmark_parameters(values):
    return [
        pytest.param(
            value["scopes"],
            value["rules"],
            value.get("variables"),
            value.get("result"),
            id=value["id"],
        )
        for value in values
    ]

@pytest.mark.parametrize(
    "scopes, rules, variables, result",
    generate_benchmark_parameters(data["benchmarks"]),
)
def test_benchmarks(scopes, rules, variables, result):
    if variables is None:
        variables = {}

    actual = is_allowed(scopes, rules, **variables)
    assert actual == result

@pytest.mark.parametrize(
    "scopes, rules, variables, result",
    generate_benchmark_parameters(data["benchmarks"]),
)
@pytest.mark.benchmark(
    max_time=0,
    min_rounds=10_000,
    warmup=True,
    warmup_iterations=50,
    calibration_precision=100,
)
def test_benchmarks_as_benchmarks(benchmark, scopes, rules, variables, result):
    if variables is None:
        variables = {}

    actual = benchmark(is_allowed, scopes=scopes, rules=rules, **variables)
    assert actual == result
