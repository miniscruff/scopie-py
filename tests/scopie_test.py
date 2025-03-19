from src.scopie.scopie import is_allowed
import json
import pytest

val

data = {}
with open('tests/scenarios.json') as f:
    data = json.load(f)


def generate_test_parameters(values):
    return [(value["id"], value["actionScopes"], value["actorRules"], value.get("variables"), value.get("result")) for value in values]


@pytest.mark.parametrize('id, actionScopes, actorRules, variables, result', generate_test_parameters(data["isAllowedTests"]))
def test_is_allowed(id, actionScopes, actorRules, variables, result):
    if variables is None:
        variables = {}
    assert is_allowed(actionScopes, actorRules, **variables) == result
