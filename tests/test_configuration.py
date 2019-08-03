import pytest

from yay import Configuration
from yay.exceptions import ConfigurationFileNotFound


def test_Configuration(mocker):
    """Ensure that object of type Configuration has correct defaults
    """
    mocker.patch.object(Configuration, '_read_config_schema')

    cfg = Configuration()
    assert cfg.config_schema_file is None
    assert cfg.config_file is None
    assert cfg.read_from_env is False
    assert cfg.use_defaults is True


@pytest.mark.parametrize('config_file', [
    'nonexisting', 'valid', 'empty'
])
def test__read_config(config_file, empty_config_file, faker,
                      mocker, valid_config_file):
    """Ensure _read_config member function behaves as expected
       when the following type of config files are input:
       1. A config file that doesn't exist
       2. Valid config file
       3. An empty config file
    """
    mocker.patch.object(Configuration, '_read_config_schema')
    if config_file == 'nonexisting':
        cfg = Configuration(config_file=faker.file_path())
        with pytest.raises(ConfigurationFileNotFound):
            cfg._read_config()
    else:
        input_cfg, cfg_dict = valid_config_file \
            if config_file == 'valid' \
            else empty_config_file

        cfg = Configuration(config_file=input_cfg)

        assert cfg._read_config() == cfg_dict


@pytest.mark.parametrize('schema_file', [
    'nonexisting', 'valid'
])
def test__read_config_schema(schema_file, faker, fake_config_schema_and_dict,
                             mocker, valid_config_file):
    """Ensure _read_config_schema member function behaves as expected
       when the following type of config files are input:
       1. A schema file that doesn't exist
       2. Valid schema file
    """
    if schema_file == 'nonexisting':
        cfg = Configuration(config_file=faker.file_path())
        with pytest.raises(ConfigurationFileNotFound):
            cfg._read_config()
    elif schema_file == 'valid':
        fake_schema_file = fake_config_schema_and_dict[0]
        fake_schema_dict = fake_config_schema_and_dict[1]
        cfg = Configuration()

        assert cfg._read_config_schema(
            schema_file=fake_schema_file) == fake_schema_dict


def test__get_config_from_env(fake_config_schema_and_dict):
    """Ensure that the function reads the expected fields from env\
       and create dictionary in expected format.
    """
    schema_file = fake_config_schema_and_dict[0]
    schema_dict = fake_config_schema_and_dict[1]

    cfg = Configuration(config_schema_file=schema_file)

    cfg_from_env = cfg._get_config_from_env()

    x_cfg = {
        i['name']: i['environment'] for i in schema_dict
        if i.get('priority') == 'environment'
    }

    assert x_cfg == cfg_from_env


def test_Configuration_with_env(fake_config_schema_and_dict):
    """Ensure that the configuration values are read correctly from the
       following sources:
            1. Config schema file
            2. Configuration file
            3. Environment variables

       If same config is available in multiple sources priority is given
       to the latter sources
    """

    schema_file, schema_dict, config_file = fake_config_schema_and_dict

    cfg = Configuration(config_schema_file=schema_file,
                        config_file=config_file,
                        read_from_env=True)

    final_config = cfg.as_dict

    x_config = {
        i['name']: i[i['priority']] for i in schema_dict
    }

    assert final_config == x_config


def test_Configuration_without_env(fake_config_schema_and_dict):
    """Ensure that the configuration values are read correctly from the
       following sources:
            1. Config schema file
            2. Configuration file

       If same config is available in multiple sources priority is given
       to the latter sources.
       Since the COnfiguration object is created with ``read_from_env`` as
       False, config values must not be read from environment variables.
    """

    schema_file, schema_dict, config_file = fake_config_schema_and_dict

    cfg = Configuration(config_schema_file=schema_file,
                        config_file=config_file,
                        read_from_env=False)

    final_config = cfg.as_dict

    x_config = {
        i['name']: i[i['priority']] for i in schema_dict
        if i['priority'] != 'environment'
    }
    x_config.update(
        {
            i['name']: i['config'] for i in schema_dict
            if i['priority'] == 'environment'
        }
    )

    assert final_config == x_config


def test_print_config_file(fake_config_schema_and_dict, capsys):
    """Ensure that sample configuration file when printed has correct
       options and values
    """

    schema_file, schema_dict, config_file = fake_config_schema_and_dict

    cfg = Configuration(config_schema_file=schema_file)

    cfg.print_config_file()
    out, _ = capsys.readouterr()

    for i in schema_dict:
        assert f"{i['name']}: {i['default']}" in out
