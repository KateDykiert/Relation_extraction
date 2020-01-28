from SPARQLWrapper import SPARQLWrapper, JSON
import json

import en_core_web_sm
import itertools

import functions as f

sentence_list = []
basepath = 'training/'

# for entry in os.listdir(basepath):
#     if os.path.isfile(os.path.join(basepath, entry)):
#         sent, sentences = f.parse_file(basepath + entry, only_sentences=True)
#         sentence_list.append(sent)
#         # print(sent)


sent, sentences = f.parse_file('training/file5.ttl', only_sentences=True)
print(sent)
sentence_list.append(sent)

chunks = []
core = en_core_web_sm.load()

for sentence in sentence_list:
    pairs = f.process_using_spacy(sentence, en_core=core, format_result=True)
    chunks.append(pairs)

print('Word with entities --------------------------------')
print(chunks)

chunks_no_space = []
for element in chunks:
    tab = []
    for chunk in element:
        tab.append(chunk[0].replace(' ', '_'))
    chunks_no_space.append(tab)

print('Word with entities --------------------------------')
print(chunks_no_space)

permutations = []
for chunk in chunks_no_space:
    permutations.append(list(itertools.permutations(chunk, 2)))
#
print('Permutations --------------------------------')
print(permutations)

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
for perm in permutations:
    for pair in perm:
        if len(pair) > 1:
            sparql.setQuery("""SELECT ?relationship
            WHERE {
                <http://dbpedia.org/resource/""" + pair[0] + """>
                ?relationship
                <http://dbpedia.org/resource/""" + pair[1] + """>
            }""")
            sparql.setReturnFormat(JSON)

            response = sparql.query().convert()
            if response["results"]["bindings"]:
                for relationship in response["results"]["bindings"]:
                    value = relationship["relationship"]["value"]
                    if value != "http://dbpedia.org/ontology/wikiPageWikiLink" and value != "http://www.w3.org/2000/01/rdf-schema#seeAlso" \
                            and value != "http://dbpedia.org/ontology/wikiPageRedirects":
                        print(pair[0] + " & " + pair[1])
                        print(json.dumps(relationship, sort_keys=True, indent=4))
                        print("=============================================================================")

print("Second solution------------------------------------------------------------------------")

for index, sente in enumerate(sentence_list):
    relation = f.get_relation(chunks[index], sente)
    print(relation)
