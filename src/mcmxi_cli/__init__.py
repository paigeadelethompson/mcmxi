import os, sys
from pathlib import Path
import importlib.resources as resources

import sopel
sopel.__version__ = "2024.1.17"
sopel._version_info = "2024.1.17"
sopel.version_info = "2024.1.17"
from sopel.cli.run import main as sopel_main

import mcmxi_config

def main():
    os.environ["SOPEL_CONFIG_DIR"] = (os.environ.get("SOPEL_CONFIG_DIR") != None
                                  and os.environ["SOPEL_CONFIG_DIR"]
                                  or str(Path.home() / Path(".mcmxi")))

    os.environ["SOPEL_CONFIG"] = (os.environ.get("SOPEL_CONFIG") != None
                                  and os.environ["SOPEL_CONFIG"]
                                  or "sopel.cfg")

    if not (Path.home() / Path(".mcmxi")).exists():
        for index in resources.files(mcmxi_config).iterdir():
            if str(index).endswith("sopel.cfg"):
                (Path.home() / Path(".mcmxi")).mkdir(parents = True)
                dat = open(str(index)).read()
                new_cfg = open(Path.home() / Path(".mcmxi") / Path("sopel.cfg"), "w")
                new_cfg.write(dat)
                print("Created default configuration file, please edit: ~/.mcmxi/sopel.cfg")
                sys.exit(0)
        
    sopel_main()
