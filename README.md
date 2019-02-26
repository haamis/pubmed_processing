# pubmed_processing

Run:
`ls *.xml.gz | parallel -j <jobs> --eta python3 xml_articles_to_json.py {} ../json_output/{/.}.json`

then:
`./merge_json.bash ../json_output/*.json > ../complete_output.json`
