# build script to generate markdown resources from rdf.

import pandas
import pathlib
import rdflib


def build():

    # load local graph.

    path = pathlib.Path.cwd() / "data.ttl"
    if not path.exists():
        raise Exception("Path does not exist.")
    g = rdflib.Graph().parse(path)

    # merge external ontologies.

    g += rdflib.Graph().parse('https://raw.githubusercontent.com/lcnetdev/PREMIS/refs/heads/master/premis3.owl')
    g += rdflib.Graph().parse('https://www.w3.org/1999/02/22-rdf-syntax-ns')

    # collect primary entities.

    entities = list()
    for e in [
        "http://www.loc.gov/premis/rdf/v3/Event", # this needs to be generalised to include all subclasses.
        "https://paulduchesne.github.io/personal-premis/ontology/ReadingEvent", # ...but, for now.
        "http://www.loc.gov/premis/rdf/v3/Person",
        "http://www.loc.gov/premis/rdf/v3/Organization",
        "https://paulduchesne.github.io/personal-premis/ontology/Book",
    ]:
        entities += [s for s,p,o in g.triples((None, rdflib.RDF.type, rdflib.URIRef(e)))]

    for e in entities:
        print(e)

    # build markdown.

    for e in entities:

        def get_label(graph, uri):
            label = ''
            for s,p,o in graph.triples((uri, rdflib.RDFS.label, None)):
                label = o

            return label

        # print('\n')

        # TODO introduce expectation of minimum data here.

        string = ''

        for s,p,o in g.triples((e, rdflib.RDFS.label, None)):
            label = o
        string += '# '+label+'\n\n'

        for s,p,o in g.triples((e, rdflib.RDFS.comment, None)):
            comment = o
        string += comment

        df = pandas.DataFrame(columns=['property', 'object'])
        for s,p,o in g.triples((e, None, None)):
            if p not in [rdflib.RDFS.label, rdflib.RDFS.comment]:
                df.loc[len(df)] = [p, o]

        # TODO, make sure "type" is top.

        string += '\n\n'
        string += '### Statements\n\n'
        subj = f'[{get_label(g, e)}]({e})'
        for x in df.to_dict('records'):
            prop = f'[{get_label(g, x['property'])}]({x['property']})'
            if type(x['object']) == rdflib.term.Literal:
                obj = x['object']
            elif type(x['object']) == rdflib.term.URIRef:
                obj = f'[{get_label(g, x['object'])}]({x['object']})'
            else:
                raise Exception('Object type unknown.')
            
            string += f'{subj} → {prop} → {obj}    \n'
         



        df = pandas.DataFrame(columns=['subject', 'property'])
        for s,p,o in g.triples((None, None, e)):
            if p not in [rdflib.RDFS.label, rdflib.RDFS.comment]:
                df.loc[len(df)] = [s, p]

        # TODO, make sure "type" is top.

        string += '\n\n'
        string += '### Inverse Statements\n\n'
        obj = f'[{get_label(g, e)}]({e})'
        for x in df.to_dict('records'):
            prop = f'[{get_label(g, x['property'])}]({x['property']})'
            subj = f'[{get_label(g, x['subject'])}]({x['subject']})'
            # if type(x['object']) == rdflib.term.Literal:
            #     obj = x['object']
            # elif type(x['object']) == rdflib.term.URIRef:
            #     obj = f'[{get_label(g, x['object'])}]({x['object']})'
            # else:
            #     raise Exception('Object type unknown.')
            
            string += f'{subj} → {prop} → {obj}    \n'
         



         

        markdown_path = pathlib.Path.cwd() / f'{'/'.join(pathlib.Path(e).parts[3:])}.md'
        markdown_path.parent.mkdir(exist_ok=True)
        with open(markdown_path, 'w') as markdown:
            markdown.write(string)

if __name__ == "__main__":
    build()
