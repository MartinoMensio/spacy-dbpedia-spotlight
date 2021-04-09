import spacy
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


def main():
    test_annotate()
    test_spot()
    test_candidates()


if __name__ == '__main__':
    # to see output
    main()
