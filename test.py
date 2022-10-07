import spacy
import numpy as np
import spacy_dbpedia_spotlight

short_text = 'Google LLC is an American multinational technology company.'
strange_text = 'Today I emailed something@bbc.co.uk and they didn\'t reply yet! I will contact Boris Johnson'
long_text = '''
US President Joe Biden has issued an order targeting homemade guns, known as "ghost guns" because they are unregistered and untraceable.

"Gun violence in this country is an epidemic, and it's an international embarrassment," he said on Thursday.

The president is enacting new measures through an executive order, meaning he does not need approval from Congress.

It includes efforts to set rules for certain guns, bolster background checks and support local violence prevention.

America's gun culture in charts
US shooting suspect identified as ex-NFL player
However, the president will have an uphill task. The right to bear arms is protected by the Second Amendment to the US Constitution and many people see gun control laws as infringing on this constitutional right.

Hours after the president's address, a gunman killed one person and injured five others at a cabinet-making shop in Bryan, Texas. A state trooper was also shot and injured while taking the suspect into custody.

On Wednesday, five people, including two young children, killed in South Carolina. The suspect has been named as former NFL player Phillip Adams.

This followed two mass shootings in March, which left a total of 18 people dead - one in Boulder, Colorado and the other in Atlanta, Georgia.

What can Mr Biden do?
Speaking in the White House Rose Garden on Thursday, Mr Biden said 106 people are killed every day by guns in the country.

"This is an epidemic for God's sake. And it has to stop," he continued.

He also offered condolences to the family killed in South Carolina.

Mr Biden's executive order gives the Justice Department 30 days to propose a rule that will help reduce the number of so-called "ghost guns".

These guns are self-assembled, which means they do not contain a serial number and cannot be traced. Background checks are also not required to purchase the assembly kits.

"Anyone from a criminal to a terrorist can buy this kit and, in as little as 30 minutes, put together a weapon," Mr Biden said.

Experts say that these homemade guns are increasingly being used in crimes. Over 40% of guns being seized in Los Angeles are ghost guns, according to federal firearms officials.

Mr Biden is also giving the Justice Department two months to come up with a rule on stabilising braces for pistols. Under the rule, a pistol used with a stabilising brace would be classified as a short-barrelled rifle, which requires much more stringent background checks under the National Firearms Act.

The Justice Department has also been asked to draft a "red flag law" which states can then use to create their own legislation. These laws authorise the courts and law enforcement to remove guns from people thought to be a risk to the community.

Should US police be able to seize guns
US gun sales have hit record high - why?
Getting further gun measures through Congress would be difficult. The US Senate is currently split 50-50 between Democrats and Republicans, with Vice-President Harris holding the deciding vote.

However, current Senate rules mean that in practice, 60 votes are needed to pass legislation, meaning some Republican support is required. Republicans have blocked significant gun control laws in the past.

Presentational grey line
A hard reality for Biden
Analysis box by Anthony Zurcher, North America reporter
After recent mass shootings, gun-control activists called on Joe Biden to impose new regulations on firearms. And like past presidents who have sought to address US gun violence, Biden confronts a hard reality.

There are not enough votes in Congress to enact even modest new gun laws. And the steps a president can take unilaterally are limited in scope.

Biden promised that he would do something about gun control, however, so on Thursday he gathered a sympathetic audience in the Rose Garden and unveiled a grab-bag of new actions.

He nominated a head of the Bureau of Alcohol, Tobacco, Firearms and Explosives - a vacancy Donald Trump never bothered to fill. He instructed his Justice Department to come up with new rules for homemade guns and more heavily regulate an attachment that makes handguns more accurate. He called for new gun-violence studies and draft legislation that states could pass.

In a tacit acknowledgement that the scope of these actions are limited, Biden assured his audience that "this is just a start".

To go much farther, however, the political dynamic in Congress will have to change - and Biden, currently more focused on passing his infrastructure package, will have to expend more political capital.

Presentational grey line
What has the reaction been?
Mr Biden's proposed measures have been praised by gun control group Everytown for Gun Safety.

"Each of these executive actions will start to address the epidemic of gun violence that has raged throughout the pandemic and begin to make good on President Biden's promise to be the strongest gun safety president in history," group president John Feinblatt said.

He added that the Biden administration's decision to treat ghost guns "like the deadly weapons they are will undoubtedly save countless lives".

The National Rifle Association (NRA), the biggest gun rights lobby group in the US, described the measures as "extreme" and said it was ready to fight.

Texas Governor Greg Abbott labelled Mr Biden's order as "a new liberal power grab to take away our guns", promising not to allow this in his state.

Later on Thursday, Mr Abbott also tweeted that he had been working with public safety and law enforcement officials in the state over the shooting in Bryan. He promised any help needed to prosecute the suspect and offered prayers for the families of victims.
'''

def do_with_process(process_name):
    nlp = spacy.blank('en')
    nlp.add_pipe('dbpedia_spotlight', config={'process': process_name, 'debug':True})
    doc = nlp(short_text)
    assert(doc.ents)
    if process_name != 'spot':
        for ent in doc.ents:
            print(ent.kb_id_)
            assert 'dbpedia.org' in ent.kb_id_

def get_blank():
    nlp = spacy.blank('en')
    nlp.add_pipe('dbpedia_spotlight')
    return nlp


def test_blank():
    nlp = get_blank()
    doc = nlp(short_text)
    assert(doc.ents)
    for ent in doc.ents:
        assert 'dbpedia.org' in ent.kb_id_

def test_large_text():
    nlp = spacy.blank('en')
    nlp.add_pipe('dbpedia_spotlight')
    doc = nlp(long_text)
    assert(doc.ents)
    for ent in doc.ents:
        assert 'dbpedia.org' in ent.kb_id_

def test_strange_text():
    nlp = get_blank()
    doc = nlp(strange_text)
    assert(doc.ents)
    for ent in doc.ents:
        assert 'dbpedia.org' in ent.kb_id_


def test_large():
    nlp = get_blank()
    doc = nlp(short_text)
    assert(doc.ents)
    for ent in doc.ents:
        assert 'dbpedia.org' in ent.kb_id_

def test_spangroup():
    nlp = spacy.blank('en')
    nlp.add_pipe('dbpedia_spotlight', config={'span_group': 'test_span_group'})
    doc = nlp(short_text)
    assert(doc.ents)
    for span in doc.spans['test_span_group']:
        assert 'dbpedia.org' in span._.dbpedia_raw_result['@URI']

def test_annotate():
    do_with_process('annotate')

def test_spot():
    do_with_process('spot')

def test_candidates():
    do_with_process('candidates')

def test_concurrent_small():
    nlp = spacy.blank('en')
    nlp.add_pipe('dbpedia_spotlight', config={'debug': True})
    docs = list(nlp.pipe([long_text, short_text]))
    assert docs[0].ents, 'document without entities'
    assert docs[1].ents, 'document without entities'
    assert docs[0].text == long_text
    assert len(docs[0].ents) > len(docs[1].ents)


def test_concurrent_big():
    nlp = spacy.blank('en')
    nlp.add_pipe('dbpedia_spotlight')
    texts = [long_text] * 50 + [short_text] * 50
    docs = list(nlp.pipe(texts, batch_size=128))
    # check the order
    assert docs[0].ents, 'document without entities'
    assert docs[1].ents, 'document without entities'
    assert docs[0].text == long_text
    ents_counts = np.array([len(doc.ents) for doc in docs])
    print(ents_counts)
    assert ents_counts[:50].min() == ents_counts[:50].max()
    assert ents_counts[50:].min() == ents_counts[50:].max()
    assert ents_counts[0] == ents_counts[:50].mean()
    assert ents_counts[50] == ents_counts[50:].mean()
    assert ents_counts[0]> ents_counts[50]

def test_languages():
    text_by_lang = {
        # look at README.md for the list of supported languages
        'ca': 'Durant la Guerra dels Segadors, té lloc a Lleida la batalla de les Forques on tropes franceses amb el suport de regiments catalans derroten els terços de Castella.',
        # zh --> Proxy Error 502
        # hr --> Not Found 404
        'da': 'Den 1. januar 2016 blev det besluttet, at der skulle være en ny nationalpark i Danmark, og at den skulle ligge i det nordlige Jylland. Den nye nationalpark skulle hedde Vadehavet Nationalpark.',
        'nl': 'De Nederlandse voetbalclub FC Twente is opgericht in 1965. De club speelt in de Eredivisie en heeft als thuisbasis het stadion De Grolsch Veste.',
        'en': 'The United States presidential election of 2020 was the 59th quadrennial presidential election, held on Tuesday, November 3, 2020. The Democratic ticket of former Vice President Joe Biden and Senator Kamala Harris defeated the incumbent Republican President Donald Trump and Vice President Mike Pence, who were seeking a second term.',
        'fi': 'Suomen presidentinvaalit 2020 pidettiin 28. marraskuuta 2020. Vaalit olivat Suomen 12. presidentinvaalit. Vaalien voitti presidentti Sauli Niinistö, joka sai 62,2 prosenttia äänistä.',
        'fr': 'Le 1er janvier 2016, le gouvernement français a annoncé la création d’une nouvelle réserve naturelle nationale dans le nord du Jutland, au Danemark. Cette réserve naturelle, qui porte le nom de Vadehavet Nationalpark, est la première réserve naturelle nationale danoise.',
        'de': 'Die deutsche Fußballnationalmannschaft ist die Auswahlmannschaft des Deutschen Fußball-Bundes und der höchste Spielmannschaftsverband im deutschen Fußball. Sie repräsentiert Deutschland in internationalen Fußballwettbewerben und ist damit die deutsche Fußballnationalmannschaft.',
        # el --> Not Found 404
        'hu': 'A magyar választások 2020. november 8-án, vasárnap kerültek megrendezésre. A választásokon a Fidesz-KDNP együttműködésében létrejött Választási Szövetség jelöltjei nyertek a parlamenti választásokon, és a Fidesz-KDNP együttműködésében létrejött kormányt alakították meg.',
        'it': 'La nazionale italiana di calcio, nota anche come Squadra Azzurra, è la rappresentativa calcistica dell’Italia e rappresenta il paese nelle competizioni ufficiali internazionali. La Federazione Italiana Giuoco Calcio (FIGC) è l’ente che governa il calcio italiano e si occupa della nazionale.',
        # ja --> Proxy Error 502
        # pip install sudachipy sudachidict-core
        # ko --> Not Found 404
        # lt --> Proxy Error 502
        # mk --> Not Found 404
        # nb --> Not Found 404
        # pl --> Not Found 404
        'pt': 'A seleção brasileira de futebol, também conhecida como seleção canarinho, é a seleção nacional de futebol da República Federativa do Brasil. É organizada pela Confederação Brasileira de Futebol (CBF), entidade máxima do futebol brasileiro.',
        'ro': 'Echipa națională de fotbal a României este echipa națională de fotbal a României și este organizată de Federația Română de Fotbal. Echipa națională a României este una dintre cele mai bune echipe naționale din Europa.',
        'ru': 'Российская футбольная сборная — сборная Российской Федерации по футболу, которая представляет Россию на международных футбольных турнирах. Российская футбольная сборная является одной из самых успешных сборных в мире.',
        'es': 'La selección de fútbol de España, también conocida como La Roja, es la selección de fútbol de España. Es organizada por la Real Federación Española de Fútbol (RFEF), la cual es miembro de la UEFA y de la FIFA.',
        'sv': 'Den svenska fotbollslandslaget är det svenska herrlandslaget i fotboll. Det är den nationella fotbollsförbundet Sveriges fotbollförbund som är ansvarig för fotbollslaget.',
        'tr': "Sarayönü Camii, Lefkoşa'nın kuzey kesiminde yer alan bir camidir",
        # uk --> Not Found 404
    }
    for lang, text in text_by_lang.items():
        nlp = spacy.blank(lang)
        nlp.add_pipe('dbpedia_spotlight')
        doc = nlp(text)
        assert(doc.ents)
        # test one entity
        ent = doc.ents[0]
        if lang == 'en':
            assert f'dbpedia.org' in ent._.dbpedia_raw_result['@URI'], f'@URI {ent._.dbpedia_raw_result["@URI"]} does not match with dbpedia.org'
        else:
            assert f'{lang}.dbpedia.org' in ent._.dbpedia_raw_result['@URI'], f'@URI {ent._.dbpedia_raw_result["@URI"]} does not contain language code {lang}'


def main():
    test_annotate()
    test_spot()
    test_candidates()
    test_concurrent_small()
    test_concurrent_big()


if __name__ == '__main__':
    # to see output
    main()
