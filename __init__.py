
from cryptography.fernet import Fernet
import base64
import json
import pandas
import pathlib
import rdflib
import uuid

def write_statements(graph):

    ''' Parse private to public graph. '''
    
    private_keys = dict()

    for s,p,o in graph.triples((None, None, None)):

        statement_id = str(uuid.uuid4())
        statement_uri = rdflib.URIRef('web://'+statement_id)
        statement = rdflib.Graph().add((s, p, o)).serialize(format='nt')

        key = str(uuid.uuid4()).replace('-', '')
        fernet = Fernet(base64.urlsafe_b64encode(key.encode()))

        public_graph = rdflib.Graph()
        public_graph.add((statement_uri, rdflib.RDF.type, rdflib.URIRef('state://ontology/statement')))
 
        state_literal = rdflib.Literal(fernet.encrypt(statement.encode()).decode())
        public_graph.add((statement_uri, rdflib.URIRef('state://ontology/content'), state_literal))

        graph_path = pathlib.Path.home() / 'state' / 'turtle' / statement_id[:2] / f'{statement_id}.ttl'
        graph_path.parents[0].mkdir(exist_ok=True, parents=True)
        public_graph.serialize(destination=str(graph_path), format='turtle')

        private_keys[statement_id] = key

    keys_path = pathlib.Path.home() / 'state' / 'private.json'
    if not keys_path.exists():
        with open(keys_path, 'w') as keys_out:
            json.dump(private_keys, keys_out, indent=4)
    else:
        with open(keys_path) as keys_in:
            keys_in = json.load(keys_in)
        
        with open(keys_path, 'w') as keys_out:
            json.dump(keys_in | private_keys, keys_out, indent=4)

def read_statement(statement_id):

    ''' Retrieve triple against provided state id. '''

    key_path = pathlib.Path.home() / 'state' / 'private.json'
    if not key_path.exists():
        raise Exception('Keys could not be found.')
    else:
        with open(key_path) as private_keys:
            private_keys = json.load(private_keys)

    statement_path = pathlib.Path.home() / 'state' / 'turtle' / statement_id[:2] / f'{statement_id}.ttl'
    public_statememt = rdflib.Graph().parse(statement_path)
    for s,p,o in public_statememt:
        if p == rdflib.URIRef('state://ontology/content'):
            if pathlib.Path(s).name in private_keys:
                key = private_keys[pathlib.Path(s).name]
                fernet = Fernet(base64.urlsafe_b64encode(key.encode()))
                private_statement = fernet.decrypt(o.encode()).decode()
                private_graph = rdflib.Graph().parse(data=private_statement)

                return private_graph

def map_statements():

    ''' Regenerate files from existing graph. '''

    # build a map of the private graph. this is currently being performed on-the-fly, 
    # but an alternate model would be that a local copy exists to be consulted.

    map_df = pandas.DataFrame(columns=['source', 'subject', 'predicate', 'object'])
    public_statements = [x.stem for x in (pathlib.Path.home() / 'state' / 'turtle' ).rglob('*') if x.suffix == '.ttl']
    for x in public_statements:

        res_triple = read_statement(x)

        if res_triple:

            for a,b,c in res_triple.triples((None, None, None)):
                if type(c) == type(rdflib.URIRef('')):
                    map_df.loc[len(map_df)] = [(x),(a), (b), (c)]
                elif type(c) == type(rdflib.Literal('')):
                    map_df.loc[len(map_df)] = [(x),(a), (b), (rdflib.Literal('LITERAL'))]
                else:
                    raise Exception('Unknown object type.')

    return map_df

def map_update():

    ''' Unlike map statemenst, map update works off a disk resource. '''

    map_path = pathlib.Path.home() / 'state' / 'map.parquet'
    if not map_path.exists():
        map_df = pandas.DataFrame(columns=['source', 'subject', 'predicate', 'object'])
        map_df.to_parquet(map_path)
    else:
        map_df = pandas.read_parquet(map_path)

    public_statements = [x.stem for x in (pathlib.Path.home() / 'state' / 'turtle' ).rglob('*') if x.suffix == '.ttl']
    for x in public_statements:
        if x not in map_df.source.unique():
            res_triple = read_statement(x)
            if res_triple:
                for a,b,c in res_triple.triples((None, None, None)):
                    if type(c) == type(rdflib.URIRef('')):
                        map_df.loc[len(map_df)] = [(x),(a), (b), (c)]
                    elif type(c) == type(rdflib.Literal('')):
                        map_df.loc[len(map_df)] = [(x),(a), (b), (rdflib.Literal('LITERAL'))]
                    else:
                        raise Exception('Unknown object type.')

    map_df.to_parquet(map_path)

    return map_df

