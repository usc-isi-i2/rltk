import json
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')
packagePath = '/Users/yuanli/GitHub/ISI/rltk'
inputPath = '/Users/yuanli/GitHub/ISI/HitiJsonInput/'
# inputPath='ll_nepal/'
# outputPath='output/'
outputPath = '/Users/yuanli/rltk/HitiJsonOutput/'
#sys.path.append(packagePath)
from rltk import rltk

tk = rltk.init()
topicWords = []
thr = 0.8


def pickTopicWords(data, tp, file):
    if data['_source'].has_key(tp):
        for d in data['_source'][tp]:
            haveName = 0
            for ele in range(len(topicWords)):
                if topicWords[ele]['type'] == tp:
                    for n in range(len(topicWords[ele]['originalNames'])):
                        if topicWords[ele]['originalNames'][n]['name'] == d:
                            topicWords[ele]['originalNames'][n]['docIds'].append(file)
                            haveName = 1
                    for n in range(len(topicWords[ele]['originalNames'])):
                        if haveName == 0:
                            similarity = tk.jaccard_index_similarity(
                                set(topicWords[ele]['originalNames'][n]['name'].split(' ')), set(d.split(' ')))
                            if similarity >= thr:
                                haveName = 1
                                obj = {
                                    'name': d,
                                    'docIds': [file]
                                }
                                topicWords[ele]['originalNames'].append(obj)
                                if len(d) > len(topicWords[ele]['preferredName']):
                                    topicWords[ele]['preferredName'] = d
            if haveName == 0:
                obj = {
                    "preferredName": d,
                    "type": tp,
                    "originalNames": [
                        {
                            "name": d,
                            "docIds": [file]
                        }
                    ]
                }
                topicWords.append(obj)


files = os.listdir(inputPath)
for f in files:
    input = open(inputPath + f)
    data = input.read()
    data = json.loads(data)
    pickTopicWords(data, 'PER', f)
    pickTopicWords(data, 'ORG', f)
    pickTopicWords(data, 'GPE', f)
    pickTopicWords(data, 'LOC', f)
for t in topicWords:
    # print t
    newData = json.dumps(t)
    ouputFile = outputPath + t['preferredName'].replace('.json', '').replace('/', '').encode('utf-8') + '_' + t[
        'type'].encode('utf-8') + '.json'
    output = open(ouputFile, 'w')
    output.write(newData)
    output.close()
