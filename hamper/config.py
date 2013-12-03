import os
import sys
from copy import deepcopy

import yaml


def load():
    try:
        with open('hamper.conf') as config_file:
            config = yaml.load(config_file)
    except IOError:
        config = {}

    config = replace_env_vars(config)

    # Fill in data from the env:
    for k, v in os.environ.items():
        try:
            config[k] = yaml.load(v)
        except yaml.error.YAMLError:
            config[k] = v

    # Special case: database
    if 'DATABASE_URL' in os.environ:
        config['db'] = os.environ['DATABASE_URL']

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
