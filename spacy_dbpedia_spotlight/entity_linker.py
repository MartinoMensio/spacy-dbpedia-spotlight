import spacy
import requests
from spacy.language import Language

from spacy.tokens import Span, Doc

# span extension attribute for raw json
Span.set_extension("dbpedia_raw_result", default=None)
Doc.set_extension("dbpedia_raw_result", default=None)

@Language.factory('dbpedia_spotlight', default_config={
    'language_code': None,
    'dbpedia_rest_endpoint': None,
    'process': 'annotate',
    'confidence': None,
    'support': None,
    'types': None,
    'sparql': None,
    'policy': None,
    'span_group': 'dbpedia_spotlight',
    'overwrite_ents': True,
    'debug': False
})
def dbpedia_spotlight_factory(nlp, name, language_code, dbpedia_rest_endpoint, process, confidence, support, types, sparql, policy, span_group, overwrite_ents, debug):
    '''Factory of the pipeline stage `dbpedia_spotlight`.
    Parameters:
    - `language_code`: which language to use for entity linking. Possible values are listed in EntityLinker.supported_languages. If the parameter is left as None, the language code is matched with the nlp object currently used.
    - `dbpedia_rest_endpoint`: this needs to be configured if you want to use a different REST endpoint from the default `EntityLinker.base_url`. Example: `http://localhost:2222/rest` for a localhost server
    - `process`: (REST API path) which of the processes to use from DBpedia Spotlight (see https://www.dbpedia-spotlight.org/api). The value can be 'annotate', 'spot' or 'candidates'
    - `confidence`: (REST API parameter) confidence score for disambiguation / linking
    - `support`: (REST API parameter) how prominent is this entity in Lucene Model, i.e. number of inlinks in Wikipedia
    - `types`: (REST API parameter) types filter (Eg.DBpedia:Place)
    - `sparql`: (REST API parameter) SPARQL filtering
    - `policy`: (REST API parameter) (whitelist) select all entities that have the same type; (blacklist) - select all entities that have not the same type.
    - `span_group`: which span group to write the entities to. By default the value is `dbpedia_spotlight` which writes to `doc.spans['dbpedia_spotlight']`
    - `overwrite_ents`: if set to False, it won't overwrite `doc.ents` in cases of overlapping spans with current entities, and only produce the results in `doc.spans[span_group]. If it is True, it will move the entities from doc.ents into `doc.spans['ents_original']`
    - `debug`: prints several debug information to stdout
    '''
    if debug:
        print('dbpedia_spotlight_factory:', nlp, 'language_code', language_code,
            'dbpedia_rest_endpoint', dbpedia_rest_endpoint, 'process', process, 'confidence', confidence, 'support', support,
            'types', types, 'sparql', sparql, 'policy', policy,
            'overwrite_ents', overwrite_ents)
    # take the language code from the nlp object
    nlp_lang_code = nlp.meta['lang']
    if debug:
        print('nlp.meta["lang"]=', nlp_lang_code)
    # language_code can override the language code from the nlp object
    if not language_code:
        language_code = nlp_lang_code
    return EntityLinker(language_code, dbpedia_rest_endpoint, process, confidence, support, types, sparql, policy, span_group, overwrite_ents, debug)


class EntityLinker(object):
    '''This class manages the querying of DBpedia and attaches the found entities to the document'''
    # default location of the service
    base_url = 'https://api.dbpedia-spotlight.org'
    # list of supported languages
    supported_languages = ['en', 'de', 'es', 'fr', 'it', 'nl', 'pt', 'ru']
    # list of supported processes
    supported_processes = ['annotate', 'spot', 'candidates']

    def __init__(self, language_code='en', dbpedia_rest_endpoint=None, process='annotate', confidence=None, support=None,
        types=None, sparql=None, policy=None, span_group='dbpedia_spotlight', overwrite_ents=True, debug=False):
        # constructor of the pipeline stage
        if language_code not in self.supported_languages:
            raise ValueError(f'Linker not available in {language_code}. Choose one of {self.supported_languages}')
        self.language_code = language_code
        if process not in self.supported_processes:
            raise ValueError(f'The process {process} is not supported. Choose one of {self.supported_processes}')
        self.process = process
        self.confidence = confidence
        self.support = support
        self.types = types
        self.sparql = sparql
        self.policy = policy
        self.span_group = span_group
        self.overwrite_ents = overwrite_ents
        self.debug = debug
        self.dbpedia_rest_endpoint = dbpedia_rest_endpoint


    def __call__(self, doc):
        # called in the pipeline
        if self.dbpedia_rest_endpoint:
            # override the default endpoint, e.g., 'http://localhost:2222/rest'
            endpoint = self.dbpedia_rest_endpoint
            if self.debug:
                print('api_endpoint has been manually set to', endpoint)
        else:
            # use the default endpoint for the language selected
            endpoint = f'{self.base_url}/{self.language_code}'
            if self.debug:
                print('api_endpoint has been built as', endpoint)


        params = {'text': doc.text}
        if self.confidence:
            params['confidence'] = self.confidence
        if self.support:
            params['support'] = self.support
        if self.types:
            params['types'] = self.types
        if self.sparql:
            params['sparql'] = self.sparql
        if self.policy:
            params['policy'] = self.policy


        # TODO: application/ld+json would be more detailed? https://github.com/digitalbazaar/pyld
        response = requests.post(f'{endpoint}/{self.process}', headers={'accept': 'application/json'}, data=params)
        response.raise_for_status()
        data = response.json()
        if self.debug:
            print(data)

        doc._.dbpedia_raw_result = data

        ents_data = []
        # fields have different names depending on the process
        text_key = '@name'
        get_ents_list = lambda json: json.get('annotation', {}).get('surfaceForm', [])
        get_uri = lambda el: None
        # get_offset
        if self.process == 'annotate':
            get_ents_list = lambda json: json.get('Resources', [])
            text_key = '@surfaceForm'
            get_uri = lambda el: el['@URI']
        elif self.process == 'spot':
            pass
        elif self.process == 'candidates':
            get_uri = lambda el: f"http://dbpedia.org/resource/{el['resource']['@uri']}"
            
            
        for ent in get_ents_list(data):
            if self.debug:
                print(ent)
            start_ch = int(ent['@offset'])
            end_ch = int(start_ch + len(ent[text_key]))
            ent_kb_id = get_uri(ent)
            # TODO look at '@types' and choose most relevant?
            if ent_kb_id:
                span = doc.char_span(start_ch, end_ch, 'DBPEDIA_ENT', ent_kb_id)
            else:
                span = doc.char_span(start_ch, end_ch, 'DBPEDIA_ENT')
            if not span:
                # something strange like "something@bbc.co.uk" where the match is only part of a SpaCy token
                # 1. find the token to split
                print(start_ch, end_ch, ent)
                # tokens also wider than start_ch, end_ch
                tokens_to_split = [t for t in doc if t.idx >= start_ch or t.idx+len(t) <=end_ch]
                span = doc.char_span(min(t.idx for t in tokens_to_split), max(t.idx + len(t) for t in tokens_to_split))
                # with doc.retokenize() as retokenizer:
                #     for t in tokens_to_split:
                #         retokenizer.split(t, ['a', 't'], [t.head, t.head])
                # raise ValueError()
            span._.dbpedia_raw_result = ent
            ents_data.append(span)
        
        # try to add results to doc.ents
        try:
            doc.ents = list(doc.ents) + ents_data
            if self.debug:
                print('the entities are in doc.ents')
        except Exception as e:
            if self.debug:
                print(e)
            if self.overwrite_ents:
                # overwrite ok
                doc.spans['ents_original'] = doc.ents
                doc.ents = ents_data
                if self.debug:
                    print('doc.ents has been overwritten. The original entities are in doc.spans["ents_original"]')
            else:
                # don't overwrite
                if self.debug:
                    print('doc.ents not overwritten. You can find the dbpedia ents in doc.spans["dbpedia_ents"]')
        # doc.spans['dbpedia_raw'] = data
        doc.spans[self.span_group] = ents_data
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

