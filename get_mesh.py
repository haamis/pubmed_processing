"""
Read mesh annotations for each PubMed document
"""
import glob
import sys
import gzip
import xml.etree.ElementTree as ET
import json
import re

def get_mesh(earliest_year, input_file, output_file):

    out_f = open(output_file, 'wt')
    
    root = ET.fromstring(gzip.open(input_file, 'rt').read())
    articles = []
    
    for doc in root.findall('.//PubmedArticle'):
        
        abstract = doc.find('.//Abstract')
        if abstract == None: # Skip articles without abstract.
            #print("abstract skip")
            break

        mesh_list = doc.find('.//MeshHeadingList')
        if mesh_list == None: # Skip articles without mesh terms.
            #print("mesh skip:", mesh_list)
            break

        pub_year_node = doc.find('.//PubDate').find('Year')
        if pub_year_node == None:
            #print("no year node")
            break

        if int(pub_year_node.text) <= earliest_year: # Skip articles that were published before earliest_year.
            #print("bad year", int(pub_year_node.text))
            break

        pub_year = pub_year_node.text

        article = {}
        article['pubmed_id'] = doc.find('.//PMID').text
        
        article['pub_year'] = pub_year

        article["abstract"] = []
        for part in abstract:
            # Regular expression trick to avoid problems with xml tags inside <AbstractText> element.
            reg = re.compile(r"</?AbstractText[\w=\"\s]*>\s*")
            abstract_text = ET.tostring(part, encoding='unicode')
            abstract_text = reg.sub("", abstract_text)
            article['abstract'].append({'text': abstract_text, 'category': part.get('NlmCategory')})
        
        article['mesh_list'] = []
        for mesh in mesh_list:
            desc = mesh.find('DescriptorName')
            mesh_id = desc.get('UI')
            mesh_name = desc.text
            major_topic = desc.get('MajorTopicYN')
            article['mesh_list'].append({'mesh_id':mesh_id, 'mesh_name':mesh_name, 'major_topic':major_topic})
        
        articles.append(article)
    
    if len(articles) > 0:
        json.dump(articles, out_f, indent=2, sort_keys=True)
                
if __name__ == '__main__':
    get_mesh(2013, *sys.argv[1:])