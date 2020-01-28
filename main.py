import itertools

from SPARQLWrapper import SPARQLWrapper, JSON, XML
import json
import functions as f
import os, nltk, re
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('universal_tagset')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
#nltk.download('ace')

sentence_list = []
basepath = 'training/'
for entry in os.listdir(basepath):
    if os.path.isfile(os.path.join(basepath, entry)):
        sent, sentences = f.parse_task_1_2(basepath+entry, only_sentences=True)
        sentence_list.append(sent)

print(sentence_list[0:10])
tokens = f.ie_preprocess(sentence_list)
grammar3 = "PERSON: {<PERSON><PERSON>+}"
cp = nltk.RegexpParser(grammar3)

chunks = []
for t in tokens:
    chunk = nltk.ne_chunk(t)
    #chunk2 = cp.parse(chunk)
    chunks.append(chunk)

print(chunks[0:10])
founds = []
for chunk in chunks:
    s = []
    for i in chunk.subtrees(filter=lambda x: x.label() == 'PERSON' or x.label() == 'ORGANIZATION' or x.label() == 'GPE'):
        count = 0
        for val in i:
            if count == 0 :
                #print(val[0])
                s.append(val[0])
                count = 1
            else:
                #print(val[0])
                s[len(s)-1] = s[len(s)-1] + '_' + val[0]
    founds.append(s)

print(founds)

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
perm = []
for l in founds:
    perm.append(list(itertools.combinations(l,2)))
    #perm.append(pm)
perm = list(itertools.chain(*perm))
print(perm)
print(len(perm))
#perm = list(dict.fromkeys(perm))
#print(len(perm))
for i in perm:
    if len(i) > 1:
        sparql.setQuery("""SELECT ?relationship
        WHERE {
            <http://dbpedia.org/resource/"""+i[0]+""">
            ?relationship 
            <http://dbpedia.org/resource/"""+i[1]+""">
        }""")
        sparql.setReturnFormat(JSON)

        response = sparql.query().convert()
        if response["results"]["bindings"] != []:
            for ind, relationship in enumerate(response["results"]["bindings"]):
                value = response["results"]["bindings"][ind]["relationship"]["value"]
                if value != "http://dbpedia.org/ontology/wikiPageWikiLink" and value != "http://www.w3.org/2000/01/rdf-schema#seeAlso"\
                        and value != "http://dbpedia.org/ontology/wikiPageRedirects":
                    print(i[0] +" & "+ i[1])
                    print(json.dumps(relationship, sort_keys=True, indent=4))
                    print("=============================================================================")

#def findRelation(json, name):
#    for dict in json["results"]["bindings"]:
#        if str(dict["o"]["value"]).find(name) != -1:
#            return dict
#    return "relation not found"

#print(findRelation(response, "James_Damore"))