import logging
import os
import yaml

from yay.exceptions import (
        ConfigurationFileNotFound,
        ConfigurationMissingKeys
    )

LOG = logging.getLogger(__name__)


class Configuration:
    """
      1. Read configuration options from various sources viz. config
         schema file, configuration file and environment variables
      2. ensure that mandatory values are available
      3. prepare a single dictionary containing the configuration options
         read from various sources

         - Expected format of schema file:

         .. code-block:: yaml

            ---
            - name: CONFIG-OPTION-1
              descrption: Description of CONFIG-OPTION-1
              required: True
              default: <Default value of CONFIG-OPTION-1>

            - name: CONFIG-OPTION-2
              descrption: Description of CONFIG-OPTION-2
              required: False
              default: <Default value of CONFIG-OPTION-2>

         - Expected format of configuration file:

         .. code-block:: yaml

            ---
            CONFIG-OPTION-1: value1
            CONFIG-OPTION-2: value2

    Class attributes:
      1. ``schema_file``: Path to the config schema file. This is used
         to define the mandatory fields and default values.
      2. ``config_file``: Path to the user specified configuration file
      3. ``read_from_env``: If True, Default values specified in the config
         schema file are used to prepare the config dictionary
      4. ``use_defaults``: If True, Default values specified in the config
         schema file are used to prepare the config dictionary
    """

    def __init__(self, schema_file, config_file,
                 read_from_env=False,
                 use_defaults=True):
        """
        Read config options from various sources

        Arguments:
        schema_file {str} --
                    Path to the config schema file. This is used to
                    define the mandatory fields and default values.
        config_file {str} -- Path to the configuration file
        read_from_env {boolean} --
                    If True, values for the options defined in schema,
                    are read from the environment variables.
        use_defaults {boolean} --
                    If True, Default values specified in the config schema
                    file are used to prepare the config dictionary

        Raises:
            ConfigurationFileNotFound -- Raise exception if configuration files
                    path is not correct.
        """

        self._config = {}
        self.schema_file = schema_file
        self.config_file = config_file
        self.read_from_env = read_from_env
        self.use_defaults = use_defaults

    def _read_config(self):
        """
        Read the config options from a YAML file

        Returns:
            dict -- Configuration options read from YAML file
        """
        if not os.path.isfile(self.config_file):
            raise ConfigurationFileNotFound(
                f'Config file not found: {self.config_file}')
        with open(self.config_file, 'r') as config_yaml:
            cfg = yaml.safe_load(config_yaml)
        if not isinstance(cfg, dict):
            cfg = {}
            LOG.warning(
                f'Unable to parse the configuration file {self.config_file}.'
                ' Default config values will be used.')
        return cfg

    @property
    def schema(self):
        """
        Read schema file

        :param schema_file: Path to the schema file to read
        :type schema_file: str

        Returns:
            dict -- Config options read from schema file
        """

        if not os.path.isfile(self.schema_file):
            raise ConfigurationFileNotFound(
                f'Config schema file not found: {self.schema_file}')

        with open(self.schema_file, 'r') as schema_yaml:
            cfg = yaml.safe_load(schema_yaml)
        return cfg

    def _get_config_from_env(self):
        """
        Read the values of the config options (specified in config
        schema file) from environment variables.

        returns:
            dict -- Config options read from environment variables
        """

        cfg = {
            i['name']: os.environ.get(i['name'])
            for i in self.schema
            if os.environ.get(i['name'])
        }

        return cfg

    def _check_mandatory_fields(self):
        """
        Check if all the mandatory fields, as specified in the config
        schema file are available in the final configuration dcitionary
        prepared after reading config schema file, config file and
        environment variables.

        Raises:
            AttributeError -- Raise exception is any mandatory field
                              is missing
        """

        missing_keys = []

        for i in self.schema:
            if i['required'] and i['name'] not in self._config:
                missing_keys.append(i['name'])

        if missing_keys:
            raise ConfigurationMissingKeys(
                f'Config is missing required fields: {missing_keys}')

    def _merge_configs(self):
        """
        Read configuration options from following sources and merge
        the configs to a single dictionary:
            1. Configuration schema file, if a default
               value is specified and ``self.use_defaults`` is True
            2. Configuration file
            3. Environment variables

        If same config option is available in multiple sources, priority
        is given to the latter sources.

        Returns:
            dict -- Config options read from different sources
        """

        config_from_file = self._read_config()

        default_config_values = {
            i['name']: i['default'] for i in self.schema
            if 'default' in i
        } if self.use_defaults else {}

        final_dict = default_config_values.copy()
        final_dict.update(config_from_file)

        if self.read_from_env:
            config_from_env = self._get_config_from_env()
            final_dict.update(config_from_env)

        return final_dict

    def print_config_file(self):
        """Print the sample configuration file from schema
        """
        config_dict = {
            i['name']: i.get('default', '') for i in self.schema
        }
        print(yaml.dump(config_dict, default_flow_style=False))

    @property
    def config(self):
        """
        Representation of the Configuration as a dictionary

        Schema of the output dictionary:

        .. code-block:: python

           {
               'CONFIG-OPTION-1': 'value1',
               'CONFIG-OPTION-2': 'value2'
           }

        Returns:
            dict -- each key-value pair in the dict corresponds to a
            config option and its value.
        """
        self._config = self._merge_configs()
        self._check_mandatory_fields()
        return self._config
