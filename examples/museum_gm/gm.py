import json
import rltk

tk = rltk.init()
tk.load_feature_configuration('C', 'feature_config.json')

# blocking data
ulan = [
    {"byear": {"datatype": "http://www.w3.org/2001/XMLSchema#gYear", "type": "literal", "value": "1864"}, "uri": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500009086"}, "name": {"type": "literal", "value": "Russell, Charles Marion"}},
    {"byear": {"datatype": "http://www.w3.org/2001/XMLSchema#gYear", "type": "literal", "value": "1859"}, "uri": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500019643"}, "name": {"type": "literal", "value": "Sharp, Joseph Henry"}},
    {"byear": {"datatype": "http://www.w3.org/2001/XMLSchema#gYear", "type": "literal", "value": "1876"}, "uri": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500012516"}, "name": {"type": "literal", "value": "Leighton, Kathryn Woodman"}}
]
museum = [
    {"byear": {"type": "literal", "value": "1864"},
     "uri": {"type": "uri", "value": "http://data.americanartcollaborative.org/GM/constituent/charles_marion_russell"},
     "name": {"type": "literal", "value": "Charles Marion Russell"}},
    {"byear": {"type": "literal", "value": "1859"},
     "uri": {"type": "uri", "value": "http://data.americanartcollaborative.org/GM/constituent/henry_joseph_sharp"},
     "name": {"type": "literal", "value": "Joseph Henry Sharp"}},
    {"byear": {"type": "literal", "value": "1876"},
     "uri": {"type": "uri", "value": "http://data.americanartcollaborative.org/GM/constituent/kathryn_leighton_woodman"},
     "name": {"type": "literal", "value": "Kathryn Woodman Leighton"}}
]

# compute feature vector
with open('feature_vector.jsonl', 'w') as f:
    for u in ulan:
        for m in museum:
            v = tk.compute_feature_vector(u, m, name='C')
            f.write(json.dumps(v))
            f.write('\n')

# featurize ground truth
# tk.featurize_ground_truth('feature_vector.jsonl', 'ground_truth.jsonl')
tk.featurize_ground_truth('feature_vector.jsonl', 'ground_truth.jsonl', 'featurized.jsonl')

# build model
featurized_ground_truth = []
with open('featurized.jsonl', 'r') as f:
    for line in f:
        featurized_ground_truth.append(json.loads(line))
model = tk.train_classifier(featurized_ground_truth, config={'function': 'k_neighbors'})


# blocking data for prediction
ulan2 = [
    {"byear": {"datatype": "http://www.w3.org/2001/XMLSchema#gYear", "type": "literal", "value": "1796"},
     "uri": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500004854"},
     "name": {"type": "literal", "value": "Catlin, George"}},
    {"byear": {"datatype": "http://www.w3.org/2001/XMLSchema#gYear", "type": "literal", "value": "1898"},
     "uri": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500007030"},
     "name": {"type": "literal", "value": "Hogue, Alexandre"}},
    {"byear": {"datatype": "http://www.w3.org/2001/XMLSchema#gYear", "type": "literal", "value": "1796"},
     "uri": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500026080"},
     "name": {"type": "literal", "value": "Durand, Asher Brown"}}
]
museum2 = [
    {"byear": {"type": "literal", "value": "1796"},
     "uri": {"type": "uri", "value": "http://data.americanartcollaborative.org/GM/constituent/catlin_george"},
     "name": {"type": "literal", "value": "George Catlin"}},
    {"byear": {"type": "literal", "value": "1898"},
     "uri": {"type": "uri", "value": "http://data.americanartcollaborative.org/GM/constituent/alexandre_hogue"},
     "name": {"type": "literal", "value": "Alexandre Hogue"}},
    {"byear": {"type": "literal", "value": "1796"},
     "uri": {"type": "uri", "value": "http://data.americanartcollaborative.org/GM/constituent/asher_brown_durand"},
     "name": {"type": "literal", "value": "Asher Brown Durand"}}
]

# compute feature vector & prediction
for u in ulan2:
    for m in museum2:
        v = tk.compute_feature_vector(u, m, name='C')
        print v['id'][0], v['id'][1], v['feature_vector'], model.predict([v['feature_vector']])

# result
# http://vocab.getty.edu/ulan/500004854 http://data.americanartcollaborative.org/GM/constituent/catlin_george [0.6666666666666666] [ 1.]
# http://vocab.getty.edu/ulan/500004854 http://data.americanartcollaborative.org/GM/constituent/alexandre_hogue [0.39999999999999997] [ 0.]
# http://vocab.getty.edu/ulan/500004854 http://data.americanartcollaborative.org/GM/constituent/asher_brown_durand [0.37777777777777777] [ 0.]
# http://vocab.getty.edu/ulan/500007030 http://data.americanartcollaborative.org/GM/constituent/catlin_george [0.39999999999999997] [ 0.]
# http://vocab.getty.edu/ulan/500007030 http://data.americanartcollaborative.org/GM/constituent/alexandre_hogue [0.6666666666666666] [ 1.]
# http://vocab.getty.edu/ulan/500007030 http://data.americanartcollaborative.org/GM/constituent/asher_brown_durand [0.4037037037037037] [ 0.]
# http://vocab.getty.edu/ulan/500026080 http://data.americanartcollaborative.org/GM/constituent/catlin_george [0.2833333333333333] [ 0.]
# http://vocab.getty.edu/ulan/500026080 http://data.americanartcollaborative.org/GM/constituent/alexandre_hogue [0.30277777777777776] [ 0.]
# http://vocab.getty.edu/ulan/500026080 http://data.americanartcollaborative.org/GM/constituent/asher_brown_durand [0.75] [ 1.]