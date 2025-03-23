from typing import List, Dict
from itertools import zip_longest

array_seperator = "|"
block_seperator = "/"
wildcard = "*"
var_prefix = "@"

allow_permission = "allow"
deny_permission = "deny"

allowed_extra_chars = {"_", "-", var_prefix, wildcard}


class ScopieError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __eq__(self, other) -> bool:
        return isinstance(other, ScopieError) and self.msg == other.msg


def is_valid_char(char: str) -> bool:
    if char >= "a" and char <= "z":
        return True

    if char >= "A" and char <= "Z":
        return True

    if char >= "0" and char <= "9":
        return True

    return char in allowed_extra_chars


def compare_rule_to_scope(rule: str, scope: str, vars: dict) -> bool:
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
    scopes: List[str],
    rules: List[str],
    **vars: Dict[str, str],
) -> bool:
    has_been_allowed = False
    if not rules:
        return False

    if rules[0] == "":
        raise ScopieError("scopie-106 in rule: rule was empty")

    if len(scopes) == 0:
        raise ScopieError("scopie-106 in scope: scopes was empty")

    for rule in rules:
        for scope in scopes:
            match = compare_rule_to_scope(rule, scope, vars)
            if match and rule.startswith(deny_permission):
                return False
            elif match:
                has_been_allowed = True

    return has_been_allowed
