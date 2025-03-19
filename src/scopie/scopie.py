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
        if isinstance(other, ScopieError):
            return self.msg == other.msg
        return False


def is_valid_char(char: str) -> bool:
    if char >= "a" and char <= "z":
        return True

    if char >= "A" and char <= "Z":
        return True

    if char >= "0" and char <= "9":
        return True

    return char in allowed_extra_chars


def is_allowed(
    action_scopes: List[str],
    actor_rules: List[str],
    **vars: Dict[str, str],
) -> bool | ScopieError:
    has_been_allowed = False
    if not actor_rules:
        return False

    if actor_rules[0] == "":
        raise ScopieError("scopie-106 in actor: rule was empty")

    if len(action_scopes) == 0:
        raise ScopieError("scopie-106 in action: scopes was empty")

    actor_blocks = actor_rules[0].split(block_seperator)
    action_blocks = action_scopes[0].split(block_seperator)
    for i, (actor_block, action_block) in enumerate(
        zip_longest(actor_blocks[1:], action_blocks)
    ):
        if action_block == "":
            raise ScopieError("scopie-106 in action: scope was empty")

        if actor_block == "":
            raise ScopieError("scopie-106 in action: actor was empty")

        if not action_block or not actor_block:
            break

        if actor_block == wildcard:
            continue

        if len(actor_block) == 2 and actor_block == wildcard + wildcard:
            print(i, len(actor_blocks), "super")
            if i < len(actor_blocks) - 2:
                print("not at the end")
                raise ScopieError("scopie-105: super wildcard not in the last block")

            return actor_blocks[0] == allow_permission

        if actor_block[0] == var_prefix:
            var_name = actor_block[1:]
            if var_name not in vars:
                raise ScopieError(f"scopie-104: variable '{var_name}' not found")
            if vars[var_name] != action_block:
                break
        else:
            actor_rules_split = actor_block.split(array_seperator)

            for actor_split in actor_rules_split:
                if actor_split[0] == var_prefix:
                    raise ScopieError(
                        f"scopie-101: variable '{actor_split[1:]}' found in array block"
                    )

                if (
                    actor_split[0] == wildcard
                    and len(actor_split) > 1
                    and actor_split[1] == wildcard
                ):
                    raise ScopieError("scopie-103: super wildcard found in array block")

                if actor_split[0] == wildcard:
                    raise ScopieError("scopie-102: wildcard found in array block")

                for c in actor_split:
                    if not is_valid_char(c):
                        raise ScopieError(
                            f"scopie-100 in actor: invalid character '{c}'"
                        )

            for c in action_block:
                if not is_valid_char(c):
                    raise ScopieError(f"scopie-100 in action: invalid character '{c}'")

            if action_block not in actor_rules_split:
                break

    # Runs only at completion of loop
    else:
        if actor_blocks[0] == deny_permission:
            return False
        else:
            has_been_allowed = True

    return has_been_allowed
