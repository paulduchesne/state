from flask import Flask, render_template
from flask_frozen import Freezer
import json
import pathlib
import rdflib

# load triples.

graph = rdflib.Graph().parse(pathlib.Path.cwd() / 'data.ttl')

# define app.

app = Flask(__name__)

# index page.

@app.route('/')
def index():
    return render_template('index.html')

# resource page.

@app.route('/resource/<resource>.html')
def resource(resource):

    entity_uri = f'https://paulduchesne.github.io/personal-premis/resource/{resource}'
    entity_graph = rdflib.Graph()
    for s,p,o in graph.triples((rdflib.URIRef(entity_uri), None, None)):
        entity_graph.add((s,p,o))

    entity_graph = entity_graph.serialize(format='json-ld')
    return render_template('resource.html', data=json.loads(entity_graph), blab=entity_graph)

# flask freezer.

freezer = Freezer(app)

# register iterations of resources.
# this could actually be auto-parsed from all uris which feature "resource".

@freezer.register_generator
def resource_generator():  
    people = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('http://www.loc.gov/premis/rdf/v3/Person')))]
    for p in people:
        p = pathlib.Path(p).name
        yield ('resource', {'resource': p})

    org = [s for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.URIRef('http://www.loc.gov/premis/rdf/v3/Organization')))]
    for p in org:
        p = pathlib.Path(p).name
        yield ('resource', {'resource': p})

if __name__ == '__main__':
    freezer.freeze()