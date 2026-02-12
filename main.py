from flask import Flask, render_template
from flask_frozen import Freezer
import markdown
import pandas
import pathlib
import pydash
import rdflib

def extract_entity(uriref, prop):

    entity = [o for s,p,o in graph.triples((uriref, prop, None))]
    if not len(entity):
        raise Exception(f"{prop} not found for {uriref}.")
    entity = entity[0]    
    entity_label = extract_text(entity, rdflib.RDFS.label)

    return {'entity_link': entity, 'entity_label': entity_label}

def extract_text(uriref, prop):
    text = [o for s,p,o in graph.triples((uriref, prop, None))]
    if not len(text):
        raise Exception(f"{prop} not found for {uriref}.")
    
    return text[0]

# load triples.

graph = rdflib.Graph().parse(pathlib.Path.cwd() / 'public.ttl')
graph += rdflib.Graph().parse(pathlib.Path.cwd() / 'ontology.ttl')

# external ontologies.

graph += rdflib.Graph().parse('http://www.w3.org/2000/01/rdf-schema')
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
    node_array[x]['comment'] = markdown.markdown(extract_text(x, rdflib.RDFS.comment))

# node statements.

extant_props = [rdflib.RDFS.label, rdflib.RDF.type, rdflib.RDFS.comment]
for x in node_array.keys():

    props = [p for s,p,o in graph.triples((x, None, None))]
    props = [p for p in props if p not in extant_props]

    df = pandas.DataFrame(columns=['type', 'property_link', 'property_label', 'entity_link', 'entity_label'])
    for p in sorted(props):
        for a,b,c in graph.triples((x, p, None)):
            if pathlib.Path(p).name == 'wikidataIdentifier':
                df.loc[len(df)] = ['entity', p, extract_text(p, rdflib.RDFS.label), f'https://www.wikidata.org/wiki/{c}', str(c)]
            elif type(c) is rdflib.term.URIRef:
                df.loc[len(df)] = ['entity', p, extract_text(p, rdflib.RDFS.label), c, str(extract_text(c, rdflib.RDFS.label))]
            elif type(c) is rdflib.term.Literal:
                df.loc[len(df)] = ['literal', p, extract_text(p, rdflib.RDFS.label), '', str(c)]
            else:
                raise Exception('Type unknown.')

    df = df.drop_duplicates()
    df.sort_values(by=['property_label', 'entity_label'], key=lambda col: col.str.lower(), inplace=True)
    node_array[x]['statements'] = df.to_dict('records')

# define app.

app = Flask(__name__)

# index page.

@app.route('/')
def index():

    classes = [{'class_link':s} for s,p,o in graph.triples((None, rdflib.RDF.type, rdflib.OWL.Class))]
    for c in classes:
        c['class_label'] = extract_text(c['class_link'], rdflib.RDFS.label)
        instances = [{'entity_link':s} for s,p,o in graph.triples((None, rdflib.RDF.type, c['class_link']))]
        for i in instances:
            i['entity_label'] = extract_text(i['entity_link'], rdflib.RDFS.label)

        c['instances'] = sorted(instances, key=lambda x: x['entity_label'])

    classes = sorted(classes, key=lambda x: x['class_label'])

    return render_template('index.html', data=classes)

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

# transform README to index page.

# with open(pathlib.Path.cwd() / 'README.md') as index_in:
#     index_in = index_in.read()

# with open(pathlib.Path.cwd() / 'templates' / 'index.html', 'w') as index_out:
#     index_out.write(markdown.markdown(index_in))

if __name__ == '__main__':
    freezer.freeze()