import pickle

from typesense.api_call import ObjectNotFound
from acdh_cfts_pyutils import TYPESENSE_CLIENT as client
from acdh_cfts_pyutils import CFTS_COLLECTION
from tqdm import tqdm


collection_name = "Schnitzler-Zeitungen"


with open("data.pickle", "rb") as f:
    data = pickle.load(f)


try:
    client.collections[collection_name].delete()
except ObjectNotFound:
    pass

current_schema = {
    "name": collection_name,
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "rec_id", "type": "string", "sort": True},
        {"name": "title", "type": "string"},
        {"name": "full_text", "type": "string"},
        {"name": "document", "type": "string", "facet": True},
    ],
}

client.collections.create(current_schema)

records = []
cfts_records = []
print("collecting data for fulltext search index")
for x in tqdm(data, total=len(data)):
    for y in x["pages"]:
        cfts_record = {
            "project": collection_name,
        }
        record = {}
        record["id"] = y["page_id"]
        record["rec_id"] = f'{y["page_id"]}.html'
        record["title"] = f'{x["title"]}, Seite {y["page_nr"]}'
        record["document"] = x["title"]

        cfts_record["id"] = record["id"]
        cfts_record["resolver"] = (
            f"https://schnitzler-zeitungen.acdh.oeaw.ac.at/{record['id']}.html"
        )
        cfts_record["rec_id"] = record["rec_id"]
        cfts_record["title"] = record["title"]

        record["full_text"] = " ".join([a["text"] for a in y["lines"]])
        cfts_record["full_text"] = record["full_text"]
        records.append(record)
        cfts_records.append(cfts_record)

print("populating index")
make_index = client.collections[collection_name].documents.import_(records)
print(make_index)
print(f"done with indexing {collection_name}")

make_index = CFTS_COLLECTION.documents.import_(cfts_records, {"action": "upsert"})
print(make_index)
print("done with cfts-index {collection_name}")
