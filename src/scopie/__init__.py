"""
Authorization engine for configuring per user per feature access control.
Access is configured via plain text and handled directly via code.
Configuration storage is controlled by you, scopie just handles the logic.
"""

from .scopie import (
    ScopieError,
    is_allowed,
    validate_scopes,
    array_seperator,
    block_seperator,
    wildcard,
    super_wildcard,
    var_prefix,
    allow_permission,
    deny_permission,
)
