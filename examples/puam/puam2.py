import rltk
import json

import matplotlib
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, precision_recall_curve
from rltk.classifier import get_classifier_class

tk = rltk.init()

iter1 = tk.get_file_iterator('../../datasets/ulan.json', type='json_line', id_path='uri[*].value')
iter2 = tk.get_file_iterator('../../datasets/puam.json', type='json_line', id_path='uri[*].value')

fig = plt.figure(1, figsize=(15, 10))
fig.suptitle('Precision vs Recall')

for i in xrange(1, 4):
    print 'step: ', i
    # tk.load_feature_configuration('feature_config' + str(i), 'feature_config' + str(i) + '.json')
    # tk.compute_labeled_features(iter1=iter1.copy(), iter2=iter2.copy(),
    #                     label_path='labeled_500.jsonl',
    #                     feature_config_name='feature_config' + str(i),
    #                     feature_output_path='labeled_500_feature' + str(i) + '.jsonl')

    X, y = [], []
    with open('labeled_500_feature' + str(i) + '.jsonl', 'r') as f:
        for line in f:
            j = json.loads(line)
            X.append(j['feature_vector'])
            y.append(j['label'])

    clf = get_classifier_class('svm')()
    # y_pred = cross_val_predict(clf, X, y, cv=3)
    # print y
    # print y_pred
    # pr = precision_score(y, y_pred)
    # re = recall_score(y, y_pred)
    # f1 = f1_score(y, y_pred)
    # print pr, re, f1

    y_scores = cross_val_predict(clf, X, y, cv=5, method='decision_function')
    pr, re, th = precision_recall_curve(y, y_scores)
    # print '%s\n%s\n%s' % (pr, re, th)

    plt.subplot(220 + i)
    plt.title('config' + str(i))
    l1 = plt.plot(th, pr[:-1], 'b--', label='Precision')
    l2 = plt.plot(th, re[:-1], 'g-', label='Recall')
    plt.xlabel('Threshold')
    plt.xlim([th[0] - 0.1, th[-1] + 0.1])
    plt.ylim([-0.1, 1.1])
    plt.legend(loc='lower left')
    plt.grid(True)

plt.savefig('figure.png')
plt.show()

    # f = plt.figure()
    # f.plot(range(0,10))
    # f.plot(th, pr[:-1], 'b--', label='Precision')
    # plt.plot(th, re[:-1], 'g-', label='Recall')
    # plt.xlabel('Threshold')
    # plt.ylim([-0.1, 1.1])