from spacy.language import Language
from spacy.util import load_model_from_init_py

from . import entity_linker, util
from .entity_linker import EntityLinker, create

__version__ = util.pkg_meta["version"]


def load(**overrides):
    return load_model_from_init_py(__file__, **overrides)
