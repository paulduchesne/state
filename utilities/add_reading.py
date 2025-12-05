
# add book reading event to graph.
# note that this assumes no two entities with the same name!

import pathlib
import rdflib
import uuid

# information to be added.

data = {
    'reader_uuid': '0ef53722-52ca-49c8-873d-3549a74914e8', 
    'book_label': 'The School of Night',
    'book_isbn': '9781787304215',
    'author_label': 'Karl Ove Knausgaard',
    'author_decription': 'Norwegian writer.',
    'author_wikidata': 'Q609317',
    'event_start': '2025-11-23',
    'event_end': '2025-12-03'
}

# load existing graph.

graph_path = pathlib.Path.cwd().parent / 'data.ttl'
if not graph_path.exists():
    raise Exception('File not found.')
graph = rdflib.Graph().parse(graph_path)

print(len(graph))

# pull or mind author id.

data['author_id'] = f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}"
persons = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))]
for p in persons:
    for a,b,c in graph.triples((p, rdflib.RDFS.label, None)):
        if str(c) == data['author_label']:
            data['author_id'] = p

# add author label.

graph.add((rdflib.URIRef(data['author_id']), rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))
graph.add((rdflib.URIRef(data['author_id']), rdflib.RDFS.label, rdflib.Literal(data['author_label'], lang='en')))

# add author comment.

if len(data['author_decription']):
    comment = [o for s,p,o in graph.triples((rdflib.URIRef(data['author_id']), rdflib.RDFS.comment, None))]
    if not len(comment):
        graph.add((rdflib.URIRef(data['author_id']), rdflib.RDFS.comment, rdflib.Literal(data['author_decription'], lang='en')))

# add author wikidata.

if len(data['author_wikidata']):
    wikidata = [o for s,p,o in graph.triples((rdflib.URIRef(data['author_id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), None))]
    if not len(wikidata):
        graph.add((rdflib.URIRef(data['author_id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), rdflib.Literal(data['author_wikidata'])))

# pull or mind book id.

data['book_id'] = f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}"
books = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Book')))]
for p in books:
    for a,b,c in graph.triples((p, rdflib.RDFS.label, None)):
        if str(c) == data['book_label']:
            data['book_id'] = p

# add book detail.

graph.add((rdflib.URIRef(data['book_id']), rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Book')))
graph.add((rdflib.URIRef(data['book_id']), rdflib.RDFS.label, rdflib.Literal(data['book_label'], lang='en')))
graph.add((rdflib.URIRef(data['book_id']), rdflib.RDFS.comment, rdflib.Literal(f'Book by {data['author_label']}', lang='en')))
graph.add((rdflib.URIRef(data['book_id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/identifier'), rdflib.Literal(data['book_isbn'])))
graph.add((rdflib.URIRef(data['book_id']), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasAuthor'), rdflib.URIRef(data['author_id'])))

# detect if a reading event already exist.

# TODO this currently assumes that a reader never re-reads a book!
# fix would be to also factor in the event start date.

write_reading_event = True
reading_events = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/ReadingEvent')))]
for r in reading_events:
    matching_reader = [s for s,p,o in graph.triples((r, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), rdflib.URIRef(f'https://paulduchesne.github.io/state/resource/{data['reader_uuid']}')))]
    matching_book = [s for s,p,o in graph.triples((r, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), rdflib.URIRef(data['book_id'])))]
    if len(matching_reader) and len(matching_book):
        write_reading_event = False

# if required, write reading event.

if write_reading_event:
    event_uri = rdflib.URIRef(f'https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}')
    graph.add((event_uri, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/ReadingEvent')))
    graph.add((event_uri, rdflib.RDFS.label, rdflib.Literal(f"Reading '{data['book_label']}'", lang='en')))
    graph.add((event_uri, rdflib.RDFS.comment, rdflib.Literal(f'Reading event.', lang='en')))
    graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), rdflib.URIRef(f'https://paulduchesne.github.io/state/resource/{data['reader_uuid']}')))
    graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), rdflib.URIRef(data['book_id'])))
    graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/startDate'), rdflib.Literal(data['event_start'])))
    graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/endDate'), rdflib.Literal(data['event_end'])))

# TODO you need to write reading event to reader and book as inverse properties.

# write to graph.

graph.serialize(graph_path, format='longturtle')
