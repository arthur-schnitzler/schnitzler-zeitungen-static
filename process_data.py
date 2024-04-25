import glob
import os
import pickle
import json

from acdh_xml_pyutils.xml import NSMAP as nsmap
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext
from tqdm import tqdm

from utils import get_id_and_title, gsheet_to_df, process_pmb_ids


print("data crunching")
sheet_id = "1FyPgOydzc95Pk-2e9qj3xNevg9ZbcwaMZEglepdrVBk"

df = gsheet_to_df(sheet_id)
files = sorted(glob.glob("exports/*/metadata.xml"))
df = df.set_index("TranskribusDocId")
df.to_csv("hansi.csv")
lookup_dict = df.to_dict("index")
with open("hansi.json", "w") as f:
    json.dump(lookup_dict, f)
data = []
for doc_i, x in tqdm(enumerate(files), total=len(files)):
    heads, tail = os.path.split(x)
    item = {}
    try:
        next_doc = TeiReader(files[doc_i + 1])
        title_str = next_doc.any_xpath(".//title")[0].text
        item["next_doc_title"] = get_id_and_title(title_str)[1]
        item["next_doc_id"] = int(next_doc.any_xpath("//docId")[0].text)
    except IndexError:
        item["next_doc_id"] = None
        item["next_doc_title"] = None
    if doc_i > 0:
        prev_doc = TeiReader(files[doc_i - 1])
        title_str = prev_doc.any_xpath(".//title")[0].text
        item["prev_doc_title"] = get_id_and_title(title_str)[1]
        item["prev_doc_id"] = int(prev_doc.any_xpath("//docId")[0].text)
    else:
        item["prev_doc_id"] = None
        item["prev_doc_title"] = None
    doc = TeiReader(x)
    title_str = doc.any_xpath(".//title")[0].text
    item["doc_id"], item["title"] = get_id_and_title(title_str)
    item["nr_of_pages"] = int(doc.any_xpath(".//nrOfPages")[0].text)
    item["transkribus_id"] = int(doc.any_xpath("//docId")[0].text)
    try:
        item["metadata"] = lookup_dict[item["transkribus_id"]]
    except KeyError:
        item["metadata"] = {}
        print(f'no match for doc {x} with {item["transkribus_id"]}')
    if item["metadata"]:
        md = item["metadata"]
        quote = f'{md["Mappe"]}, {md["Mappentitel"]} {md["Ordner"]}, {md["Unterordner2"]}, {md["Inhalt"]}'
        item["quote"] = quote.replace("nan", "").replace(" ,", ","). replace(",,", ",")
        print(item["quote"])
        item["pmb_tuples"] = process_pmb_ids(item["metadata"]["PMB"])
    pages = sorted(glob.glob(f"{heads}/page/*.xml"))
    item["pages"] = []
    for i, x in enumerate(pages, start=1):
        doc = TeiReader(x)
        heads, tail = os.path.split(x)
        page = {}
        page["page_nr"] = i
        page["page_id"] = tail.replace(".xml", "")
        page["transkribus_image_url"] = doc.tree.xpath(
            ".//page:TranskribusMetadata/@imgUrl", namespaces=nsmap
        )[0]
        try:
            page["next_page"] = os.path.split(pages[i])[-1].replace(".xml", "")
        except IndexError:
            page["next_page"] = None
        if i == 1:
            page["prev_page"] = None
        else:
            page["prev_page"] = os.path.split(pages[i - 2])[-1].replace(".xml", "")
        lines = doc.tree.xpath("//page:TextLine", namespaces=nsmap)
        line_objects = []
        for x in lines:
            line = {}
            line["id"] = x.attrib["id"]
            line["text"] = extract_fulltext(x)
            line_objects.append(line)
        page["lines"] = line_objects
        item["pages"].append(page)
    data.append(item)

print("writing temp files")
with open("data.pickle", "wb") as fp:
    pickle.dump(sorted(data, key=lambda x: x["doc_id"]), fp, protocol=pickle.HIGHEST_PROTOCOL)
with open("data.json", "w", encoding="utf-8") as fp:
    json.dump(sorted(data, key=lambda x: x["doc_id"]), fp, ensure_ascii=False, indent=2)

print("done with data processing")
