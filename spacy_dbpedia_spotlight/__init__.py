from spacy.language import Language

from . import entity_linker, util

__version__ = util.pkg_meta["version"]

Language.factories['overwrite_vectors'] = lambda nlp, **cfg: EntityLinker(nlp, **cfg)

def load(language_code, nlp=None):
    """Get a nlp with the dbpedia spotlight linker.
    
    Params:

    - ``language_code``: one of the language codes supported ``('en', 'de', 'es', 'fr', 'it', 'nl', 'pt', 'ru')``

    - nlp: an existing nlp model to attach the entity recogniser and linker, if absent a new one will be created and returned
    """
    return entity_linker.DbpediaLinker(language_code, nlp).nlp


class EntityLinker(object):
    name = "annotate_dbpedia_spotlight"

    def __init__(self, nlp, language_code='en'):
        self.nlp = entity_linker.DbpediaLinker(language_code).nlp

    def __call__(self, doc):
        new_ents = self.nlp(doc).ents
        doc.ents = list(doc.ents) + new_ents

        return doc