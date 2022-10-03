import concurrent.futures
import sys

import requests
import spacy
from multiprocessing.pool import ThreadPool
from loguru import logger
from requests import HTTPError
from spacy import util
from spacy.language import Language
from spacy.tokens import Doc, Span

DBPEDIA_SPOTLIGHT_DEFAULT_ENDPOINT = 'https://api.dbpedia-spotlight.org'

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
    'raise_http_errors': True,
    'debug': False
})
def dbpedia_spotlight_factory(nlp, name, language_code, dbpedia_rest_endpoint, process, confidence, support, types, sparql, policy, span_group, overwrite_ents, raise_http_errors, debug):
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
    - `raise_http_errors`: if set to True, it will raise the HTTPErrors generated by the dbpedia REST API. If False instead, HTTPErrors will be ignored. Default to True.
    - `debug`: prints several debug information to stdout
    '''
    logger.remove()
    if debug:
        logger.add(sys.stdout, level="DEBUG")
    else:
        logger.add(sys.stdout, level="INFO")
    logger.debug(f'dbpedia_spotlight_factory: {nlp}, language_code: {language_code}, dbpedia_rest_endpoint: {dbpedia_rest_endpoint}, '
                 f'process: {process}, confidence: {confidence}, support: {support}, types: {types}, '
                 f'sparql: {sparql}, policy: {policy}, overwrite_ents: {overwrite_ents}')
    # take the language code from the nlp object
    nlp_lang_code = nlp.meta['lang']
    logger.debug(f'nlp.meta["lang"]={nlp_lang_code}')
    # language_code can override the language code from the nlp object
    if not language_code:
        language_code = nlp_lang_code
    return EntityLinker(language_code, dbpedia_rest_endpoint, process, confidence, support, types, sparql, policy, span_group, overwrite_ents, raise_http_errors, debug)


class EntityLinker(object):
    '''This class manages the querying of DBpedia and attaches the found entities to the document'''
    # default location of the service
    base_url = DBPEDIA_SPOTLIGHT_DEFAULT_ENDPOINT
    # list of supported languages
    supported_languages = ['en', 'de', 'es', 'fr', 'it', 'nl', 'pt', 'ru']
    # list of supported processes
    supported_processes = ['annotate', 'spot', 'candidates']

    def __init__(self, language_code='en', dbpedia_rest_endpoint=None, process='annotate', confidence=None, support=None,
                 types=None, sparql=None, policy=None, span_group='dbpedia_spotlight', overwrite_ents=True, raise_http_errors=True, debug=False):
        # constructor of the pipeline stage
        if dbpedia_rest_endpoint is None and language_code not in self.supported_languages:
            raise ValueError(
                f'Linker not available in {language_code}. Choose one of {self.supported_languages}')
        self.language_code = language_code
        if process not in self.supported_processes:
            raise ValueError(
                f'The process {process} is not supported. Choose one of {self.supported_processes}')
        self.process = process
        self.confidence = confidence
        self.support = support
        self.types = types
        self.sparql = sparql
        self.policy = policy
        self.span_group = span_group
        self.overwrite_ents = overwrite_ents
        self.raise_http_errors = raise_http_errors
        self.debug = debug
        self.dbpedia_rest_endpoint = dbpedia_rest_endpoint

    def process_single_doc_after_call(self, doc: Doc, data) -> Doc:
        """
        Adds the entities from the response data to the doc.ents.
        
        :param doc: The document to process
        :type doc: Doc
        :param data: The JSON data from the server
        :return: The return value is a Doc object.
        """

        if not data:
            logger.log('DEBUG', 'No data returned from DBpedia Spotlight')
            return doc
        
        doc._.dbpedia_raw_result = data

        ents_data = []
        # fields have different names depending on the process
        text_key = '@name'
        def get_uri(el): return None
        # get_offset
        if self.process == 'annotate':
            def get_ents_list(json): return json.get('Resources', [])
            text_key = '@surfaceForm'
            def get_uri(el): return el['@URI']
        elif self.process == 'spot':
            def get_ents_list(json): return json.get(
                'annotation', {}).get('surfaceForm', [])
        elif self.process == 'candidates':
            def get_ents_list(json):
                surface_form = json.get(
                    'annotation', {}).get('surfaceForm', [])
                if isinstance(surface_form, dict):
                    # if only one candidate
                    surface_form = [surface_form]
                return surface_form

            def get_uri(
                el): return f"http://dbpedia.org/resource/{el['resource']['@uri']}"

        for ent in get_ents_list(data):
            logger.debug(ent)
            start_ch = int(ent['@offset'])
            end_ch = int(start_ch + len(ent[text_key]))
            ent_kb_id = get_uri(ent)
            # TODO look at '@types' and choose most relevant?
            if ent_kb_id:
                span = doc.char_span(
                    start_ch, end_ch, 'DBPEDIA_ENT', ent_kb_id)
            else:
                span = doc.char_span(start_ch, end_ch, 'DBPEDIA_ENT')
            if not span:
                # something strange like "something@bbc.co.uk" where the match is only part of a SpaCy token
                # 1. find the token to split
                logger.debug(f'{start_ch}, {end_ch}, {ent}')
                # tokens also wider than start_ch, end_ch
                tokens_to_split = [t for t in doc if t.idx >=
                                   start_ch or t.idx+len(t) <= end_ch]
                span = doc.char_span(min(t.idx for t in tokens_to_split), max(
                    t.idx + len(t) for t in tokens_to_split))
                # with doc.retokenize() as retokenizer:
                #     for t in tokens_to_split:
                #         retokenizer.split(t, ['a', 't'], [t.head, t.head])
                # raise ValueError()
            span._.dbpedia_raw_result = ent
            ents_data.append(span)

        # try to add results to doc.ents
        try:
            doc.ents = list(doc.ents) + ents_data
            logger.debug('The entities are in doc.ents')
        except Exception as e:
            logger.debug(str(e))
            if self.overwrite_ents:
                # overwrite ok
                doc.spans['ents_original'] = doc.ents
                try:
                    doc.ents = ents_data
                except ValueError:  # if there are overlapping spans in the dbpedia_spotlight entities
                    doc.ents = spacy.util.filter_spans(ents_data)
                logger.debug(
                    'doc.ents has been overwritten. The original entities are in doc.spans["ents_original"]')
            else:
                # don't overwrite
                logger.debug(
                    'doc.ents not overwritten. You can find the dbpedia ents in doc.spans["dbpedia_spotlight"]')
        # doc.spans['dbpedia_raw'] = data
        doc.spans[self.span_group] = ents_data
        return doc

    def make_request(self, doc: Doc):
        """
        It takes a Doc object as input, and returns a response object from the DBpedia Spotlight API
        
        :param doc: the text to be annotated
        :type doc: Doc
        :return: The response as a requests.Response instance.
        """
        if self.dbpedia_rest_endpoint:
            # override the default endpoint, e.g., 'http://localhost:2222/rest'
            endpoint = self.dbpedia_rest_endpoint
            logger.debug(f'api_endpoint has been manually set to {endpoint}')
        else:
            # use the default endpoint for the language selected
            endpoint = f'{self.base_url}/{self.language_code}'
            logger.debug(f'api_endpoint has been built as {endpoint}')

        params = {'text': doc.text}
        if self.confidence != None:
            params['confidence'] = self.confidence
        if self.support != None:
            params['support'] = self.support
        if self.types != None:
            params['types'] = self.types
        if self.sparql != None:
            params['sparql'] = self.sparql
        if self.policy != None:
            params['policy'] = self.policy

        # TODO: application/ld+json would be more detailed? https://github.com/digitalbazaar/pyld
        return requests.post(
            f'{endpoint}/{self.process}', headers={'accept': 'application/json'}, data=params)

    def get_remote_response(self, doc: Doc):
        """
        Wraps a remote call to the DBpedia Spotlight API, handles the possible errors and returns the JSON response:
        - calls make_request to perform the actual request
        - hecks the response object and acts accordingly to the status code and the decided behaviour (self.raise_http_errors)
        - returns the JSON response
        
        :param doc: the document to be annotated
        :type doc: Doc
        :return: the JSON response or None in case of error and self.raise_http_errors is False
        """
        try:
            response = self.make_request(doc)
            response.raise_for_status()
        except HTTPError as e:
            # due to too many requests to the endpoint - this happens sometimes with the default public endpoint
            logger.warning(
                f"Bad response from server {self.endpoint}, probably too many requests. Consider using your own endpoint. Document not updated.")
            logger.debug(str(e))
            if self.raise_http_errors:
                raise e
            return None
        except Exception as e:  # other erros
            logger.error(
                f"Endpoint {self.endpoint} unreachable, please check your connection. Document not updated.")
            logger.debug(str(e))
            return None

        data = response.json()
        logger.debug(f'Received data: {data}')
        return data

    def __call__(self, doc):
        """
        The function makes a request to the endpoint, and if the request is successful, it returns the
        document. If the request is unsuccessful, it returns the document without updating it
        
        :param doc: the document to be processed
        :return: The document is being returned.
        """

        data = self.get_remote_response(doc)
        self.process_single_doc_after_call(doc, data)
        return doc

    def pipe(self, stream, batch_size=128):
        """
        It takes a stream of documents, and for each batch of documents, it makes a request to the API
        for each document in the batch, and then yields the processed results of each document
        
        :param stream: the stream of documents to be processed
        :param batch_size: The number of documents to send to the API in a single request, defaults to
        128 (optional)
        """
        for docs in util.minibatch(stream, size=batch_size):
            with ThreadPool(batch_size) as pool:
                print('batch_size', batch_size)
                # using pool.imap to preserve order and avoid blocking
                for data, doc in zip(pool.imap(self.get_remote_response, docs), docs):
                    self.process_single_doc_after_call(doc, data)
                    yield doc


def create(language_code, nlp=None):
    '''Creates an instance of a Language with the DBpedia EntityLinker pipeline stage.
    If the parameter `nlp` is None, it will return a blank language with the EntityLinker.
    If the parameter `nlp` is an existing Language, it simply adds the EntityLinker pipeline stage (equivalent to `nlp.add`)
    '''
    if not nlp:
        nlp = spacy.blank(language_code)
    nlp.add_pipe('dbpedia_spotlight')
    return nlp
