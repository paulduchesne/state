
# add location to graph.
# note that this assumes no two entities sahre the same name!

import pathlib
import rdflib
import uuid

# information to be added.

entity = {
    "label": "Wellington",
    "comment": "Capital city of New Zealand.",
    "wikidata": "Q23661",
}

# load existing graph.

data_path = pathlib.Path.cwd().parent / 'public.ttl'
if not data_path.exists():
    raise Exception('File not found.')
data = rdflib.Graph().parse(data_path)

# pull or mind id.

entity['id'] = f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}"
persons = [s for s,p,o in data.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Location')))]
for p in persons:
    for a,b,c in data.triples((p, rdflib.RDFS.label, None)):
        if str(c) == entity['label']:
            entity['id'] = p

# add label.

data.add((rdflib.URIRef(entity['id']), rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Location')))
data.add((rdflib.URIRef(entity['id']), rdflib.RDFS.label, rdflib.Literal(entity['label'], lang='en')))

# add comment.

if len(entity['comment']):
    comment = [o for s,p,o in data.triples((rdflib.URIRef(entity['id']), rdflib.RDFS.comment, None))]
    if not len(comment):
        data.add((rdflib.URIRef(entity['id']), rdflib.RDFS.comment, rdflib.Literal(entity['comment'], lang='en')))

# add wikidata.

if len(entity['wikidata']):
    wikidata = [o for s,p,o in data.triples((rdflib.URIRef(entity['id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), None))]
    if not len(wikidata):
        data.add((rdflib.URIRef(entity['id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), rdflib.Literal(entity['wikidata'])))

# write to graph.

data.serialize(data_path, format='longturtle')

