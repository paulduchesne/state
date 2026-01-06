
# add organisation to graph.
# note that this assumes no two individuals with the same name!

import pathlib
import rdflib
import uuid

# information to be added.

org = {
    "label": "iPRES",
    "comment": "International community of Digital Preservation archivists.",
    'wikidata': '',
}

# load existing graph.

data_path = pathlib.Path.cwd().parent / 'public.ttl'
if not data_path.exists():
    raise Exception('File not found.')
data = rdflib.Graph().parse(data_path)

# pull or mind id.

org['id'] = f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}"
orgs = [s for s,p,o in data.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Organisation')))]
for p in orgs:
    for a,b,c in data.triples((p, rdflib.RDFS.label, None)):
        if str(c) == org['label']:
            org['id'] = p

# add label.

data.add((rdflib.URIRef(org['id']), rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Organisation')))
data.add((rdflib.URIRef(org['id']), rdflib.RDFS.label, rdflib.Literal(org['label'], lang='en')))

# add comment.

if len(org['comment']):
    comment = [o for s,p,o in data.triples((rdflib.URIRef(org['id']), rdflib.RDFS.comment, None))]
    if not len(comment):
        data.add((rdflib.URIRef(org['id']), rdflib.RDFS.comment, rdflib.Literal(org['comment'], lang='en')))

# add wikidata.

if len(org['wikidata']):
    wikidata = [o for s,p,o in data.triples((rdflib.URIRef(org['id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), None))]
    if not len(wikidata):
        data.add((rdflib.URIRef(org['id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), rdflib.Literal(org['wikidata'])))

# write to graph.

data.serialize(data_path, format='longturtle')

