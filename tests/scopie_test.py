from src.scopie.scopie import is_allowed, ValidationError
import json
import pytest

data = {}
with open("tests/scenarios.json") as f:
    data = json.load(f)


def generate_test_parameters(values):
    return [
        (
            value["id"],
            value["actionScopes"],
            value["actorRules"],
            value.get("variables"),
            value.get("result"),
            value.get("error"),
        )
        for value in values
    ]


@pytest.mark.parametrize(
    "id, actionScopes, actorRules, variables, result, error",
    generate_test_parameters(data["isAllowedTests"]),
)
def test_is_allowed(id, actionScopes, actorRules, variables, result, error):
    if variables is None:
        variables = {}

    actual = None
    try:
        actual = is_allowed(actionScopes, actorRules, **variables)
        assert actual == result
        assert error is None
    except ValidationError as e:
        assert error == e.msg
