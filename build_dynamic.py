import os
import jinja2
import pickle
import json
from tqdm import tqdm

templateLoader = jinja2.FileSystemLoader(searchpath=".")
templateEnv = jinja2.Environment(loader=templateLoader)

out_dir = "html"

with open("project.json", "r", encoding="utf-8") as f:
    project_data = json.load(f)

with open("data.pickle", "rb") as f:
    data = pickle.load(f)

os.makedirs(out_dir, exist_ok=True)
doc_template = templateEnv.get_template("./templates/dynamic/document.j2")
page_template = templateEnv.get_template("./templates/dynamic/page.j2")
browse_template = templateEnv.get_template("./templates/dynamic/browse.j2")

print("render browse.html")
output_path = os.path.join("html", "browse.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(browse_template.render({"project_data": project_data, "browse_data": data}))


print("building document und page pages")
for x in tqdm(data):
    output_path = os.path.join("html", f'{x["transkribus_id"]}.html')
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc_template.render({"project_data": project_data, "document_data": x}))
    for y in x["pages"]:
        output_path = os.path.join("html", f'{y["page_id"]}.html')
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(
                page_template.render(
                    {
                        "project_data": project_data,
                        "document_data": x,
                        "page_data": y,
                    }
                )
            )
