import os
import sys
from copy import deepcopy

import yaml


def load():
    with open('hamper.conf') as config_file:
        config = yaml.load(config_file)
    config = replace_env_vars(config)

    for key in ['server', 'port', 'nickname', 'channels']:
        if (key not in config) or (not config[key]):
            print('You need to define {0} in the config file.'.format(key))
            sys.exit()

    return config


def replace_env_vars(conf):
    """Fill `conf` with environment variables, where appropriate.

    Any value of the from $VAR will be replaced with the environment variable
    VAR. If there are sub dictionaries, this function will recurse.

    This will preserve the original dictionary, and return a copy.
    """
    d = deepcopy(conf)
    for key, value in d.items():
        if type(value) == dict:
            d[key] = replace_env_vars(value)
        elif type(value) == str:
            if value[0] == '$':
                var_name = value[1:]
                d[key] = os.environ[var_name]

    return d
