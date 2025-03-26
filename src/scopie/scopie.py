from typing import List, Dict, Sequence
from itertools import zip_longest

array_seperator = "|"
block_seperator = "/"
wildcard = "*"
super_wildcard = "**"
var_prefix = "@"

allow_permission = "allow"
deny_permission = "deny"

allowed_extra_chars = {"_", "-", var_prefix, wildcard}


class ScopieError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __eq__(self, other) -> bool:
        return (isinstance(other, ScopieError) and self.msg == other.msg) or (
            isinstance(other, str) and self.msg == other
        )


def is_valid_char(char: str) -> bool:
    if char >= "a" and char <= "z":
        return True

    if char >= "A" and char <= "Z":
        return True

    if char >= "0" and char <= "9":
        return True

    return char in allowed_extra_chars


def _compare_rule_to_scope(rule: str, scope: str, vars: dict) -> bool:
    rule_blocks = rule.split(block_seperator)
    scope_blocks = scope.split(block_seperator)
    for i, (rule_block, scope_block) in enumerate(
        zip_longest(rule_blocks[1:], scope_blocks)
    ):
        if scope_block == "":
            raise ScopieError("scopie-106 in scope: scope was empty")

        if rule_block == "":
            raise ScopieError("scopie-106 in rule: rule was empty")

        if not scope_block or not rule_block:
            return False

        if rule_block == wildcard:
            continue

        if len(rule_block) == 2 and rule_block == wildcard + wildcard:
            if i < len(rule_blocks) - 2:
                raise ScopieError("scopie-105: super wildcard not in the last block")

            return rule_blocks[0] == allow_permission

        if rule_block[0] == var_prefix:
            var_name = rule_block[1:]
            if var_name not in vars:
                raise ScopieError(f"scopie-104: variable '{var_name}' not found")
            if vars[var_name] != scope_block:
                return False
        else:
            rules_split = rule_block.split(array_seperator)

            for rule_split in rules_split:
                if rule_split[0] == var_prefix:
                    raise ScopieError(
                        f"scopie-101: variable '{rule_split[1:]}' found in array block"
                    )

                if (
                    rule_split[0] == wildcard
                    and len(rule_split) > 1
                    and rule_split[1] == wildcard
                ):
                    raise ScopieError("scopie-103: super wildcard found in array block")

                if rule_split[0] == wildcard:
                    raise ScopieError("scopie-102: wildcard found in array block")

                for c in rule_split:
                    if not is_valid_char(c):
                        raise ScopieError(
                            f"scopie-100 in rule: invalid character '{c}'"
                        )

            for c in scope_block:
                if not is_valid_char(c):
                    raise ScopieError(f"scopie-100 in scope: invalid character '{c}'")

            if scope_block not in rules_split:
                return False

    return True


def is_allowed(
    scopes: Sequence[str],
    rules: Sequence[str],
    **vars: str,
) -> bool:
    """
    Returns whether or not the scopes are allowed with the given rules.
    Depending on the language, we would also return an error, throw or raise an exception for invalid
    scopes or rules.

        :param scopes: Scopes specifies one or more scopes our actor must match. When using more then one scope, they are treated as a series of OR conditions, and an actor will be allowed if they match any of the scopes.
        :param rules: Rules specifies one or more rules our requesting scopes has to have to be allowed access.
        :returns: If we are allowed or not
        :raises ScopieError: If the scopes or rules are invalid based on scopie requirements
    """
    has_been_allowed = False
    if not rules:
        return False

    if rules[0] == "":
        raise ScopieError("scopie-106 in rule: rule was empty")

    if len(scopes) == 0:
        raise ScopieError("scopie-106 in scope: scopes was empty")

    for rule in rules:
        for scope in scopes:
            match = _compare_rule_to_scope(rule, scope, vars)
            if match and rule.startswith(deny_permission):
                return False
            elif match:
                has_been_allowed = True

    return has_been_allowed


def validate_scopes(
    scope_or_rules: Sequence[str],
) -> ScopieError | None:
    """
    Checks whether or not the given scopes or rules are valid given the
    requirements outlined in the specification.
    Depending on the language, this could return a boolean and throw an error, return
    an error or other language standard.

        :param scope_or_rules: Given scope or rule to validate.
        :returns: An error if one is found or None
    """
    if len(scope_or_rules) == 0:
        return ScopieError("scopie-106: scope or rule was empty")

    first_scope = scope_or_rules[0]
    is_rules = first_scope.startswith((allow_permission, deny_permission))

    for scope_or_rule in scope_or_rules:
        if len(scope_or_rule) == 0:
            return ScopieError("scopie-106: scope or rule was empty")

        scope_is_rule = scope_or_rule.startswith(
            allow_permission
        ) or scope_or_rule.startswith(deny_permission)
        if scope_is_rule != is_rules:
            return ScopieError("scopie-107: inconsistent array of scopes and rules")

        block_split = scope_or_rule.split(block_seperator)
        for i, block in enumerate(block_split):
            if block == super_wildcard and i < len(block_split) - 1:
                return ScopieError("scopie-105: super wildcard not in the last block")
            if array_seperator in block:
                if super_wildcard in block:
                    return ScopieError(
                        "scopie-103: super wildcard found in array block"
                    )
                if wildcard in block:
                    return ScopieError("scopie-102: wildcard found in array block")
                if var_prefix in block:
                    return ScopieError(
                        "scopie-101: variable 'group' found in array block"
                    )

            for c in block:
                if c != array_seperator and not is_valid_char(c):
                    return ScopieError(f"scopie-100: invalid character '{c}'")

    return None
