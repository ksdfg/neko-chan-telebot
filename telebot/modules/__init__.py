import glob
import importlib
from os.path import dirname, basename, isfile

from telebot import config

# get names of all the module .py files currently in the repo
mod_paths = glob.glob(dirname(__file__) + "/*.py")
ALL_MODULES = sorted(
    [basename(f)[:-3] for f in mod_paths if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")]
)

# Import all modules
imported_mods = {}
for module_name in ALL_MODULES:
    # check whether module is to be loaded or not
    if (config.LOAD and module_name not in config.LOAD) or (config.NO_LOAD and module_name in config.NO_LOAD):
        continue

    imported_module = importlib.import_module("telebot.modules." + module_name)

    # add imported module to the dict of modules, to be used later
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__.split(".")[-1]
    imported_mods[imported_module.__mod_name__.lower()] = imported_module
