
import ansible_vault
import base64 
import hashlib
import json
import pathlib
import pydash
import rdflib
import state
import uuid

def checksummer(file_path):

    ''' Default MD5 checksumming function. '''

    with open(file_path, 'rb') as item:
        hash = hashlib.md5()
        for buff in iter(lambda: item.read(65536), b''):
            hash.update(buff)
        checksum = hash.hexdigest().lower()
        return(checksum)

ident_file = pathlib.Path.cwd().parents[0] / 'person.json'

if not ident_file.exists():
    raise Exception('Ident file not found.')
else:
    with open(ident_file) as ident_uuid:
        ident_uuid = json.load(ident_uuid)
        ident = pydash.get(ident_uuid, 'identifier')

ont = rdflib.Namespace(f'https://{ident}.org/ontology/')
res = rdflib.Namespace(f'https://{ident}.org/resource/')

source_file = input('Add file: ') 
source_file = pathlib.Path(str(source_file.replace("'","").strip()))
if not pathlib.Path(source_file).is_file():
    raise Exception('Not a file.')

file_uuid = str(uuid.uuid4())
file_hash = checksummer(source_file) # ideally check if file already exists
b64_file = open(source_file, 'rb').read() 
b64_file_encode = base64.b64encode(b64_file)

state.format_statement(res[ident], ont.hasFile, ont[file_uuid], ident)
state.format_statement(res[file_uuid], rdflib.RDF.type, ont['file'], file_uuid)
state.format_statement(res[file_uuid], ont.hasHash, rdflib.Literal(file_hash), file_uuid)
state.format_statement(res[file_uuid], ont.hasExtension, rdflib.Literal(source_file.suffix), file_uuid)
state.format_statement(res[file_uuid], ont.hasFilename, rdflib.Literal(source_file), file_uuid)
state.format_statement(res[file_uuid], ont.hasData, rdflib.Literal(b64_file_encode.decode()), file_uuid)
