# PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
# PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
#
# SELECT ?uri ?lod_identifier
# WHERE {
#   GRAPH <http://data.americanartcollaborative.org/puam> {
#       ?uri a crm:E39_Actor;
#         skos:exactMatch ?lod_identifier.
#   }
# }
# query data to queryResult.csv


import csv, json, random


# # generate ulan_puam_exact_match
# with open('ulan_puam_exact_match.jsonl', 'w') as output:
#     with open('queryResults.csv', 'r') as f:
#         csv_reader = csv.DictReader(f, delimiter=',', quotechar='"')
#         for line in csv_reader:
#             j = {}
#             j['ulan_id'] = line[' "lod_identifier" '][2:-2]
#             # fix mal-formatted ulan id
#             if j['ulan_id'].startswith('http://vocab.getty.edu/ulan/http'):
#                 j['ulan_id'] = j['ulan_id'][len('http://vocab.getty.edu/ulan/'):]
#             j['puam_id'] = line[' "uri" '][2:-2]
#             output.write(json.dumps(j))
#             output.write('\n')



# # generate ulan exclude file
# ulan_used = set()
# with open('ulan_puam_exact_match.jsonl', 'r') as f:
#     for line in f:
#         ulan_used.add(json.loads(line)['ulan_id'])
#
# with open('../../datasets/ulan.json', 'r') as f:
#     with open('ulan_exclude.jsonl', 'w') as output:
#         for line in f:
#             j = json.loads(line)
#             if j['uri']['value'] in ulan_used:
#                 continue
#             output.write(line)



# # ulan has totoal 187482 lines
# # ulan_exclude has 186362 lines
# # generate negative paris
# puam = []
# with open('../../datasets/puam.json', 'r') as f:
#     for line in f:
#         puam.append(json.loads(line)['uri']['value'])
#
# ulan_exclude_line_num = 186362
negative_pair_num = 3000
# selected_lines = sorted(random.sample(range(ulan_exclude_line_num), negative_pair_num))
# with open('ulan_puam_not_match.jsonl', 'w') as output:
#     with open('ulan_exclude.jsonl', 'r') as f:
#         idx = 0
#         line_count = 0
#         for line in f:
#             if selected_lines[idx] == line_count:
#                 j = json.loads(line)
#                 j_out = {'puam_id': random.choice(puam), 'ulan_id': j['uri']['value']}
#                 output.write(json.dumps(j_out))
#                 output.write('\n')
#                 idx += 1
#                 if idx == len(selected_lines):
#                     break
#             line_count += 1


# generate labeled data
with open('labeled.jsonl', 'w') as output:
    with open('ulan_puam_exact_match.jsonl', 'r') as match:
        with open('ulan_puam_not_match.jsonl', 'r') as unmatch:
            match_finished, unmatch_finished = False, False
            while not match_finished or not unmatch_finished:
                s = random.randint(0, 1) if not match_finished and not unmatch_finished \
                    else (0 if match_finished else 1)
                j_out = {}
                if s == 1:
                    ss = match.readline()
                    if ss == '' or ss == '\n':
                        match_finished = True
                        continue
                    j = json.loads(ss)
                    j_out = {
                        'id': [j['ulan_id'], j['puam_id']],
                        'label': 1.0
                    }
                else:
                    ss = unmatch.readline()
                    if ss == '' or ss == '\n':
                        unmatch_finished = True
                        continue
                    j = json.loads(ss)
                    j_out = {
                        'id': [j['ulan_id'], j['puam_id']],
                        'label': 0.0
                    }
                output.write(json.dumps(j_out))
                output.write('\n')
