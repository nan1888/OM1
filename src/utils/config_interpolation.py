"""
Environment variable interpolation utilities for configuration files.

This module provides functions to interpolate environment variables in
configuration dictionaries loaded from JSON5 files.

Supported syntax:
- ${VAR_NAME} - Replace with environment variable value, keep original if not found
- ${VAR_NAME:-default_value} - Replace with env var value, use default if not found
"""

import os
import re
from typing import Any


def interpolate_env_vars(config: Any) -> Any:
    """
    Recursively interpolate environment variables in configuration values.

    This function traverses the configuration structure and replaces
    environment variable placeholders with their actual values from
    the environment.

    Parameters
    ----------
    config : Any
        Configuration value (can be dict, list, str, or other types)

    Returns
    -------
    Any
        Configuration with environment variables interpolated

    Examples
    --------
    >>> os.environ['API_KEY'] = 'secret123'
    >>> interpolate_env_vars({'key': '${API_KEY}'})
    {'key': 'secret123'}

    >>> interpolate_env_vars({'key': '${MISSING:-default}'})
    {'key': 'default'}

    >>> interpolate_env_vars(['${API_KEY}', 'static'])
    ['secret123', 'static']
    """
    if isinstance(config, str):
        return _interpolate_string(config)
    elif isinstance(config, dict):
        return {k: interpolate_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [interpolate_env_vars(item) for item in config]
    else:
        return config


def _interpolate_string(value: str) -> str:
    """
    Interpolate environment variables in a single string.

    Supports two formats:
    - ${VAR_NAME} - Replaced with env var value, keeps original if not found
    - ${VAR_NAME:-default} - Replaced with env var value or default

    Parameters
    ----------
    value : str
        String potentially containing environment variable placeholders

    Returns
    -------
    str
        String with environment variables interpolated
    """
    # Pattern matches ${VAR_NAME} or ${VAR_NAME:-default_value}
    # Group 1: variable name
    # Group 2: default value (optional, after :-)
    pattern = r"\$\{([^}:]+)(?::-(.*?))?\}"

    def replacer(match):
        var_name = match.group(1)
        default_value = match.group(2)

        # Get environment variable
        env_value = os.environ.get(var_name)

        if env_value is not None:
            return env_value
        elif default_value is not None:
            return default_value
        else:
            # Keep original placeholder if env var doesn't exist and no default
            return match.group(0)

    return re.sub(pattern, replacer, value)
