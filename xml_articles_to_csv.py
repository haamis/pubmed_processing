import sys, gzip, csv
#import xml.etree.ElementTree as ET
import lxml.etree as ET
# lxml is about 2x faster, seemingly because of parse().
from os.path import basename, splitext
from tqdm import tqdm

def get_mesh(earliest_year, input_file, output_folder):
    
    with gzip.open(input_file, "rt") as f:
        root = ET.parse(f).getroot()

    articles = []

    for doc in root.findall("PubmedArticle"):
        
        article = []
        
        abstract_node = doc.find(".//Abstract")
        if abstract_node is None: # Skip articles without abstract.
            #print("abstract skip")
            continue
        else:
            abstract_node = abstract_node.findall("AbstractText")
            #print(abstract)

        mesh_list_node = doc.find(".//MeshHeadingList")
        if mesh_list_node is None: # Skip articles without mesh terms.
            #print("mesh skip:", mesh_list)
            continue

        # Add ArticleDate as first choice, then parse PubDate in <JournalIssue>.
        article_date_node = doc.find(".//ArticleDate")
        pub_date_node = doc.find(".//PubDate")

        if article_date_node is None:
            if pub_date_node.find("Year") is None:
                continue
            elif int(pub_date_node.find("Year").text) < earliest_year: # Skip articles that were published before `earliest_year`.
                continue
        elif int(article_date_node.find("Year").text) < earliest_year: # Skip articles that were published before `earliest_year`.
            #print("bad year", int(pub_year_node.text))
            continue

        title = "".join(doc.find(".//ArticleTitle").itertext())

        journal = "".join(doc.find(".//Journal/Title").itertext())

        abstract_parts = []

        for part in abstract_node:
            if part.get("NlmCategory"):
                abstract_parts.append(part.get("NlmCategory") + ": " + "".join(part.itertext()))
            else:
                abstract_parts.append("".join(part.itertext()))
        
        abstract = "".join(abstract_parts)

        article.append(" ".join( (title, journal, abstract) ).replace("\t", "\s"))
        
        mesh_list = []
        for mesh in mesh_list_node:
            desc = mesh.find("DescriptorName")
            mesh_id = desc.get("UI")
            #mesh_name = desc.text
            #major_topic = desc.get("MajorTopicYN")
            mesh_list.append(mesh_id)
        
        article.append(",".join(mesh_list))

        articles.append(article)
    
    if len(articles) > 0:
        with open(output_folder + '/' + splitext(basename(input_file))[0] + ".tsv", "wt") as f:
            cr = csv.writer(f, delimiter="\t")
            cr.writerows(articles)
                
if __name__ == "__main__":
    for arg in tqdm(sys.argv[2:]):
        #print(dirname(sys.argv[1]))
        get_mesh(2013, arg, sys.argv[1])