
# validate inverse properties.

import pathlib
import pydash
import rdflib

def raise_exception(s,p,o):
    s_name = pathlib.Path(s).name
    p_name = pathlib.Path(p).name
    o_name = pathlib.Path(o).name
    raise Exception(f'Inverse of {s_name} {p_name} {o_name} not found.')

# load ontology.

ontology_path = pathlib.Path.cwd().parent / 'ontology.ttl'
if not ontology_path.exists():
    raise Exception('File not found.')
ontology = rdflib.Graph().parse(ontology_path)

# detect inverse properties.

inverse_pairs = list()
for s,p,o in ontology.triples((None, rdflib.RDF.type, rdflib.OWL.ObjectProperty)):
    for a,b,c in ontology.triples((s, rdflib.OWL.inverseOf, None)):
        inverse_pairs.append(sorted([s, c]))
        
inverse_pairs = pydash.uniq(inverse_pairs)

# load data.

data_path = pathlib.Path.cwd().parent / 'data.ttl'
if not data_path.exists():
    raise Exception('File not found.')
data = rdflib.Graph().parse(data_path)


for props in inverse_pairs:
    for s,p,o in data.triples((None, props[0], None)):
        inverse = [(a,b,c) for a,b,c in data.triples((o, props[1], s))]
        if len(inverse) != 1:
            raise_exception(s,p,o)
            
    for s,p,o in data.triples((None, props[1], None)):
        inverse = [(a,b,c) for a,b,c in data.triples((o, props[0], s))]
        if len(inverse) != 1:
            raise_exception(s,p,o)
            

