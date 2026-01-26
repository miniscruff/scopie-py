from typing import List, Dict, Sequence, Optional
from itertools import zip_longest

array_separator = "|"
block_separator = "/"
wildcard = "*"
super_wildcard = "**"
var_prefix = "@"

allow_grant = "allow"
deny_grant = "deny"
grant_separator = ":"

allowed_extra_chars = {"_", "-"}


class ScopieError(Exception):
    """
    When validating a action or trying to process a action or permission that has an incorrect format we return or throw errors.
    To keep consistency across languages we define an error format in the specification and include error messages as
    part of the validation test suite.

    Parsing the errors should not be required, this format is aimed at being helpful to log for internal debugging,
    but are probably not useful for your end users.

    In cases where you are taking user input and saving a action, you should use the ``validate_action`` function to check
    if the provided value is properly formatted.
    You may also need to do extra processing to make sure the values defined in the action logically make sense
    in your system as a whole.

    Reference https://scopie.dev/specification/errors/ for the full list of possible errors.
    """

    def __init__(self, msg: str):
        self.msg = msg

    def __eq__(self, other) -> bool:
        return (isinstance(other, ScopieError) and self.msg == other.msg) or (
            isinstance(other, str) and self.msg == other
        )


def _is_valid_char(char: str) -> bool:
    if char >= "a" and char <= "z":
        return True

    if char >= "A" and char <= "Z":
        return True

    if char >= "0" and char <= "9":
        return True

    return char in allowed_extra_chars


def _compare_permission_to_action(permission: str, action: str, vars: dict) -> bool:
    if action == "":
        raise ScopieError("scopie-106 in action: action was empty")

    if permission == "":
        raise ScopieError("scopie-106 in permission: permission was empty")

    perms_grant_and_blocks = permission.split(grant_separator, maxsplit=1)
    grant = perms_grant_and_blocks[0]
    if grant != allow_grant and grant != deny_grant:
        raise ScopieError("scopie-107: permission does not start with a grant")

    permission_blocks = perms_grant_and_blocks[1].split(block_separator)
    action_blocks = action.split(block_separator)

    # if action_block == "":

    for i, (permission_block, action_block) in enumerate(
        zip_longest(permission_blocks, action_blocks)
    ):
        if not action_block or not permission_block:
            return False

        if permission_block == wildcard:
            continue

        if len(permission_block) == 2 and permission_block == wildcard + wildcard:
            if i < len(permission_blocks) - 1:
                raise ScopieError("scopie-105: super wildcard not in the last block")

            return True

        if permission_block[0] == var_prefix:
            var_name = permission_block[1:]
            if var_name not in vars:
                raise ScopieError(f"scopie-104: variable '{var_name}' not found")
            if vars[var_name] != action_block:
                return False
        else:
            permissions_split = permission_block.split(array_separator)

            for permission_split in permissions_split:
                if permission_split[0] == var_prefix:
                    raise ScopieError(
                        f"scopie-101: variable '{permission_split[1:]}' found in array block"
                    )

                if (
                    permission_split[0] == wildcard
                    and len(permission_split) > 1
                    and permission_split[1] == wildcard
                ):
                    raise ScopieError("scopie-103: super wildcard found in array block")

                if permission_split[0] == wildcard:
                    raise ScopieError("scopie-102: wildcard found in array block")

                for c in permission_split:
                    if not _is_valid_char(c):
                        raise ScopieError(
                            f"scopie-100 in permission: invalid character '{c}'"
                        )

            for c in action_block:
                if not _is_valid_char(c):
                    raise ScopieError(f"scopie-100 in action: invalid character '{c}'")

            if action_block not in permissions_split:
                return False

    return True


def is_allowed(
    actions: Sequence[str],
    permissions: Sequence[str],
    **vars: str,
) -> bool:
    """
    Whether or not the user actions are allowed with the given permissions.

        :param actions: Actions specifies what our user is attemping to do.
        :param permissions: Permissions specifies what our user has access to do.
        When using more then one permission, they are treated as a series of OR conditions,
        and a user will be allowed if they match any of the actions.
        :returns: If we are allowed to complete the actions.
        :raises ScopieError: If the actions or permissions are invalid based on scopie requirements
    """
    has_been_allowed = False
    if not permissions:
        return False

    if permissions[0] == "":
        raise ScopieError("scopie-106 in permission: permission was empty")

    if len(actions) == 0:
        raise ScopieError("scopie-106 in action: actions was empty")

    for permission in permissions:
        for action in actions:
            match = _compare_permission_to_action(permission, action, vars)
            if match and permission.startswith(deny_grant):
                return False
            elif match:
                has_been_allowed = True

    return has_been_allowed


def validate_actions(
    actions: Sequence[str],
) -> Optional[ScopieError]:
    """
    Checks whether the given actions are valid given the
    requirements outlined in the specification.

        :param actions: Given actions to validate.
        :returns: An error if one is found or None
    """
    if len(actions) == 0:
        return ScopieError("scopie-106: action array was empty")

    first_action = actions[0]

    for action in actions:
        if len(action) == 0:
            return ScopieError("scopie-106: action was empty")

        block_split = action.split(block_separator)
        for i, block in enumerate(block_split):
            for c in block:
                if not _is_valid_char(c):
                    return ScopieError(f"scopie-100: invalid character '{c}'")

    return None


def validate_permissions(
    permissions: Sequence[str],
) -> Optional[ScopieError]:
    """
    Checks whether the given permissions are valid given the
    requirements outlined in the specification.

        :param permissions: Given permissions to validate.
        :returns: An error if one is found or None
    """
    if len(permissions) == 0:
        return ScopieError("scopie-106: permission array was empty")

    for permission in permissions:
        if len(permission) == 0:
            return ScopieError("scopie-106: permission was empty")

        perm_block_split = permission.split(grant_separator, 1)
        grant = perm_block_split[0]
        if grant != allow_grant and grant != deny_grant:
            return ScopieError("scopie-107: permission does not start with a grant")

        blocks = perm_block_split[1].split(block_separator)

        for i, block in enumerate(blocks):
            if block == super_wildcard and i < len(blocks) - 1:
                return ScopieError("scopie-105: super wildcard not in the last block")
            if array_separator in block:
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
                if (
                    c != array_separator
                    and c != wildcard
                    and c != var_prefix
                    and not _is_valid_char(c)
                ):
                    return ScopieError(f"scopie-100: invalid character '{c}'")

    return None
