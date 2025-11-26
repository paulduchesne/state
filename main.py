from flask import Flask, render_template
from flask_frozen import Freezer
import json
import pathlib
import pydash
import rdflib

def extract_entity(uriref, prop):

    entity = [o for s,p,o in graph.triples((uriref, prop, None))]
    if not len(entity):
        raise Exception(f"{prop} not found for {uriref}.")
    entity = entity[0]    
    entity_label = extract_text(entity, rdflib.RDFS.label)

    return {'entity_link':entity, 'entity_label': entity_label}

def extract_text(uriref, prop):
    text = [o for s,p,o in graph.triples((uriref, prop, None))]
    if not len(text):
        raise Exception(f"{prop} not found for {uriref}.")
    
    return text[0]

# load triples.

graph = rdflib.Graph().parse(pathlib.Path.cwd() / 'data.ttl')
graph += rdflib.Graph().parse(pathlib.Path.cwd() / 'ontology.ttl')

# external ontologies.

graph += rdflib.Graph().parse('http://www.w3.org/2002/07/owl')

# nodes.

nodes = pydash.uniq([s for s,p,o in graph.triples((None, None, None))])
nodes = [x for x in nodes if type(x) is rdflib.term.URIRef]
nodes = [x for x in nodes if 'paulduchesne.github.io' in x]
node_array = {x:dict() for x in nodes}

# node labels.

for x in node_array.keys():
    node_array[x]['label'] = extract_text(x, rdflib.RDFS.label)

# node type.

for x in node_array.keys():
    node_array[x]['type'] = extract_entity(x, rdflib.RDF.type)

# node comment.

for x in node_array.keys():
    node_array[x]['comment'] = extract_text(x, rdflib.RDFS.comment)

# define app.

app = Flask(__name__)

# index page.

@app.route('/')
def index():
    return render_template('index.html')

# resource pages.

@app.route('/resource/<resource>.html')
def resource(resource):

    node = f'https://paulduchesne.github.io/state/resource/{resource}'

    return render_template('resource.html', data=node_array[rdflib.URIRef(node)])

# ontology pages.

@app.route('/ontology/<ontology>.html')
def ontology(ontology):

    node = f'https://paulduchesne.github.io/state/ontology/{ontology}'

    return render_template('ontology.html', data=node_array[rdflib.URIRef(node)])

# flask freezer.

freezer = Freezer(app)

# render pages.

@freezer.register_generator
def resource_generator():  

    for n in node_array.keys():
        for t in ['resource', 'ontology']:
            if t in str(n):
                p = pathlib.Path(n).name
                yield (t, {t: p})

if __name__ == '__main__':
    freezer.freeze()