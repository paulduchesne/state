
import ansible_vault
import json
import pathlib
import rdflib
import uuid

# check authored data can be retrieved.

def author_triple(s, p, o, n):

    ''' Author triple as encrypted statement. '''

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
    data_graph.serialize(destination=data_path, format='nt', encoding='utf-8')

    key_graph = rdflib.Graph()
    key_graph.add((res[statement_ident], ont.hasKey, rdflib.Literal(statement_key)))
    key_path = pathlib.Path.cwd().parents[0] / 'keys.nt'
    key_graph.serialize(destination=key_path, format='nt', encoding='utf-8')

    # you need a function here, if path does not exist, create.
    # otherwise append.

json_path = pathlib.Path.cwd().parents[0] / "person.json"

# if not json_path.exists():
if json_path.exists():

    print("\n// Define subject entity.")

    name = input("\nProvide name: ")
    dob = input("\nProvide date of birth: ")
    ident = str(uuid.uuid4())

    with open(json_path, "w") as json_data:
        json.dump({"identifier": ident}, json_data)

    ont = rdflib.Namespace(f'https://{ident}.org/ontology/')
    res = rdflib.Namespace(f'https://{ident}.org/resource/')

    author_triple(res[ident], rdflib.RDFS.label, rdflib.Literal(name), ident)
    author_triple(res[ident], ont.hasBirthDate, rdflib.Literal(dob), ident)
