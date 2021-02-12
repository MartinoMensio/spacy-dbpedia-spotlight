# Spacy DBpedia Spotlight

This package acts as a Entity Recogniser and Linker using [DBpedia Spotlight](https://www.dbpedia-spotlight.org/), annotating SpaCy's Spans and adding them to the entities annotations.

It can be added to an existing spaCy [Language](https://spacy.io/api/language) object, or create a new one from an empty pipeline.


The results are put in `doc.ents`, overwriting existing entities in case of conflict depending on the `overwrite_ents` parameter.
The spans produced have the following properties:

- `span.label_ = 'DBPEDIA_ENT'`
- `span.ent_kb_id_` containing the URI of the linked entity
- `span._.dbpedia_raw_result` containing the raw json for the entity from DBpedia spotlight (`@URI`, `@support`, `@types`, `@surfaceForm`, `@offset`, `@similarityScore`, `@percentageOfSecondRank`)

## Usage

## Installation

This package works with SpaCy v3

With pip: `pip install spacy-dbpedia-spotlight`
From GitHub (after clone): `pip install .`

### Instantiating the pipeline component

With a blank new language

```python
import spacy_dbpedia_spotlight
# a new blank model will be created, with the language code provided in the parameter
nlp = spacy_dbpedia_spotlight.create('en')
# in this case, the pipeline will be only contain the EntityLinker
print(nlp.pipe_names)
# ['dbpedia_spotlight']
```

On top of an existing nlp object (added as last pipeline stage by default)

```python
import spacy
# this is any existing model
nlp = spacy.load('en_core_web_lg')
# add the pipeline stage
nlp.add_pipe('dbpedia_spotlight')
# see the pipeline, the added stage is at the end
print(nlp.pipe_names)
# ['tok2vec', 'tagger', 'parser', 'ner', 'attribute_ruler', 'lemmatizer', 'dbpedia_spotlight']
```

The pipeline stage can be added at any point of an existing pipeline (using the arguments `before`, `after`, `first` or `last`)

```python
import spacy
# this is any existing model
nlp = spacy.load('en_core_web_lg')
# add the pipeline stage
nlp.add_pipe('dbpedia_spotlight', first=True)
# see the pipeline, the added stage is at the beginning
print(nlp.pipe_names)
# ['dbpedia_spotlight', 'tok2vec', 'tagger', 'parser', 'ner', 'attribute_ruler', 'lemmatizer']
```
### Configuration parameters

This component can be used with the following parameters:

- `language_code`: to explicitly use a specific dbpedia language, because on default the value from `nlp.meta['lang']` is used
- `dbpedia_rest_endpoint`: to use something different from `http://api.dbpedia-spotlight.org/{LANGUAGE_CODE}`, for example when using a local instance of DBpedia Spotlight. Don't set it if the default location is ok
- `overwrite_ents`: to control how the overwriting of `doc.ents` is performed, because other components may have already written there (e.g., the `en_core_web_lg` model has a `ner` pipeline component which already sets some entities). The component tries to add the new ones from DBpedia, which can be successful if the entities do not overlap in terms of tokens. The cases are the following:
  - no tokens overlap between the pre-exisiting `doc.ents` and the new entities: in this case `doc.ents` will contain both the previous entities and the new entities
  - some tokens overlap and `overwrite_ents=True`: the previous value of `doc.ents` is saved in `doc.spans['ents_original']` and only the dbpedia entities will be saved in `doc.ents`
  - some tokens overlap and `overwrite_ents=False`: the previous value of `doc.ents` is left untouched, and the dbpedia entiities can be found in `doc.spans['dbpedia_ents']`

The configuration dict needs to be passed when instantiating the pipeline component

```python
import spacy
nlp = spacy.load('en_core_web_lg')
# instantiate Spanish EntityLinker on the English model
nlp.add_pipe('dbpedia_spotlight', config={'language_code': 'es'})
```

### Using the model

After having instantiated the component, you can use the spaCy API as usual

```python
doc = nlp('The president of USA is calling Boris Johnson to decide what to do about coronavirus')
print("Entities", [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents])
```

Output example:
```text
Entities [('USA', 'DBPEDIA_ENT', 'http://dbpedia.org/resource/United_States'), ('Boris Johnson', 'DBPEDIA_ENT', 'http://dbpedia.org/resource/Boris_Johnson'), ('coronavirus', 'DBPEDIA_ENT', 'http://dbpedia.org/resource/Coronavirus')]
```


## Known issues
### DBpedia spotlight is denying my requests

After a few requests to DBpedia spotlight, the public web service will reply with some bad HTTP codes.

The solution is to use a local DBpedia instance (TODO documentation will come soon).
