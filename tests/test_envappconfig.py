import pytest

from envappconfig import EnvAppConfig

def test_envappconfig_desc():
    config = EnvAppConfig(description='Builds a config from environment variables')
    assert config.description is not None
