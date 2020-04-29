# Spacy DBpedia Spotlight

This package acts as a Entity Recogniser and Linker using [DBpedia Spotlight](https://www.dbpedia-spotlight.org/), annotating SpaCy's Spans and adding them to the entities annotations.

It can create a new [Language](https://spacy.io/api/language) object or be added on an existing one.

It uses:

- `DBPEDIA_ENT` as `ent_type`
- the entity URI as `ent_kb_id`

## Usage

Use on a blank new language

```python
import spacy_dbpedia_spotlight

# here a new blank model will be created
nlp = spacy_dbpedia_spotlight.load('en')
doc = nlp('The president of USA is calling Boris Johnson to decide what to do about coronavirus')
print("Entities", [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents])
```

Or use on top of an existing nlp object (added as last pipeline stage)

```python
import spacy
import spacy_dbpedia_spotlight

# use your model
nlp = spacy.load('en_core_web_lg')
# pass nlp as parameter
spacy_dbpedia_spotlight.load('en', nlp)
doc = nlp('The president of USA is calling Boris Johnson to decide what to do about coronavirus')
print("Entities", [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents])
```

Or if you want to just get the pipeline stage and place it where you want

```python
import spacy

# any nlp you want
nlp = spacy.blank('en')
# create the pipe component, the dict argument is optional
entity_annotator = nlp.create_pipe('annotate_dbpedia_spotlight', {'language_code':'it'})
# add on your fancy pipeline with options like `first`
nlp.add_pipe(entity_annotator, first=True)
```

Output example:
```text
Entities [('USA', 'DBPEDIA_ENT', 'http://dbpedia.org/resource/United_States'), ('Boris Johnson', 'DBPEDIA_ENT', 'http://dbpedia.org/resource/Boris_Johnson'), ('coronavirus', 'DBPEDIA_ENT', 'http://dbpedia.org/resource/Coronavirus')]
```