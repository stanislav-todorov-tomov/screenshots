from configparser import ConfigParser


class Configuration:

    @classmethod
    def connection_string(cls):
        return cls._read_property('connection_string')

    @classmethod
    def base_dir(cls):
        return cls._read_property('base_dir')

    @classmethod
    def _read_property(cls, prop: str):
        config: ConfigParser = ConfigParser()
        config.read('properties.cfg')
        return config.get('DEFAULT', prop)
