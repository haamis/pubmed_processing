"""
Read mesh annotations for each PubMed document
"""
import sys, gzip, json
import xml.etree.ElementTree as ET

def get_mesh(earliest_year, input_file, output_file):
    
    root = ET.parse(gzip.open(input_file, 'rt')).getroot()
    articles = []
    
    for doc in root.findall('.//PubmedArticle'):
        
        abstract = doc.find('.//Abstract')
        if abstract == None: # Skip articles without abstract.
            #print("abstract skip")
            continue
        else:
            abstract = abstract.findall('.//AbstractText')
            #print(abstract)

        mesh_list = doc.find('.//MeshHeadingList')
        if mesh_list == None: # Skip articles without mesh terms.
            #print("mesh skip:", mesh_list)
            continue

        pub_year_node = doc.find('.//PubDate').find('Year')
        if pub_year_node == None:
            #print("no year node")
            continue

        elif int(pub_year_node.text) < earliest_year: # Skip articles that were published before earliest_year.
            #print("bad year", int(pub_year_node.text))
            continue

        article = {}
        article['pubmed_id'] = doc.find('.//PMID').text
        
        article['pub_year'] = pub_year_node.text

        article['title'] = doc.find('.//ArticleTitle').text

        abstract_parts = []

        for part in abstract:
            if part.text == None:
                continue
            if part.get('NlmCategory'):
                abstract_parts.append(part.get('NlmCategory') + ": " + part.text)
            else:
                abstract_parts.append(part.text)
        
        article["abstract"] = "".join(abstract_parts)
        
        article['mesh_list'] = []
        for mesh in mesh_list:
            desc = mesh.find('DescriptorName')
            mesh_id = desc.get('UI')
            mesh_name = desc.text
            major_topic = desc.get('MajorTopicYN')
            article['mesh_list'].append({'mesh_id':mesh_id, 'mesh_name':mesh_name, 'major_topic':major_topic})

        article['author_list'] = []
        for author in doc.findall('.//AuthorList/Author'):
            firstname = author.find('ForeName').text if author.find('ForeName') != None else ""
            lastname = author.find('LastName').text if author.find('LastName') != None else ""
            affiliation = author.find('AffiliationInfo/Affiliation').text if author.find('AffiliationInfo/Affiliation') != None else ""
            article['author_list'].append((firstname, lastname, affiliation))
        
        articles.append(article)
    
    if len(articles) > 0:
        with open(output_file, 'wt') as f:
            json.dump(articles, f, indent=2, sort_keys=True)
                
if __name__ == '__main__':
    get_mesh(2013, sys.argv[1], sys.argv[2])