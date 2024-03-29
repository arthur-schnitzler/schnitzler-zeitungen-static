import glob
import os
from tqdm import tqdm
from acdh_tei_pyutils.tei import TeiReader
from acdh_xml_pyutils.xml import NSMAP
from rdflib import Namespace, URIRef, RDF, Graph, Literal


g = Graph().parse("arche_seed_files/arche_constants.ttl")
g_repo_objects = Graph().parse("arche_seed_files/repo_objects_constants.ttl")
TOP_COL_URI = URIRef("https://id.acdh.oeaw.ac.at/schnitzler-zeitungen")

ACDH = Namespace("https://vocabs.acdh.oeaw.ac.at/schema#")
COLS = [ACDH["TopCollection"], ACDH["Collection"], ACDH["Resource"]]
COL_URIS = set()


files = glob.glob("exports/*/mets.xml")
for x in tqdm(files[:3]):
    heads, _ = os.path.split(x)
    # document collection
    cur_col_id = x.split("/")[1]
    cur_col_uri = URIRef(f"{TOP_COL_URI}/{cur_col_id}")
    g.add((cur_col_uri, RDF.type, ACDH["Collection"]))
    g.add((cur_col_uri, ACDH["isPartOf"], TOP_COL_URI))

    # mets file
    mets = URIRef(f"{cur_col_uri}/mets.xml")
    g.add((mets, RDF.type, ACDH["Resource"]))
    g.add((mets, ACDH["isPartOf"], cur_col_uri))
    g.add((mets, ACDH["hasTitle"], Literal("mets.xml", lang="und")))
    g.add(
        (
            mets,
            ACDH["hasCategory"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/model"),
        )
    )

    # parse mets file to extract image-uris and document title
    doc = TeiReader(x)
    cur_col_title = doc.tree.xpath(".//title/text()")[0]
    g.add((cur_col_uri, ACDH["hasTitle"], Literal(cur_col_title, lang="und")))
    for i, image in enumerate(
        doc.tree.xpath(
            ".//mets:fileGrp[@ID='IMG']/mets:file/mets:FLocat/@xlink:href",
            namespaces=NSMAP,
        ),
        start=1,
    ):
        image_uri = URIRef(f"{cur_col_uri}/{image}")
        g.add((image_uri, RDF.type, ACDH["Resource"]))
        g.add((image_uri, ACDH["hasTitle"], Literal(f"{cur_col_title}, Seite: {i:04}", lang="de")))
        g.add((image_uri, ACDH["isPartOf"], cur_col_uri))
        g.add(
            (
                image_uri,
                ACDH["hasCategory"],
                URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/image"),
            )
        )
    # page folder
    page_folder_uri = URIRef(f"{cur_col_uri}/page")
    g.add((page_folder_uri, RDF.type, ACDH["Collection"]))
    g.add((page_folder_uri, ACDH["isPartOf"], cur_col_uri))
    g.add(
        (
            page_folder_uri,
            ACDH["hasTitle"],
            Literal(f"PAGE files für: {cur_col_title}", lang="und"),
        )
    )

    # page files
    page_files = glob.glob(f"{heads}/page/*.xml")
    for y in page_files:
        _, tail = os.path.split(y)
        page_file_uri = URIRef(f"{page_folder_uri}/{tail}")
        g.add((page_file_uri, RDF.type, ACDH["Resource"]))
        g.add((page_file_uri, ACDH["isPartOf"], page_folder_uri))
        g.add((page_file_uri, ACDH["hasTitle"], Literal(tail, lang="und")))
        g.add(
            (
                page_file_uri,
                ACDH["hasCategory"],
                URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/model"),
            )
        )


for x in COLS:
    for s in g.subjects(None, x):
        COL_URIS.add(s)

for x in COL_URIS:
    for p, o in g_repo_objects.predicate_objects():
        g.add((x, p, o))

print("writing graph to file")
g.serialize("arche.ttl")
