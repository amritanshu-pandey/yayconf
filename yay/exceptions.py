class ConfigurationError(Exception):
    """Generic configuration errors"""
    pass


class ConfigurationFileNotFound(ConfigurationError):
    """Configuration file not found"""
    pass


class ConfigurationMissingKeys(ConfigurationError):
    """Configuratino missing a required key"""
    pass
