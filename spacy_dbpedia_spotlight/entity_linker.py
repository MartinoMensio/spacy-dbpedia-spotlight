import spacy
import requests

from spacy.tokens import Span

supported_languages = ['en', 'de', 'es', 'fr', 'it', 'nl', 'pt', 'ru']

class DbpediaLinker(object):
    base_url = 'http://api.dbpedia-spotlight.org/'

    def __init__(self, language_code, nlp=None):
        if language_code not in supported_languages:
            raise ValueError(f'Linker not available in {language_code}. Choose one of {supported_languages}')
        self.language_code = language_code

        if not nlp:
            nlp = spacy.blank(language_code)
        
        if 'ner' not in nlp.pipe_names:
            ner = nlp.create_pipe('ner')
            nlp.add_pipe(ner)
            nlp.begin_training()
        
        nlp.entity.add_label('DBPEDIA_ENT')

        def annotate_dbpedia_spotlight(doc):
            self._annotate_dbpedia_spotlight(doc)
            return doc
        
        nlp.add_pipe(annotate_dbpedia_spotlight)
        self.nlp = nlp


    def _annotate_dbpedia_spotlight(self, doc, debug=False):

        response = requests.get(f'{self.base_url}{self.language_code}/annotate', headers={'accept': 'application/json'}, params={'text': doc.text})
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
            ents_data.append(span)
        
        doc.ents = list(doc.ents) + ents_data
        return doc
