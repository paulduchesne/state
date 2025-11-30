
# add person to graph.
# note that this assumes no two individuals with the same name!

import pathlib
import rdflib
import uuid

# information to be added.

person = {
    "label": "Ina Blümel",
    "comment": "German information scientist and architect.",
    "member": "Technische Informationsbibliothek",
    "wikidata": "Q57697004",
}

# load existing graph.

graph_path = pathlib.Path.cwd().parent / 'data.ttl'
if not graph_path.exists():
    raise Exception('File not found.')
graph = rdflib.Graph().parse(graph_path)

# pull or mind id.

person['id'] = f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}"
persons = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))]
for p in persons:
    for a,b,c in graph.triples((p, rdflib.RDFS.label, None)):
        if str(c) == person['label']:
            person['id'] = p

# add label.

graph.add((rdflib.URIRef(person['id']), rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))
graph.add((rdflib.URIRef(person['id']), rdflib.RDFS.label, rdflib.Literal(person['label'], lang='en')))

# add comment.

if len(person['comment']):
    comment = [o for s,p,o in graph.triples((rdflib.URIRef(person['id']), rdflib.RDFS.comment, None))]
    if not len(comment):
        graph.add((rdflib.URIRef(person['id']), rdflib.RDFS.comment, rdflib.Literal(person['comment'], lang='en')))

# add membership.

if len(person['member']):
    membership = [o for s,p,o in graph.triples((rdflib.URIRef(person['id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/memberOf'), None))]
    if not len(membership):
        orgs = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Institution')))]
        for o in orgs:
            for a,b,c in graph.triples((o, rdflib.RDFS.label, None)):
                if str(c) == person['member']:
                    graph.add((rdflib.URIRef(person['id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/memberOf'), a))
                    graph.add((a, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasMember'), rdflib.URIRef(person['id'])))

# add wikidata.

if len(person['wikidata']):
    wikidata = [o for s,p,o in graph.triples((rdflib.URIRef(person['id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), None))]
    if not len(wikidata):
        graph.add((rdflib.URIRef(person['id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), rdflib.Literal(person['wikidata'])))

# write to graph.

graph.serialize(graph_path, format='longturtle')

