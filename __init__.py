
from cryptography.fernet import Fernet
import base64
import json
import pathlib
import rdflib
import uuid

def write_statements(graph):

    ''' Parse private to public graph. '''
    
    private_keys = dict()

    for s,p,o in graph.triples((None, None, None)):

        statement_uuid = str(uuid.uuid4())
        statement_uri = rdflib.URIRef('web://'+statement_uuid)
        statement = rdflib.Graph().add((s, p, o)).serialize(format='nt')

        key = str(uuid.uuid4()).replace('-', '')
        fernet = Fernet(base64.urlsafe_b64encode(key.encode()))

        public_graph = rdflib.Graph()
        public_graph.add((statement_uri, rdflib.RDF.type, rdflib.URIRef('state://ontology/statement')))
 
        state_literal = rdflib.Literal(fernet.encrypt(statement.encode()).decode())
        public_graph.add((statement_uri, rdflib.URIRef('state://ontology/content'), state_literal))

        graph_path = pathlib.Path.home() / 'state' / 'turtle' / statement_uuid[:2] / f'{statement_uuid}.ttl'
        graph_path.parents[0].mkdir(exist_ok=True, parents=True)
        public_graph.serialize(destination=str(graph_path), format='turtle')

        private_keys[statement_uuid] = key

    keys_path = pathlib.Path.home() / 'state' / 'private.json'
    if not keys_path.exists():
        with open(keys_path, 'w') as keys_out:
            json.dump(private_keys, keys_out, indent=4)
    else:
        with open(keys_path) as keys_in:
            keys_in = json.load(keys_in)
        
        with open(keys_path, 'w') as keys_out:
            json.dump(keys_in | private_keys, keys_out, indent=4)
