import spacy
import requests
from spacy.language import Language

from spacy.tokens import Span

# span extension attribute for raw json
Span.set_extension("dbpedia_raw_result", default=None)

@Language.factory('dbpedia_spotlight', default_config={
    'language_code': None,
    'dbpedia_rest_endpoint': None,
    'overwrite_ents': True,
    'debug': False
})
def dbpedia_spotlight_factory(nlp, name, language_code, dbpedia_rest_endpoint, overwrite_ents, debug):
    '''Factory of the pipeline stage `dbpedia_spotlight`.
    Parameters:
    - `language_code`: which language to use for entity linking. Possible values are listed in EntityLinker.supported_languages. If the parameter is left as None, the language code is matched with the nlp object currently used.
    - `dbpedia_rest_endpoint`: this needs to be configured if you want to use a different REST endpoint from the default `EntityLinker.base_url`. Example: `http://localhost:2222/rest` for a localhost server
    - `overwrite_ents`: if set to False, it won't overwrite `doc.ents` in cases of overlapping spans with current entities, and only produce the results in `doc.spans['dbpedia_ents']. If it is True, it will move the entities from doc.ents into `doc.spans['ents_original']`
    - `debug`: prints several debug information to stdout
    '''
    if debug:
        print('dbpedia_spotlight_factory:', nlp, 'language_code', language_code, 'dbpedia_rest_endpoint', dbpedia_rest_endpoint, 'overwrite_ents', overwrite_ents)
    # take the language code from the nlp object
    nlp_lang_code = nlp.meta['lang']
    if debug:
        print('nlp.meta["lang"]=', nlp_lang_code)
    # language_code can override the language code from the nlp object
    if not language_code:
        language_code = nlp_lang_code
    return EntityLinker(language_code, dbpedia_rest_endpoint, overwrite_ents, debug)


class EntityLinker(object):
    '''This class manages the querying of DBpedia and attaches the found entities to the document'''
    # default location of the service
    base_url = 'http://api.dbpedia-spotlight.org'
    # list of supported languages
    supported_languages = ['en', 'de', 'es', 'fr', 'it', 'nl', 'pt', 'ru']

    def __init__(self, language_code='en', dbpedia_rest_endpoint=None, overwrite_ents=True, debug=False):
        # constructor of the pipeline stage
        if language_code not in self.supported_languages:
            raise ValueError(f'Linker not available in {language_code}. Choose one of {self.supported_languages}')
        self.language_code = language_code
        self.overwrite_ents = overwrite_ents
        self.debug = debug
        if dbpedia_rest_endpoint:
            # override the default endpoint, e.g., 'http://localhost:2222/rest'
            self.api_endpoint = dbpedia_rest_endpoint
            if debug:
                print('api_endpoint has been manually set to', self.api_endpoint)
        else:
            # use the default endpoint for the language selected
            self.api_endpoint = f'{self.base_url}/{self.language_code}'
            if debug:
                print('api_endpoint has been built as', self.api_endpoint)

    def __call__(self, doc):
        # called in the pipeline
        annotate_dbpedia_spotlight(doc, self.api_endpoint, self.overwrite_ents, self.debug)
        return doc

def create(language_code, nlp=None):
    '''Creates an instance of a Language with the DBpedia EntityLinker pipeline stage.
    If the parameter `nlp` is None, it will return a blank language with the EntityLinker.
    If the parameter `nlp` is an existing Language, it simply adds the EntityLinker pipeline stage (equivalent to `nlp.add`)
    '''
    if not nlp:
        nlp = spacy.blank(language_code)
    nlp.add_pipe('dbpedia_spotlight')
    return nlp


def annotate_dbpedia_spotlight(doc, api_endpoint, overwrite_ents, debug=True):
    if debug:
        print('running remote', api_endpoint)

    response = requests.get(f'{api_endpoint}/annotate', headers={'accept': 'application/json'}, params={'text': doc.text})
    response.raise_for_status()
    data = response.json()
    if debug:
        print(data)

    ents_data = []
    for ent in data.get('Resources', []):
        start_ch = int(ent['@offset'])
        end_ch = int(start_ch + len(ent['@surfaceForm']))
        ent_kb_id = ent['@URI']
        # TODO look at '@types' and choose most relevant?
        span = doc.char_span(start_ch, end_ch, 'DBPEDIA_ENT', ent_kb_id)
        span._.dbpedia_raw_result = ent
        ents_data.append(span)
    
    # try to add results to doc.ents
    try:
        doc.ents = list(doc.ents) + ents_data
        if debug:
            print('the entities are in doc.ents')
    except Exception as e:
        if debug:
            print(e)
        if overwrite_ents:
            # overwrite ok
            doc.spans['ents_original'] = doc.ents
            doc.ents = ents_data
            if debug:
                print('doc.ents has been overwritten. The original entities are in doc.spans["ents_original"]')
        else:
            # don't overwrite
            if debug:
                print('doc.ents not overwritten. You can find the dbpedia ents in doc.spans["dbpedia_ents"]')
    # doc.spans['dbpedia_raw'] = data
    doc.spans['dbpedia_ents'] = ents_data
    return doc
