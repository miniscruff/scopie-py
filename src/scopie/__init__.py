"""
Authorization engine for configuring per user per feature access control.
Access is configured via plain text and handled directly via code.
Configuration storage is controlled by you, scopie just handles the logic.
"""

from .scopie import (
    ScopieError,
    is_allowed,
    validate_actions,
    validate_permissions,
    array_separator,
    block_separator,
    wildcard,
    super_wildcard,
    var_prefix,
    allow_grant,
    deny_grant,
    grant_separator,
)
