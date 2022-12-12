import sys

import pytest

import envappconfig

def test_envappconfig_desc():
    config = envappconfig.EnvAppConfig(description='Builds a config from environment variables')
    assert config.description is not None

def test_basic_configure():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo', transform=int)
    config.add_env('bar')
    config.configure({'FOO': '1', 'BAR': 'baz'})
    assert config.foo == 1
    assert config.bar == 'baz'

def test_envappconfig_prefix():
    config = envappconfig.EnvAppConfig(prefix='someproj')
    config.add_env('foo', transform=int)
    config.add_env('bar')
    config.configure({'SOMEPROJ_FOO': '1', 'SOMEPROJ_BAR': 'baz'})
    assert config.foo == 1
    assert config.bar == 'baz'

def test_envappconfig_asdict():
    config = envappconfig.EnvAppConfig(prefix='someproj')
    config.add_env('foo', transform=int)
    config.add_env('bar')
    config.configure({'SOMEPROJ_FOO': '1', 'SOMEPROJ_BAR': 'baz'})
    d = config.asdict()
    assert d['foo'] == 1
    assert d['bar'] == 'baz'


def test_display_usage():
    config = envappconfig.EnvAppConfig(description='a foo bar app', prefix='someproj')
    config.add_env('foo', transform=int)
    config.add_env('barbaz', help='some bar')
    config.add_env('boom', help='kabam')
    config.usage()

def test_usage_when_not_exists(mocker):
    config = envappconfig.EnvAppConfig()
    config.add_env('foo')
    mocker.patch('envappconfig.EnvAppConfig.usage')
    mocker.patch('sys.exit')
    config.configure({'BAR': '1'})
    envappconfig.EnvAppConfig.usage.assert_called_once()
    sys.exit.assert_called_once_with(1)
