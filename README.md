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

The pipeline stage can be added at any point of an existing pipeline (using the arguments `before`, `after`, `first` or `last`).
A specific positioning can be useful if you are using the output of one stage as input to another stage.

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

### Using the model

After having instantiated the component, you can use the spaCy API as usual, and you will get the DBPedia spotlight entities

```python
import spacy
nlp = spacy.blank('en')
nlp.add_pipe('dbpedia_spotlight')

doc = nlp('Google LLC is an American multinational technology company.')
print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents])
```

Output example:
```text
[('Google LLC', 'http://dbpedia.org/resource/Google', '0.9999999999999005'), ('American', 'http://dbpedia.org/resource/United_States', '0.9861264878996763')]
```

## Configuration parameters

This component can be used with several parameters, which control the usage of the [DBpedia Spotlight API](https://www.dbpedia-spotlight.org/api) and the behaviour of this bridge library.

All the configuration options described in detail below can be passed when instantiating the pipeline component with the `config` optional parameter.

```python
import spacy
nlp = spacy.load('en_core_web_lg')
# instantiate Italian EntityLinker on the English model
nlp.add_pipe('dbpedia_spotlight', config={'language_code': 'it'})
```

Or, in alternative, the values can be changed also after the pipeline stage creation. In this case, you can modify them directly in the pipeline stage object

```python
import spacy
text = 'And the boy said "voglio andare negli Stati Uniti"'
nlp = spacy.blank('en')
# at the beginning we want to use default parameters (in this case the english API endpoint is used)
nlp.add_pipe('dbpedia_spotlight')
doc = nlp(text)
# no entities found
print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents])


# we want to change the `language_code`
nlp.get_pipe('dbpedia_spotlight').language_code = 'it'
# you need to re-create the document, because the entities are computed at document creation
doc = nlp(text)
# now we have one entity
print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents])

```

### Using DBpedia in a specific language

`language_code` controls the language of DBpedia Spotlight. The API is located at `https://api.dbpedia-spotlight.org/{language_code}`.
By default the language to be used is derived from the `nlp.meta['lang']`. So if you are using a French pipeline, the default is `fr`.

When you pass a value in the configuration, this will override the default value. If you are using a pipeline in a language not supported by DBPedia Spotlight, you will be required to set this configuration option.

To support a language, it needs to be supported both by spaCy and by DBpedia-spotlight. This table shows the two requirements and the final result:

| language | code | spaCy supported |DBpedia spotlight supported| supported |
|--- | :-: | :-: | :-: | :-: |
| Catalan | `ca` | ✅ | ✅ | ✅ |
| Chinese | `zh`| ✅ | ❌ | ❌ |
| Croatian | `hr`| ✅ | ❌ | ❌ |
| Danish | `da`| ✅ | ✅ | ✅ |
| Dutch | `nl`| ✅ | ✅ | ✅ |
| English | `en`| ✅ | ✅ | ✅ |
| Finnish | `fi`| ✅ | ✅ | ✅ |
| French | `fr`| ✅ | ✅ | ✅ |
| German | `de`| ✅ | ✅ | ✅ |
| Greek | `el`| ✅ | ❌ | ❌ |
| Hungarian | `hu`| ✅ | ✅ | ✅ |
| Italian | `it`| ✅ | ✅ | ✅ |
| Japanese | `ja`| ✅ | ❌ | ❌ |
| Korean | `ko`| ✅ | ❌ | ❌ |
| Lithuanian | `lt`| ✅ | ❌ | ❌ |
| Macedonian | `mk`| ✅ | ❌ | ❌ |
| Norwegian Bokmål | `nb`| ✅ | ❌ | ❌ |
| Polish | `pl`| ✅ | ❌ | ❌ |
| Portuguese | `pt`| ✅ | ✅ | ✅ |
| Romanian | `ro`| ✅ | ✅ | ✅ |
| Russian | `ru`| ✅ | ✅ | ✅ |
| Spanish | `es`| ✅ | ✅ | ✅ |
| Swedish | `sv`| ✅ | ✅ | ✅ |
| Turkish | `tr`| ✅ | ✅ | ✅ |
| Ukrainian | `uk`| ✅ | ❌ | ❌ |
| Multi-language | `xx`| ✅ | ❌ | ❌ |

Example:

```python
import spacy
# Greek not supported by spotlight
nlp = spacy.blank('el')
# so let's try to use the English endpoint on the greek language
nlp.add_pipe('dbpedia_spotlight', config={'language_code': 'en'})
```

### Using another server

If you don't want to use `api.dbpedia-spotlight.org` as server (for example because you have your local DBPedia Spotlight deployed), you can use the `dbpedia_rest_endpoint` parameter to point to a custom server.

The default value is `http://api.dbpedia-spotlight.org/{language_code}`

By setting this parameter, the `language_code` parameter will be ignored. You are providing the URL of the endpoint to be used (excluding the last part which is `/annotate` or `/spot` or `/candidates`).

Example:
```python
import spacy
nlp = spacy.blank('en')
# Use your endpoint: don't put any trailing slashes, and don't include the /annotate path
nlp.add_pipe('dbpedia_spotlight', config={'dbpedia_rest_endpoint': 'http://localhost:2222/rest'})
```

#### Changing between `annotate` / `spot` and `candidates`

The parameter `process` conrols which specific type of processing is done. The possible values are:
- `annotate`: A 4(four) step process - Spotting, Candidate Mapping, Disambiguation and Linking / Stats - for linking unstructured information sources
- `spot`: A 1(one) step process - Spotting - for linking unstructured information sources
- `candidates`: A 2(two) step process - Spotting, Candidate Mapping - for linking unstructured information sources

The default value is `annotate`. This parameter works both for the default DBpedia endpoint and for custom ones.

Example:
```python
import spacy
nlp = spacy.blank('en')
# run the candidates process
nlp.add_pipe('dbpedia_spotlight', config={'process': 'candidates'})
doc = nlp('Google LLC is an American multinational technology company.')
print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['resource']['@contextualScore']) for ent in doc.ents])
```

### Setting other parameters of the DBpedia REST API

As can be seen in the [documentation of the DBpedia REST API](https://www.dbpedia-spotlight.org/api), there are 5 parameters (`confidence`, `support`, `types`, `sparql` and `policy`) which can be used to filter the results. You can use them through the `config` object:

- `confidence`: confidence score for disambiguation / linking
- `support`: how prominent is this entity in Lucene Model, i.e. number of inlinks in Wikipedia
- `types`: types filter (Eg.DBpedia:Place)
- `sparql`: SPARQL filtering
- `policy`: (whitelist) select all entities that have the same type; (blacklist) - select all entities that have not the same type.

Example:
```python
import spacy
nlp = spacy.blank('en')
text ='Google LLC is an American multinational technology company.'
# get only the places (DBpedia:Place) with confidence above 0.75
nlp.add_pipe('dbpedia_spotlight', config={'types': 'DBpedia:Place', 'confidence': 0.75})
doc = nlp(text)
# this will output [('American', 'http://dbpedia.org/resource/United_States', '0.9861264878996763')]
print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents])

# now only get the organisations
nlp.get_pipe('dbpedia_spotlight').types = 'DBpedia:Organisation'
# re-create the document
doc = nlp(text)
# this will output [('Google LLC', 'http://dbpedia.org/resource/Google', '0.9999999999999005')]
print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents])

# now get all together
nlp.get_pipe('dbpedia_spotlight').types = None
# re-create the document
doc = nlp(text)
# this will output both Google and American
print([(ent.text, ent.kb_id_, ent._.dbpedia_raw_result['@similarityScore']) for ent in doc.ents])
```



### Controlling where entities are saved and if they are overwritten

This pipeline stage can be loaded on existing language models which already have Entity recognition/linking and can also be loaded on models that don't have it. For this reason you may want to control the behaviour of writing to `doc.ents` and decide where the results of DBpedia Spotlight are saved.

By default, this pipeline stage writes to a dedicated [span group](https://spacy.io/api/spangroup) which can be accessed with `doc.spans['dbpedia_spotlight']`, where the name of the span group is `dbpedia_spotlight`. You can change the name by using the `span_group` parameter.

By default, the `doc.ents` are overwritten with the new results. The parameter `overwrite_ents` can be used to control how the overwriting of `doc.ents` is performed, because other components may have already written there (e.g., the `en_core_web_lg` model has a `ner` pipeline component which already sets some entities). The component tries to add the new ones from DBpedia, which can be successful if the entities do not overlap in terms of tokens. The cases are the following:
  - no tokens overlap between the pre-exisiting `doc.ents` and the new entities: in this case `doc.ents` will contain both the previous entities and the new entities
  - some tokens overlap and `overwrite_ents=True`: the previous value of `doc.ents` is saved in `doc.spans['ents_original']` and only the dbpedia entities will be saved in `doc.ents`
  - some tokens overlap and `overwrite_ents=False`: the previous value of `doc.ents` is left untouched, and the dbpedia entities can be found in `doc.spans['dbpedia_spotlight']`


### Set how to behave in case of HTTPError from the API

In case there is a HTTPError from the REST API, you can use the parameter `raise_http_errors` to select which behaviour to have:

- `False`: will ignore the errors (they will be logged and visible on STDOUT).
- `True`: the exception will be rethrown and will stop your processing. This is the default.

```python
import spacy
nlp = spacy.blank('en')
nlp.add_pipe('dbpedia_spotlight')
# this time you will get a HTTPError: 400 Client Error
doc = nlp('')

# now change it to False
nlp.get_pipe('dbpedia_spotlight').raise_http_errors = False
# this will generate a warning, but will not break your processing (e.g. in a loop)
doc = nlp('')
```

## Using this when training your pipeline

If you are [training a pipeline](https://spacy.io/usage/training#quickstart) and you want to include the component in it, you can add to your `config.cfg`:

```text
[nlp]
lang = "en"
pipeline = ["dbpedia"]

[components]

[components.dbpedia]
factory = "dbpedia_spotlight"
overwrite_ents = false
debug = false
```



## Common issues
### DBpedia refuses to answer huge quantities of requests

After a few requests to DBpedia spotlight, the public web service will reply with some bad HTTP codes.

The solution is to use a local DBpedia instance. The instructions below are with Docker or without it.

#### Deploy with Docker

```bash
# pull the official image
docker pull dbpedia/dbpedia-spotlight
# create a volume for persistently saving the language models
docker volume create spotlight-models
# start the container (here assuming we want the en model)
docker run -ti \
 --restart unless-stopped \
 --name dbpedia-spotlight.en \
 --mount source=spotlight-models,target=/opt/spotlight \
 -p 2222:80 \
 dbpedia/dbpedia-spotlight \
 spotlight.sh en
```

#### Withouth Docker

```bash
# download main jar
wget https://sourceforge.net/projects/dbpedia-spotlight/files/spotlight/dbpedia-spotlight-1.0.0.jar
# download latest model (assuming en model)
wget -O en.tar.gz http://downloads.dbpedia.org/repo/dbpedia/spotlight/spotlight-model/2020.11.18/spotlight-model_lang%3den.tar.gz
# extract model
tar xzf en.tar.gz
# run server
java -jar dbpedia-spotlight-1.0.0.jar en http://localhost:2222/rest
```

#### Use the local server

First of all, make sure that the local server is working.

```bash
curl http://localhost:2222/rest/annotate \
 --data-urlencode "text=President Obama called Wednesday on Congress to extend a tax break for students included in last year's economic stimulus package, arguing that the policy provides more generous assistance." \
 --data "confidence=0.35" \
 -H "Accept: text/turtle"
```

Then in Python you can configure the endpoint in the following way

```python
import spacy
nlp = spacy.load('en_core_web_lg')
# Use your endpoint: don't put any trailing slashes, and don't include the /annotate path
nlp.add_pipe('dbpedia_spotlight', config={'dbpedia_rest_endpoint': 'http://localhost:2222/rest'})
```

## Utils

```bash
pip install -r requirements.txt
# test
pytest test.py
# build the archive
python setup.py sdist
# upload to pypi
twine upload dist/spacy_dbpedia_spotlight-0.2.5.tar.gz
```