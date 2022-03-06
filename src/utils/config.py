import configparser
import json


def get_configurations():
    config = configparser.ConfigParser()
    config.read("../config.ini")

    return config
