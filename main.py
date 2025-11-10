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
        "http://www.loc.gov/premis/rdf/v3/Event", # this needs to be generalised to include all subclasses.
        "http://www.loc.gov/premis/rdf/v3/Person",
        "http://www.loc.gov/premis/rdf/v3/Organization",
        "https://paulduchesne.github.io/personal-premis/ontology/Book",
    ]:
        entities += [s for s,p,o in g.triples((None, rdflib.RDF.type, rdflib.URIRef(e)))]

    for e in entities:
        print(e)

    # build markdown.

    for e in entities:

        # TODO introduce expectation of minimum data here.

        string = ''

        for s,p,o in g.triples((e, rdflib.RDFS.label, None)):
            label = o
        string += '# '+label+'\n\n'

        for s,p,o in g.triples((e, rdflib.RDFS.comment, None)):
            comment = o
        string += comment

        markdown_path = pathlib.Path.cwd() / f'{'/'.join(pathlib.Path(e).parts[3:])}.md'
        markdown_path.parent.mkdir(exist_ok=True)
        with open(markdown_path, 'w') as markdown:
            markdown.write(string)

if __name__ == "__main__":
    build()
