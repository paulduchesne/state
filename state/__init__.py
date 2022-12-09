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

    config_location = pathlib.Path.home() / 'individual.json'
    with open(config_location) as config:
        config = json.load(config)

    pull_keys = config['keys']
    pull_keys.append({statement_uuid: key_uuid})
    config['keys'] = pull_keys

    with open(config_location, 'w') as config_out:
        json.dump(config, config_out)

    return {'statement':statement_uuid, 'key':key_uuid}

def me(name, birth):

    ''' Define individual. '''
    
    config_location = pathlib.Path.home() / 'individual.json'
    if config_location.exists():
        print('Individual already defined.')
    else:
        individual = {"uuid":str(uuid.uuid4()), "name":name, "birth":birth, "keys":[]}
        with open(config_location, 'w') as config:
            json.dump(individual, config)

def individual():

    ''' Retrieve state config file. '''

    config_location = pathlib.Path.home() / 'individual.json'
    if not config_location.exists():
        raise Exception('Individual undefined. Create with state.me(name, dob)')
    else:
        with open(config_location) as config:
            config = json.load(config)
        return pydash.get(config, 'uuid')

def statement(triple, home):

    ''' Encrypt rdf triple as meta-triple. '''

    enc = encryption_pair()
    ont = rdflib.Namespace(f'https://{home}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home}.org/resource/')

    single = rdflib.Graph()
    single.add(triple)
    source = str(single.serialize(format='ntriples'))

    fernet = Fernet(base64.urlsafe_b64encode(enc['key'].encode()))

    meta_graph = rdflib.Graph()
    meta_graph.add((res[enc['statement']], rdflib.RDF.type, ont['statement'] ))
    meta_graph.add((res[enc['statement']], ont['has_payload'], rdflib.Literal(fernet.encrypt(source.encode()).decode())))

    print(meta_graph.serialize(format='turtle'))

    # this needs to be appended to local turtle file.

def person(name, birth):

    ''' Add an external individual to the graph. '''

    home_uuid = individual()
    ont = rdflib.Namespace(f'https://{home_uuid}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home_uuid}.org/resource/')

    person_uuid = str(uuid.uuid4())

    statement((res[person_uuid], rdflib.RDF.type, ont['person']), home_uuid)
    statement((res[person_uuid], ont['has_name'], rdflib.Literal(name)), home_uuid)
    statement((res[person_uuid], ont['has_birth_date'], rdflib.Literal(birth)), home_uuid)

# decMessage = fernet.decrypt(encMessage.encode()).decode()
# print(decMessage)
