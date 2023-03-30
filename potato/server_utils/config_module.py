"""
Config module.
"""

import yaml
from copy import deepcopy
#from .schemas import SingleConf

config = {}

class SingleConf:
    __instance = None

    def __new__(cls, *args, **kwargs):
        print(cls.__instance)
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

def init_config(args):
    global config
    with open(args.config_file, "r") as file_p:
        config.update(yaml.safe_load(file_p))

    config.update(
        {
            "verbose": args.verbose,
            "very_verbose": args.very_verbose,
            "__debug__": args.debug,
            "__config_file__": args.config_file,
        }
    )

    single = SingleConf()
    single.conf = deepcopy(config)

