from cryptography.fernet import Fernet
import base64
import json
import pathlib
import pydash
import rdflib
import uuid

def encryption_pair():

    ''' Generate statement id and corresponding key. '''

    statement_uuid = str(uuid.uuid4()).replace('-','')
    key_uuid = str(uuid.uuid4()).replace('-','')

    config_location = pathlib.Path.cwd() / 'individual.json'
    with open(config_location) as config:
        config = json.load(config)

    pull_keys = config['keys']
    pull_keys[statement_uuid] = key_uuid
    config['keys'] = pull_keys

    with open(config_location, 'w') as config_out:
        json.dump(config, config_out)

    return {'statement':statement_uuid, 'key':key_uuid}

def me(name, birth):

    ''' Define individual. '''
    
    config_location = pathlib.Path.cwd() / 'individual.json'
    if config_location.exists():
        print('Individual already defined.')
    else:
        individual = {"uuid":str(uuid.uuid4()), "name":name, "birth":birth, "keys":{}}
        with open(config_location, 'w') as config:
            json.dump(individual, config)

def individual():

    ''' Retrieve state config file. '''

    config_location = pathlib.Path.cwd() / 'individual.json'
    if not config_location.exists():
        raise Exception('Individual undefined. Create with state.me(name, dob)')
    else:
        with open(config_location) as config:
            config = json.load(config)
        return pydash.get(config, 'uuid')

def statement(triple, home):

    ''' Encrypt rdf triple as meta-triple. '''

    ont = rdflib.Namespace(f'https://{home}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home}.org/resource/')

    single = rdflib.Graph()
    single.add(triple)
    source = str(single.serialize(format='ntriples'))

    enc = encryption_pair()
    fernet = Fernet(base64.urlsafe_b64encode(enc['key'].encode()))

    ttl_file = pathlib.Path.cwd() / 'graph.ttl'
    meta_graph = rdflib.Graph()
    if ttl_file.exists():
        meta_graph.parse(ttl_file)

    meta_graph.add((res[enc['statement']], rdflib.RDF.type, ont['statement'] ))
    meta_graph.add((res[enc['statement']], ont['has_payload'], rdflib.Literal(fernet.encrypt(source.encode()).decode())))
    meta_graph.serialize(destination=str(ttl_file), format="turtle")

def person(name, birth):

    ''' Add an external individual to the graph. '''

    home_uuid = individual()
    ont = rdflib.Namespace(f'https://{home_uuid}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home_uuid}.org/resource/')

    person_uuid = str(uuid.uuid4())

    statement((res[person_uuid], rdflib.RDF.type, ont['person']), home_uuid)
    statement((res[person_uuid], ont['has_name'], rdflib.Literal(name)), home_uuid)
    statement((res[person_uuid], ont['has_birth_date'], rdflib.Literal(birth)), home_uuid)

def decrypt_all():

    ''' Decrypt metagraph. '''

    home_uuid = individual()
    ont = rdflib.Namespace(f'https://{home_uuid}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home_uuid}.org/resource/')

    meta_graph = rdflib.Graph()
    meta_graph.parse(pathlib.Path.cwd() / 'graph.ttl')

    statements = [s for s,p,o in meta_graph.triples((None, None, ont.statement))]

    payloads = list()
    for x in statements:
        statement_id = pathlib.Path(str(x)).stem
        for s,p,o in meta_graph.triples((x, ont['has_payload'], None)):
            payloads.append({statement_id:str(o)})

    config_location = pathlib.Path.cwd() / 'individual.json'
    with open(config_location) as config:
        keys = json.load(config)['keys']

    lower_graph = rdflib.Graph()
    for p in payloads:
        for k,v in p.items():
            fernet = Fernet(base64.urlsafe_b64encode(keys[k].encode()))
            decMessage = fernet.decrypt(v.encode()).decode()
            decode_graph = rdflib.Graph()
            decode_graph.parse(data=decMessage)
            lower_graph += decode_graph

    print(lower_graph.serialize(format='turtle'))
