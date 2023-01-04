from collections import OrderedDict
from copy import copy
from typing import Any, Callable, Dict, Iterable, Optional, Union

import os
import re
import sys

from .exceptions import EnvAppConfigException

NAME_PATTERN = re.compile('[A-Za-z]+[A-Za-z0-9_]*')

def apply_prefix(prefix: Optional[str], name: str) -> str:
    return f'{prefix}_{name}'.upper() if prefix else name.upper()

def longest_str_len(strings: Iterable) -> int:
    return max(len(s) for s in strings)

def valid_name(name: str) -> bool:
    if NAME_PATTERN.fullmatch(name) is None:
        return False

    return True

class Env:
    def __init__(
        self,
        name: str,
        default: Optional[Any],
        help: str,  # pylint: disable=redefined-builtin
        transform: Callable,
    ) -> None:
        self.name = name
        self.default = default
        self.help = help
        self.transform = transform

    def raw_value(self, environ) -> str:
        return environ[self.name]

    def configure(self, environ) -> Any:
        if self.name not in environ and self.default:
            return self.default

        if self.name not in environ:
            raise EnvAppConfigException(f'{self.name} not in environment')

        return self.transform(environ[self.name])

    def default_text(self) -> str:
        if self.default is None:
            return ''

        return f' (default={self.default})'

    def usage(self, indent: int, longest: int) -> None:
        indent_str = ' ' * indent
        print(f'{indent_str}{self.name.ljust(longest)} - {self.help}{self.default_text()}')

class EnvAppConfig:
    def __init__(
        self,
        prefix: Optional[str]=None,
        description: Optional[str]=None,
    ) -> None:
        self.existing_attributes = ('add_conf', 'add_env', 'asdict', 'configure', 'usage')
        self.configure_called = False
        self.prefix = prefix.strip() if type(prefix) is str else None
        self.description = description.strip() if type(description) is str else None
        self.full_names = set()
        self.envs = OrderedDict()
        self.confs = {}

        if self.prefix is not None and not valid_name(self.prefix):
            raise EnvAppConfigException(f'{self.prefix} is not a valid prefix')

    def add_env(
        self,
        name: str,
        default: Optional[Any]=None,
        help: str='Description not provided',  # pylint: disable=redefined-builtin
        transform=str,
    ) -> None:
        self.configure_called = False
        name = name.strip().lower()

        # Can't use hasattr(self, name) here because it will call __getattr__(),
        # which raises an exception if configure() hasn't been called yet.
        if name in self.existing_attributes:
            raise EnvAppConfigException(f'{name} is already an attribute of EnvAppConfig')

        if not valid_name(name):
            raise EnvAppConfigException(f'{name} is not a valid environment variable name')

        if name in self.envs or name in self.confs:
            raise EnvAppConfigException(f'{name} already specified in EnvAppConfig')

        full_name = apply_prefix(self.prefix, name)
        self.full_names.add(full_name)
        self.envs[name] = Env(full_name, default, help, transform)

    def __getattr__(self, name):
        if not self.configure_called:
            raise EnvAppConfigException('configure() needs to be called before config values are available')

        if name not in self.confs:
            raise AttributeError(f'{name} not available in config')

        return self.confs[name]

    def asdict(self):
        if not self.configure_called:
            raise EnvAppConfigException('configure() needs to be called before config values are available')

        return copy(self.confs)

    def configure(self, environ: Optional[Union[os._Environ, Dict[str, str]]]=None) -> None:
        if environ is None:
            environ = os.environ

        is_missing_envs = False

        for name, env in self.envs.items():
            try:
                self.confs[name] = env.configure(environ)
            except EnvAppConfigException:
                print(f'Error: {env.name} not available in environment')
                is_missing_envs = True
            except Exception:
                print(f'Error while trying transform {env.name} value "{env.raw_value(environ)}"')
                self.usage()
                raise

        if is_missing_envs:
            self.usage()
            sys.exit(1)

        self.configure_called = True

    def usage(self) -> None:
        print('\nusage:\n')

        if self.description:
            print(f'{self.description}\n')

        if len(self.envs.keys()) > 0:
            print('Config Environment Variables:')

        longest_name_len = longest_str_len(self.full_names)

        for env in self.envs.values():
            env.usage(1, longest_name_len)

    def add_conf(self, name: str, value: Any) -> None:
        name = name.strip()

        # Can't use hasattr(self, name) here because it will call __getattr__(),
        # which raises an exception if configure() hasn't been called yet.
        if name in self.existing_attributes:
            raise EnvAppConfigException(f'{name} is already an attribute of EnvAppConfig')

        if name in self.envs or name in self.confs:
            raise EnvAppConfigException(f'{name} already specified in EnvAppConfig')

        self.confs[name] = value
