import sys

import pytest

import envappconfig

def test_valid_name():
    assert envappconfig.valid_name('foo') == True
    assert envappconfig.valid_name('abc123') == True
    assert envappconfig.valid_name('the_quick_brown_fox') == True
    assert envappconfig.valid_name('_test') == False
    assert envappconfig.valid_name('1fail') == False
    assert envappconfig.valid_name('this or that') == False

def test_envappconfig_desc():
    env = envappconfig.EnvAppConfig(description='Builds a config from environment variables')
    assert env.description is not None

def test_basic_configure():
    env = envappconfig.EnvAppConfig()
    env.add_env('foo', transform=int)
    env.add_env('bar')
    config = env.configure({'FOO': '1', 'BAR': 'baz'})
    assert config.foo == 1
    assert config.bar == 'baz'

def test_custom_transform():
    env = envappconfig.EnvAppConfig()
    env.add_env('foo', transform=lambda x: int(x) + 2)
    config = env.configure({'FOO': 1})
    assert config.foo == 3

def test_envappconfig_prefix():
    env = envappconfig.EnvAppConfig(prefix='someproj')
    env.add_env('foo', transform=int)
    env.add_env('bar')
    config = env.configure({'SOMEPROJ_FOO': '1', 'SOMEPROJ_BAR': 'baz'})
    assert config.foo == 1
    assert config.bar == 'baz'

def test_default():
    env = envappconfig.EnvAppConfig()
    env.add_env('foo', default=2)
    env.add_env('bar')
    config = env.configure({'BAR': 'baz'})
    assert config.foo == 2
    assert config.bar == 'baz'

def test_usage_display_default(capfd):
    env = envappconfig.EnvAppConfig()
    env.add_env('foo', default=2)
    env.usage()
    out, err = capfd.readouterr()
    assert '(default=2)' in out

def test_missing_envs(capfd, mocker):
    mocker.patch('sys.exit')
    env = envappconfig.EnvAppConfig()
    env.add_env('foo')
    env.add_env('bar')
    config = env.configure({})
    out, err = capfd.readouterr()
    assert 'Error: FOO' in out
    assert 'Error: BAR' in out
    sys.exit.assert_called_once_with(1)

def test_default_overridden():
    env = envappconfig.EnvAppConfig()
    env.add_env('foo', default=2, transform=int)
    env.add_env('bar')
    config = env.configure({'FOO': '10', 'BAR': 'baz'})
    assert config.foo == 10
    assert config.bar == 'baz'

def test_duplicate_envs():
    env = envappconfig.EnvAppConfig()

    with pytest.raises(envappconfig.EnvAppConfigException):
        env.add_env('foo')
        env.add_env('foo')

def test_invalid_name():
    config = envappconfig.EnvAppConfig()

    with pytest.raises(envappconfig.EnvAppConfigException):
        config.add_env('1fail')

def test_invalid_prefix():
    with pytest.raises(envappconfig.EnvAppConfigException):
        envappconfig.EnvAppConfig(prefix='_invalid')

def test_nonexistant_attr():
    env = envappconfig.EnvAppConfig()
    config = env.configure({})

    with pytest.raises(AttributeError):
        config.foo

def test_display_usage():
    env = envappconfig.EnvAppConfig(description='a foo bar app', prefix='someproj')
    env.add_env('foo', transform=int)
    env.add_env('barbaz', help='some bar')
    env.add_env('boom', help='kabam')
    env.usage()

def test_use_os_environ():
    env = envappconfig.EnvAppConfig()
    env.add_env('foo', default=1, transform=int)
    config = env.configure()
    assert config.foo == 1

def test_usage_when_not_exists(mocker):
    env = envappconfig.EnvAppConfig()
    env.add_env('foo')
    mocker.patch('envappconfig.EnvAppConfig.usage')
    mocker.patch('sys.exit')
    config = env.configure({'BAR': '1'})
    envappconfig.EnvAppConfig.usage.assert_called_once()
    sys.exit.assert_called_once_with(1)

def test_bad_transform(mocker):
    env = envappconfig.EnvAppConfig()
    env.add_env('foo', transform=int)
    mocker.patch('envappconfig.EnvAppConfig.usage')

    with pytest.raises(ValueError):
        config = env.configure({'FOO': 'abc'})

    envappconfig.EnvAppConfig.usage.assert_called_once()

def test_additional_confs():
    env = envappconfig.EnvAppConfig()
    env.add_env('foo', default=1, transform=int)
    config = env.configure()
    assert config.foo == 1
    config.bar = 2
    assert config.bar == 2
