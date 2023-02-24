import spacy

def test_basic_load():
    nlp = spacy.blank("en")
    p = nlp.add_pipe('dbpedia_spotlight')
    assert p != None
    assert 'dbpedia_spotlight' in nlp.pipe_names

def test_load_vector():
    nlp = spacy.blank("en")
    p = nlp.add_pipe('dbpedia_spotlight')
    assert p != None
    assert 'dbpedia_spotlight' in nlp.pipe_names
    doc = nlp("Google LLC is an American multinational technology company.")
    ents = doc.ents
    assert ents is not None
    assert len(ents) > 0