import sys, gzip, json
#import xml.etree.ElementTree as ET
import lxml.etree as ET
# lxml is about 2x faster, seemingly because of parse().
from os.path import basename, dirname, splitext
from tqdm import tqdm

def get_mesh(earliest_year, input_file, output_folder):
    
    with gzip.open(input_file, "rt") as f:
        root = ET.parse(f).getroot()

    articles = []

    for doc in root.findall("PubmedArticle"):
        
        article = {}
        
        abstract = doc.find(".//Abstract")
        if abstract is None: # Skip articles without abstract.
            #print("abstract skip")
            continue
        else:
            abstract = abstract.findall("AbstractText")
            #print(abstract)

        mesh_list = doc.find(".//MeshHeadingList")
        if mesh_list is None: # Skip articles without mesh terms.
            #print("mesh skip:", mesh_list)
            continue

        # Add ArticleDate as first choice, then parse PubDate in <JournalIssue>.
        pub_date_node = doc.find(".//PubDate")
        # if pub_date_node.find("Year") is None:
        #     print("wat", pub_date_node.find("MedlineDate").text)
        
        article_date_node = doc.find(".//ArticleDate")

        if article_date_node is None:
            if pub_date_node.find("Year") is None:
                continue

            elif int(pub_date_node.find("Year").text) < earliest_year: # Skip articles that were published before `earliest_year`.
                continue

            else:
                article["pub_year"] = pub_date_node.find("Year").text

        elif int(article_date_node.find("Year").text) < earliest_year: # Skip articles that were published before `earliest_year`.
            #print("bad year", int(pub_year_node.text))
            continue

        else:
            article["pub_year"] = article_date_node.find("Year").text

        article["pubmed_id"] = doc.find(".//PMID").text

        article["title"] = "".join(doc.find(".//ArticleTitle").itertext())

        article["journal"] = "".join(doc.find(".//Journal/Title").itertext())

        abstract_parts = []

        for part in abstract:
            if part.get("NlmCategory"):
                abstract_parts.append(part.get("NlmCategory") + ": " + "".join(part.itertext()))
            else:
                abstract_parts.append("".join(part.itertext()))
        
        article["abstract"] = "".join(abstract_parts)
        
        article["mesh_list"] = []
        for mesh in mesh_list:
            desc = mesh.find("DescriptorName")
            mesh_id = desc.get("UI")
            mesh_name = desc.text
            major_topic = desc.get("MajorTopicYN")
            article["mesh_list"].append({"mesh_id":mesh_id, "mesh_name":mesh_name, "major_topic":major_topic})

        article["author_list"] = []
        last_affiliations = ""
        for author in doc.findall(".//AuthorList/Author"):
            if author.find("LastName") is not None:
                lastname = author.find("LastName").text
                if author.find("ForeName") is not None:
                    firstname = author.find("ForeName").text
                else:
                    firstname = ""
            elif author.find("CollectiveName") is not None:
                lastname = author.find("CollectiveName").text
                firstname = "Collective"
            else:
                # Debug.
                print("Debug print", author.find("ForeName"), author.find("LastName"), author.find("CollectiveName"))
                continue
            
            aff_nodes = author.findall("AffiliationInfo/Affiliation")

            # In case of no affiliation info, assume the affiliation of an earlier author in the article info.
            if len(aff_nodes) == 0:
                affiliations = last_affiliations
            else:
                affiliations = [aff.text for aff in aff_nodes]
                last_affiliations = affiliations

            article["author_list"].append( (firstname, lastname, "; ".join(affiliations)) )
        
        articles.append(article)
    
    if len(articles) > 0:
        with open(output_folder + '/' + splitext(basename(input_file))[0] + ".json", "wt") as f:
            json.dump(articles, f, indent=2, sort_keys=True)
                
if __name__ == "__main__":
    for arg in tqdm(sys.argv[2:]):
        get_mesh(2013, arg, dirname(sys.argv[1]))