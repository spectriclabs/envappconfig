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

def test_custom_transform():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo', transform=lambda x: int(x) + 2)
    config.configure({'FOO': 1})
    assert config.foo == 3

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

def test_default():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo', default=2)
    config.add_env('bar')
    config.configure({'BAR': 'baz'})
    assert config.foo == 2
    assert config.bar == 'baz'

def test_default_overridden():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo', default=2, transform=int)
    config.add_env('bar')
    config.configure({'FOO': '10', 'BAR': 'baz'})
    assert config.foo == 10
    assert config.bar == 'baz'

def test_duplicate_envs():
    config = envappconfig.EnvAppConfig()

    with pytest.raises(envappconfig.EnvAppConfigException):
        config.add_env('foo')
        config.add_env('foo')

def test_configure_not_called_for_getattr():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo')

    with pytest.raises(envappconfig.EnvAppConfigException):
        config.foo

def test_configure_not_called_for_asdict():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo')

    with pytest.raises(envappconfig.EnvAppConfigException):
        config.asdict()

def test_nonexistant_attr():
    config = envappconfig.EnvAppConfig()
    config.configure({})

    with pytest.raises(AttributeError):
        config.foo

def test_add_conf():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo', transform=int)
    config.configure({'FOO': '10'})
    config.add_conf('bar', 'baz')
    config.foo == 10
    config.bar == 'baz'

def test_add_existing_conf():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo', transform=int)
    config.configure({'FOO': '10'})

    with pytest.raises(envappconfig.EnvAppConfigException):
        config.add_conf('foo', 20)

def test_display_usage():
    config = envappconfig.EnvAppConfig(description='a foo bar app', prefix='someproj')
    config.add_env('foo', transform=int)
    config.add_env('barbaz', help='some bar')
    config.add_env('boom', help='kabam')
    config.usage()

def test_use_os_environ():
    config = envappconfig.EnvAppConfig()
    config.add_env('foo', default=1, transform=int)
    config.configure()
    assert len(config.asdict()) > 0

def test_usage_when_not_exists(mocker):
    config = envappconfig.EnvAppConfig()
    config.add_env('foo')
    mocker.patch('envappconfig.EnvAppConfig.usage')
    mocker.patch('sys.exit')
    config.configure({'BAR': '1'})
    envappconfig.EnvAppConfig.usage.assert_called_once()
    sys.exit.assert_called_once_with(1)
