import ansible_vault
import pathlib
import rdflib

path = pathlib.Path.home() / 'git'  / 'state' 

keys = path / 'keys.nt'
key_graph = rdflib.Graph()
key_graph.parse(path / 'keys.nt')

reassemble = rdflib.Graph()

data_path = path / 'data'
for x in data_path.iterdir():

    enc_data = rdflib.Graph()
    enc_data.parse(x)

    for s,p,o in enc_data.triples((None, None, None )):
        if 'Payload' in str(p):
            for a,b,c in key_graph.triples((s, None, None)):
                fragment = rdflib.Graph()
                unlock = ansible_vault.Vault(c).load_raw(o).decode()
                fragment.parse(data=unlock)
                reassemble += fragment

print(reassemble.serialize(format='ttl'))