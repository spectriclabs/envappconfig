from collections import OrderedDict
from copy import copy
from typing import Any, Callable, Optional

import os
import sys

def apply_prefix(prefix: Optional[str], name: str) -> str:
    return f'{prefix}_{name}'.upper() if prefix else name

def longest_str_len(strings: Iterable) -> int:
    return max([len(s) for s in strings])

class Env:
    def __init__(
        self,
        name: str,
        required: bool,
        default: Optional[Any],
        help: str,
        translate: Callable,
    ) -> None:
        self.name = name
        self.required = required
        self.default = default
        self.help = help
        self.translate = translate

    def configure(self, environ) -> Any:
        if self.name not in environ and self.default:
            return default

        if self.name not in environ:
            raise EnvAppConfigException(f'{name} not in environment')

        return self.translate(environ[self.name])

    def usage(self, indent: int=1, longest: int=0) -> None:
        indent_str = ' ' * indent
        print(f'{indent_str}{self.name:<longest} {self.description}')


class EnvAppConfig:
    def __init__(
        self,
        prefix: Optional[str]=None,
        description: Optional[str]=None,
    ) -> None:
        self.prefix = prefix.strip() if type(prefix) is str else None
        self.description = description.strip() if type(description) is str else None
        self.full_names = set()
        self.envs = OrderedDict()
        self.confs = {}

    def add_env(
        self,
        name: str,
        required: bool=False,
        default: Optional[Any]=None,
        help: str='Description not provided',
        translate=str,
    ) -> None:
        self.configure_called = False
        name = name.strip()

        if name in self.envs:
            raise EnvAppConfigException(f'{name} already specified in EnvAppConfig')

        full_name = apply_prefix(self.prefix, name)
        self.full_names.add(full_name)
        self.envs[name] = Env(full_name, required, default, help, translate)

    def __getattr__(self, name):
        if not self.configure_called:
            raise EnvAppConfigException('configure() needs to be called before config values are available')

        if name not in self.confs:
            raise AttributeError(f'{name} not available in config')

        return self.confs[name]

    def asdict(self):
        if not self.configure_called:
            raise EnvAppConfigException('configure() needs to be called before config values are available')

        return copy(self.conf)

    def configure(self, environ=os.environ) -> None:
        for name, env in self.envs:
            try:
                self.confs[name] = env.configure(environ)
            except EnvAppConfigException:
                print(f'Error: {env.name} not available in environment\n')
                self.usage()
                sys.exit(1)

        self.configure_called = True

    def usage(self) -> None:
        print('usage:\n')

        if self.description:
            print(f'{description}\n')

        if len(self.envs.keys()) > 0:
            print('Config Environment Variables:')

        for env in self.envs.values():
            env.usage(indent=1, longest=longest_str_len(self.full_names))

    def add_conf(self, name: str, value: Any) -> None:
        name = name.strip()

        if name in self.envs or name in self.confs:
            raise EnvAppConfigException(f'{name} already specified in EnvAppConfig')

        self.confs[name] = value
