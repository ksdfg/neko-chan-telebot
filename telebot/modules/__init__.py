import glob
from os.path import dirname, basename, isfile

# get names of all the module .py files currently in the repo
mod_paths = glob.glob(dirname(__file__) + "/*.py")
ALL_MODULES = sorted(
    [basename(f)[:-3] for f in mod_paths if isfile(f) and f.endswith(".py") and not f.endswith('__init__.py')]
)
