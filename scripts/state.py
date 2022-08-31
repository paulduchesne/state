
import ansible_vault
import json
import pathlib
import pydash
import rdflib
import uuid

def write_statement(path, graph):

    ''' Create or append new triple. '''

    if path.exists():
        extant_graph = rdflib.Graph()
        extant_graph.parse(path)
        extant_graph += graph
        extant_graph.serialize(destination=path, format='nt', encoding='utf-8')
    else:
        graph.serialize(destination=path, format='nt', encoding='utf-8')

def format_statement(s, p, o, n):

    ''' Author triple as encrypted statement. '''

    ident_file = pathlib.Path.cwd().parents[0] / 'person.json'

    if not ident_file.exists():
        raise Exception('Ident file not found.')
    else:
        with open(ident_file) as ident_uuid:
            ident_uuid = json.load(ident_uuid)
            ident = pydash.get(ident_uuid, 'identifier')

    ont = rdflib.Namespace(f'https://{ident}.org/ontology/')
    res = rdflib.Namespace(f'https://{ident}.org/resource/')

    statement_key = str(uuid.uuid4())
    statement_ident = str(uuid.uuid4())

    triple_graph = rdflib.Graph()
    triple_graph.add((s, p ,o))
    raw_triple = triple_graph.serialize(format='nt')

    enc_statement = ansible_vault.Vault(statement_key).dump_raw(raw_triple)

    data_graph = rdflib.Graph()
    data_graph.add((res[statement_ident], rdflib.RDF.type, ont['statement']))
    data_graph.add((res[statement_ident], ont.hasPayload, rdflib.Literal(enc_statement)))
    data_path = pathlib.Path.cwd().parents[0] / 'data' / f'{n}.nt'
    data_path.parents[0].mkdir(exist_ok=True)
    write_statement(data_path, data_graph)

    key_graph = rdflib.Graph()
    key_graph.add((res[statement_ident], ont.hasKey, rdflib.Literal(statement_key)))
    key_path = pathlib.Path.cwd().parents[0] / 'keys.nt'
    write_statement(key_path, key_graph)