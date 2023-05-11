import json
import os
import argparse

from colander_client.client import Client


class Configuration:
    base_url: str
    api_key: str
    is_valid: bool = False
    default_configuration_folder = f'{os.path.expanduser("~")}/.config/pirogue/'
    default_configuration_path: str

    def __init__(self, prefix=''):
        self.default_configuration_folder = f'{prefix}{self.default_configuration_folder}'
        self.default_configuration_path = f'{self.default_configuration_folder}colander-config.json'
        os.makedirs(self.default_configuration_folder, exist_ok=True)
        self.load_configuration_file()

    def load_configuration_file(self):
        if os.path.isfile(self.default_configuration_path):
            with open(self.default_configuration_path, mode='r') as config_file:
                config = json.load(config_file)
            if 'base_url' not in config or 'api_key' not in config:
                raise Exception(f'The configuration stored in {self.default_configuration_path} is invalid')
            else:
                self.base_url = config.get('base_url')
                self.api_key = config.get('api_key')
                self.is_valid = True

    def write_configuration_file(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.is_valid = True
        with open(self.default_configuration_path, mode='w') as config_file:
            config = {
                'base_url': base_url,
                'api_key': api_key,
            }
            json.dump(config, config_file, indent=2)

    def get_colander_client(self):
        if self.is_valid:
            return Client(base_url=self.base_url, api_key=self.api_key)
        else:
            raise Exception('Unable to correctly configure the Colander client')
