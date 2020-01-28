import string
from nltk.corpus import stopwords
import nltk, re
import itertools
from nltk.stem import PorterStemmer

ps = PorterStemmer()
stop_words = list(set(stopwords.words('english')))


def parse_file(file, only_sentences=False):
    with open(file, 'r') as file:
        data = file.read().split('\n\n')
        is_string_re = 'nif:isString.*\"(.*)\"'
        anchorOf_re = 'nif:anchorOf.*\"(.*)\"'

        meta = {}
        sentences = {}

        for item in data:
            tmp = re.search(is_string_re, item)
            if tmp:
                sentences[tmp.group(1)] = item

            tmp = re.search(anchorOf_re, item)
            if tmp:
                meta[tmp.group(1)] = item

    if only_sentences:
        return list(sentences.keys())[0], sentences
    else:
        return meta, sentences


def ie_preprocess(document):
    sentences = [nltk.word_tokenize(sent) for sent in document]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences


def process_using_spacy(sent, en_core, format_result):
    entities = en_core(sent).ents
    if format_result:
        result = list(
            zip([e.text for e in entities], [e.label_ for e in entities]))
    else:
        result = entities
    return result


big_dict = {
    ('Organisation', 'Organisation'): ['affiliation'],
    ('Person', 'EducationalInstitution'): ['almaMater'],
    ('Band', 'Person'): ['formerBandMember', 'bandMember'],
    ('Person', 'Place'): ['deathPlace', 'birthPlace'],
    ('Organisation', 'Person'): ['president', 'ceo'],
    ('Person', 'Person'): ['spouse', 'relative', 'parent', 'child'],
    ('Athlete', 'SportsTeam'): ['formerTeam', 'debutTeam', 'club'],
    ('Organisation', 'Country'): ['country'],
    ('Person', 'Country'): ['country'],
    ('Place', 'Country'): ['country'],
    ('PopulatedPlace', 'PopulatedPlace'): ['department'],
    ('Place', 'PopulatedPlace'): ['district'],
    ('Scientist', 'Person'): ['doctoralStudent', 'doctoralAdvisor'],
    ('Person', 'Organisation'): ['employer'],
    ('Organisation', 'City'): ['foundationPlace'],
    ('Organisation', 'PopulatedPlace'): ['headquarter'],
    ('Organisation', 'Settlement'): ['hometown'],
    ('Person', 'Settlement'): ['hometown'],
    ('PopulatedPlace', 'Person'): ['leaderName'],
    ('Place', 'Place'): ['locatedInArea'],
    ('Organisation', 'Place'): ['location'],
    ('Person', 'Place'): ['location'],
    ('Place', 'Place'): ['location'],
    ('Person', 'Country'): ['nationality'],
    ('Company', 'Company'): ['subsidiary'],
    ('ArchitecturalStructure', 'Organisation'): ['tenant'],
    ('Athlete', 'Person'): ['trainer'],
    ('Organisation', 'Date'): ['when'],
    ('Date', 'Organisation'): ['when'],
    ('Person', 'Date'): ['when'],
    ('Date', 'Person'): ['when']
}

maps = {
    'ORG': 'Organisation',
    'PERSON': 'Person',
    'GPE': 'Place',
    'DATE': 'Date'
}


def get_relation(pairs, sent):
    perm = list(itertools.permutations(pairs, 2))

    sent = sent.translate(str.maketrans('', '', string.punctuation))
    sent = [ps.stem(w) for w in nltk.word_tokenize(sent) if not w in stop_words]

    rel = []
    for a, b in perm:
        if a[1] in maps.keys() and b[1] in maps.keys():
            if (maps[a[1]], maps[b[1]]) in big_dict:
                co = big_dict[(maps[a[1]], maps[b[1]])]
                for c in co:
                    if ps.stem(c) in sent:
                        rel.append((a, b, c))
    return rel
