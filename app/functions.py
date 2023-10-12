from configparser import ConfigParser

from pathlib import Path
from datetime import datetime

try:
    from icecream import ic

    def ic_set(debug):
        if debug:
            ic.enable()
        else:
            ic.disable()


except ImportError:  # Graceful fallback if IceCream isn't installed.
    doDebug: bool = False

    def ic(thing):  # just print to STDOUT
        if doDebug:
            print(thing)

    def ic_set(debug):
        global doDebug
        doDebug = debug
        ic("* icecream module not imported successfully, using STDOUT")


def nowString():
    return f"{datetime.now().strftime('%Y.%m.%d %T')} |> "


try:
    ic.configureOutput(prefix=nowString)
except AttributeError:
    pass


def getConfig(configFile: str = "config.ini"):
    config = ConfigParser(converters={'ListCSV'     : lambda x: [i.strip() for i in x.split(',')]
                                     ,'PathListCSV' : lambda x: [Path(i.strip()) for i in x.split(',')]
                                     }
                         )
    config.read(filenames=Path(configFile).resolve())
    ic_set(config.getboolean("APP","DEBUG"))
    return config
