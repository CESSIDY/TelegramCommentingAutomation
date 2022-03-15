import configparser
import os


def get_configurations():
    config_file_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..', "config.ini"))
    config = configparser.ConfigParser()
    config.read(config_file_path)

    return config
