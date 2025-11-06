# build script to generate resource markdown pages from turtle data.

import pathlib
import rdflib


def build():

    # load graph.

    path = pathlib.Path.cwd() / "data.ttl"
    if not path.exists():
        raise Exception("Path does not exist.")
    g = rdflib.Graph().parse(path)

    # collect primary entities.

    entities = list()
    for e in [
        "http://www.loc.gov/premis/rdf/v3/Event",
        "http://www.loc.gov/premis/rdf/v3/Person",
    ]:
        entities += [s for s,p,o in g.triples((None, rdflib.RDF.type, rdflib.URIRef(e)))]

    # build markdown.

    for e in entities:

        string = ''

        for s,p,o in g.triples((e, rdflib.RDFS.label, None)):
            label = o
        string += '# '+label+'\n\n'

        for s,p,o in g.triples((e, rdflib.RDFS.comment, None)):
            comment = o
        string += comment

        markdown_path = pathlib.Path.cwd() / '/'.join(pathlib.Path(e).parts[2:])
        with open(markdown_path, 'w') as markdown:
            markdown.write(string)

if __name__ == "__main__":
    build()
