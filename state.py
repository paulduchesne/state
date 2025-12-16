
# library of common functions.

import pathlib
import rdflib
import uuid

def test():
    print('hello')

def person(label: str, comment: str, member: str, wikidata: str) -> str:
    """
    Generate/update a person record.

    :param label: name of the person.
    :param comment: short text description of the person.
    :param member: notable organisational membership.
    :param wikidata: corresponding wikidata id.
    """

    # load existing graph.

    graph_path = pathlib.Path.cwd() / 'data.ttl'
    if not graph_path.exists():
        raise Exception('File not found.')
    graph = rdflib.Graph().parse(graph_path)

    # pull or mind id.

    uri = f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}"
    persons = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))]
    for p in persons:
        for a,b,c in graph.triples((p, rdflib.RDFS.label, None)):
            if str(c) == label:
                uri = p

    # declare person.

    graph.add((rdflib.URIRef(uri), rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))

    # add label.

    if label:
        labels = [o for s,p,o in graph.triples((rdflib.URIRef(uri), rdflib.RDFS.label, None))]
        if not len(labels):
            graph.add((rdflib.URIRef(uri), rdflib.RDFS.label, rdflib.Literal(label, lang='en')))

    # add comment.

    if comment:
        comments = [o for s,p,o in graph.triples((rdflib.URIRef(uri), rdflib.RDFS.comment, None))]
        if not len(comments):
            graph.add((rdflib.URIRef(uri), rdflib.RDFS.comment, rdflib.Literal(comment, lang='en')))

    # add membership.

    if member:
        orgs = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Institution')))]
        for o in orgs:
            for a,b,c in graph.triples((o, rdflib.RDFS.label, None)):
                if str(c) == member:
                    graph.add((rdflib.URIRef(uri), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/memberOf'), a))
                    graph.add((a, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasMember'), rdflib.URIRef(uri)))

    # add wikidata.

    if wikidata:
        wikidatas = [o for s,p,o in graph.triples((rdflib.URIRef(uri), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), None))]
        if not len(wikidatas):
            graph.add((rdflib.URIRef(uri), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), rdflib.Literal(wikidata)))

    # write to graph.

    graph.serialize(graph_path, format='longturtle')

    # return entity uri.

    return uri


