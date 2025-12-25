
# library of common functions.

import pathlib
import rdflib
import uuid

def test():
    print('hello')

def person(label: str, comment: str, member: str, wikidata: str) -> str:
    """
    Generate/update a person record.
    Note that this currently assumes no two entities share the same name.

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

    # pull or mint id.

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

def location(label: str, comment: str, wikidata: str) -> str:
    """
    Generate/update a location record.
    Note that this currently assumes no two entities share the same name.

    :param label: name of the location.
    :param comment: short text description of the location.
    :param wikidata: corresponding wikidata id.
    """

    # load existing graph.

    graph_path = pathlib.Path.cwd() / 'data.ttl'
    if not graph_path.exists():
        raise Exception('File not found.')
    graph = rdflib.Graph().parse(graph_path)

    # pull or mint id.

    uri = f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}"
    entities = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Location')))]
    for p in entities:
        for a,b,c in graph.triples((p, rdflib.RDFS.label, None)):
            if str(c) == label:
                uri = p

    # declare location.

    graph.add((rdflib.URIRef(uri), rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Location')))

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

    # add wikidata.

    if wikidata:
        wikidatas = [o for s,p,o in graph.triples((rdflib.URIRef(uri), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), None))]
        if not len(wikidatas):
            graph.add((rdflib.URIRef(uri), rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), rdflib.Literal(wikidata)))

    # write to graph.

    graph.serialize(graph_path, format='longturtle')

    # return entity uri.

    return uri

def reading_event(
        reader_id: str, 
        book_label: str, 
        book_isbn: str,
        author_label: str,
        author_decription: str,
        author_wikidata: str,
        event_start: str,
        event_end: str,
        ) -> str:
    
    """
    Generate/update a reading event record.
    Note that this currently assumes no two entities share the same name,
    also multiple readings of the same book is currently not supported.
    
    :param reader_id: uuid of the reader entity.
    :param book_label: title of the book.
    :param book_isbn: isbn of the book.
    :param author_label: name of the author.
    :param author_decription: description of the author.
    :param author_wikidata: corresponding wikidata id.
    :param event_start: date which the event began.
    :param event_end: date which the event ended.
    """

    # load existing graph.

    graph_path = pathlib.Path.cwd() / 'data.ttl'
    if not graph_path.exists():
        raise Exception('File not found.')
    graph = rdflib.Graph().parse(graph_path)

    # verify if reader exists, and is a person.

    reader_uri = rdflib.URIRef(f'https://paulduchesne.github.io/state/resource/{reader_id}')
    persons = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))]
    if reader_uri not in persons:
        raise Exception('Reader does not exist in graph.')

    # pull or mint author id.

    author_uri = rdflib.URIRef(f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}")
    persons = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))]
    for p in persons:
        for a,b,c in graph.triples((p, rdflib.RDFS.label, None)):
            if str(c) == author_label:
                author_uri = p

    # declare author.

    graph.add((author_uri, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))

    # add author label.

    if author_label:
        labels = [o for s,p,o in graph.triples((author_uri, rdflib.RDFS.label, None))]
        if not len(labels):
            graph.add((author_uri, rdflib.RDFS.label, rdflib.Literal(author_label, lang='en')))

    # add author comment.

    if author_decription:
        comments = [o for s,p,o in graph.triples((author_uri, rdflib.RDFS.comment, None))]
        if not len(comments):
            graph.add((author_uri, rdflib.RDFS.comment, rdflib.Literal(author_decription, lang='en')))

    # add author wikidata.

    if author_wikidata:
        wikidatas = [o for s,p,o in graph.triples((author_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), None))]
        if not len(wikidatas):
            graph.add((author_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/wikidataIdentifier'), rdflib.Literal(author_wikidata)))

    # pull or mint book id.

    book_uri = rdflib.URIRef(f"https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}")
    books = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Book')))]
    for x in books:
        for a,b,c in graph.triples((x, rdflib.RDFS.label, None)):
            if str(c) == book_label:
                book_uri = x

    # declare book.

    graph.add((book_uri, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Book')))

    # declare book author.

    graph.add((book_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasAuthor'), author_uri))
    graph.add((author_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/authorOf'), book_uri))

    # declare book isbn.

    if book_isbn:
        graph.add((book_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/identifier'), rdflib.Literal(book_isbn)))

   # add book label.

    if book_label:
        labels = [o for s,p,o in graph.triples((book_uri, rdflib.RDFS.label, None))]
        if not len(labels):
            graph.add((book_uri, rdflib.RDFS.label, rdflib.Literal(book_label, lang='en')))

    # add book description.

    book_description = [o for s,p,o in graph.triples((book_uri, rdflib.RDFS.comment, None))]
    if not len(book_description):
        graph.add((book_uri, rdflib.RDFS.comment,  rdflib.Literal(f'Book by {author_label}', lang='en')))

    # detect if a reading event already exist.

    # TODO this currently assumes that a reader never re-reads a book!
    # fix would be to also factor in the event start date as a filter on extant event.

    write_reading_event = True
    reading_events = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/ReadingEvent')))]
    for r in reading_events:
        matching_reader = [s for s,p,o in graph.triples((r, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), reader_uri))]
        matching_book = [s for s,p,o in graph.triples((r, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), book_uri))]
        if len(matching_reader) and len(matching_book):
            write_reading_event = False

    # if required, write reading event.
    # TODO, this does not currently update new info provided (most obvious, an event end date.)

    if write_reading_event:
        event_uri = rdflib.URIRef(f'https://paulduchesne.github.io/state/resource/{str(uuid.uuid4())}')
        graph.add((event_uri, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/ReadingEvent')))
        graph.add((event_uri, rdflib.RDFS.label, rdflib.Literal(f"Reading '{book_label}'", lang='en')))
        graph.add((event_uri, rdflib.RDFS.comment, rdflib.Literal(f'Reading event.', lang='en')))
        graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), reader_uri))
        graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), book_uri))
        graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/startDate'), rdflib.Literal(event_start)))
        graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/endDate'), rdflib.Literal(event_end)))
        graph.add((reader_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/participatedIn'), event_uri))
        graph.add((book_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/participatedIn'), event_uri))

    # write to graph.

    graph.serialize(graph_path, format='longturtle')

    # return entity uri.

    return author_uri

def attendance(
        attendee_label: str, 
        event_label: str, 
        ) -> str:
    
    """
    Generate/update an event attendance.
    Note that this currently assumes no two entities share the same name,

    :param attendee_label: name of the person attending the event.
    :param event_label: name of the event being attended.
    """

    # load existing graph.

    graph_path = pathlib.Path.cwd() / 'data.ttl'
    if not graph_path.exists():
        raise Exception('File not found.')
    graph = rdflib.Graph().parse(graph_path)

    # validate attendee.

    attendee_uri = None
    persons = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/Person')))]
    for p in persons:
        for a,b,c in graph.triples((p, rdflib.RDFS.label, None)):
            if str(c) == attendee_label:
                attendee_uri = p
    if not attendee_uri:
        raise Exception('Person does not exist in graph.')
    
    # validate event.

    event_uri = None
    events = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/OrganisationalEvent')))]
    for p in events:
        for a,b,c in graph.triples((p, rdflib.RDFS.label, None)):
            if str(c) == event_label:
                event_uri = p
    if not event_uri:
        raise Exception('Event does not exist in graph.')
    
    # add attendee triples.

    graph.add((attendee_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/participatedIn'), event_uri))
    graph.add((event_uri, rdflib.URIRef('https://paulduchesne.github.io/state/ontology/hasParticipant'), attendee_uri))

    # write to graph.

    graph.serialize(graph_path, format='longturtle')

