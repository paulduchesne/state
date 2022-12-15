from cryptography.fernet import Fernet
import base64
import hashlib
import json
import os
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

def checksummer(file_path):

    ''' Default MD5 checksumming function. '''

    with open(file_path, 'rb') as item:
        hash = hashlib.md5()
        for buff in iter(lambda: item.read(65536), b''):
            hash.update(buff)
        checksum = hash.hexdigest().lower()
        return(checksum)

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

    ttl_file = pathlib.Path.cwd() / 'data' / f'{str(uuid.uuid4())[:2]}.ttl'
    ttl_file.parents[0].mkdir(exist_ok=True)
    meta_graph = rdflib.Graph()
    if ttl_file.exists():
        meta_graph.parse(ttl_file)

    meta_graph.add((res[enc['statement']], rdflib.RDF.type, ont['statement'] ))
    meta_graph.add((res[enc['statement']], ont['has_payload'], rdflib.Literal(fernet.encrypt(source.encode()).decode())))
    if triple[1] != ont['has_payload']:
        meta_graph.add((res[enc['statement']], ont['layer'], ont['shallow']))
    else:
        meta_graph.add((res[enc['statement']], ont['layer'], ont['deep']))
    meta_graph.serialize(destination=str(ttl_file), format="turtle")

def person_extant(name, birth):

    ''' Does person likely already exist in graph? '''

    # note that for now this will just be a straight dob match,
    # in the future it would be nice to see fuzzy matching on name as factor.

    home_uuid = individual()
    ont = rdflib.Namespace(f'https://{home_uuid}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home_uuid}.org/resource/')

    extant_graph = decrypt_all()
    person_match = [s for s,p,o in extant_graph.triples((None, ont['has_birth_date'], rdflib.Literal(birth)))]

    return len(person_match)

def person(name, birth):

    ''' Add an external individual to the graph. '''

    # for now silently pass on matching individual.

    if person_extant(name, birth):
        print(f'{name} already exists.')
    else:
        home_uuid = individual()
        ont = rdflib.Namespace(f'https://{home_uuid}.org/ontology/') 
        res = rdflib.Namespace(f'https://{home_uuid}.org/resource/')

        person_uuid = str(uuid.uuid4())

        statement((res[person_uuid], rdflib.RDF.type, ont['person']), home_uuid)
        statement((res[person_uuid], ont['has_name'], rdflib.Literal(name)), home_uuid)
        statement((res[person_uuid], ont['has_birth_date'], rdflib.Literal(birth)), home_uuid)

def file_extant(md5_hash):

    ''' Check if file already exists in the graph. '''

    home_uuid = individual()
    ont = rdflib.Namespace(f'https://{home_uuid}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home_uuid}.org/resource/')

    extant_graph = decrypt_all()
    file_match = [s for s,p,o in extant_graph.triples((None, ont['has_md5_hash'], rdflib.Literal(md5_hash)))]

    return len(file_match)

def file(path):

    ''' Load file into graph. '''

    home_uuid = individual()
    ont = rdflib.Namespace(f'https://{home_uuid}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home_uuid}.org/resource/')

    checksum = checksummer(path)

    if file_extant(checksum):
        print(f'{path.name} already exists.')
    else:
        file_uuid = str(uuid.uuid4())
        with open(str(path), 'rb') as file_data:
            file_data = file_data.read()

        statement((res[file_uuid], rdflib.RDF.type, ont['file']), home_uuid)
        statement((res[file_uuid], ont['has_original_filename'], rdflib.Literal(str(path))), home_uuid)
        statement((res[file_uuid], ont['has_md5_hash'], rdflib.Literal(checksum)), home_uuid)
        statement((res[file_uuid], ont['has_file_size'], rdflib.Literal(os.path.getsize(path))), home_uuid)
        statement((res[file_uuid], ont['has_payload'], rdflib.Literal(base64.b64encode(file_data).decode('utf-8'))), home_uuid)

def decrypt_all():

    ''' Decrypt metagraph. '''

    home_uuid = individual()
    ont = rdflib.Namespace(f'https://{home_uuid}.org/ontology/') 
    res = rdflib.Namespace(f'https://{home_uuid}.org/resource/')

    meta_graph = rdflib.Graph()
    for x in [x for x in (pathlib.Path.cwd() / 'data').iterdir() if x.suffix == '.ttl']:
        meta_graph.parse(x)

    statements = [s for s,p,o in meta_graph.triples((None, None, ont.statement))]
    
    shallow_statements = list()
    for x in statements:
        for s,p,o in meta_graph.triples((x, ont['layer'], ont['shallow'])):
            shallow_statements.append(s)

    payloads = list()
    for x in shallow_statements:
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

    # print(lower_graph.serialize(format='turtle'))

    return lower_graph
