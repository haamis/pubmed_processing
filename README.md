# pubmed_processing

Run:
`ls *.xml.gz | parallel -j <jobs> -m --progress --halt now,fail=1 python3 xml_articles_to_json.py /path/to/json_output/ {}`

then:
`./merge_json.bash /path/to/json_output/*.json > ../complete_output.json`
