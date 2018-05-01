import os
import sys
import csv
# sys.path.append('/Users/rabbal1892/Documents/ISI/FuzzyMatching/rltk')
import rltk


class Classifier:

    def __init__(self):
        self.tk = rltk.init()
        self.model = self.iter1 = self.iter2 = None

        return

    def run(self):
        self.iter1 = self.tk.get_file_iterator("PatentData4_Rahul_Unified copy.txt", type='csv',
                                               id_column='patent_number', delimiter='\t', quoting=csv.QUOTE_NONE)
        self.iter2 = self.tk.get_file_iterator("VentureExpertData copy.csv", type='csv', id_column='VXFirm_ID',
                                               delimiter=",")

        print("Loading Feature Configuration")
        self.tk.load_feature_configuration('feature_config', "feature_config.json")

        self.tk.compute_labeled_features(iter1=self.iter1.copy(), iter2=self.iter2.copy(),
                                         label_path='label.jsonl',
                                         feature_config_name='feature_config',
                                         feature_output_path='labeled_feature.jsonl')

        model = self.tk.train_model(training_path='labeled_feature.jsonl',
                                    classifier='svm')  # , classifier_config={}

        print
        "Q Gram Blocking"
        self.tk.q_gram_blocking(
            iter1=self.iter1.copy(),
            q1=[0],
            q2=[0],
            output_file_path='blocking.jsonl',
            iter2=self.iter2.copy(),
            value_path1="assignee",
            value_path2="Company_Name"
        )

        self.tk.compute_features(iter1=self.iter1.copy(), iter2=self.iter2.copy(),
                                 feature_config_name='feature_config',
                                 feature_output_path='feature.jsonl',
                                 blocking_path='blocking.jsonl')
        self.tk.predict(model, feature_path='feature.jsonl', predict_output_path='predicted.jsonl')

        # print "computing labeled features"
        # self.tk.compute_labeled_features(
        #     iter1=self.iter1.copy(),
        #     iter2=self.iter2.copy(),
        #     label_path=constants.LABEL_JSONL,
        #     feature_config_name='feature_config',
        #     feature_output_path=constants.OUTPUT_LABELED_FEATURE_JSONL
        # )
        #
        # print "Training Model"
        # self.model = self.tk.train_model(training_path=constants.OUTPUT_LABELED_FEATURE_JSONL, classifier='svm')
        # self.tk.dump_model(self.model, 'model.pkl')

        print
        "Q Gram Blocking"
        self.tk.q_gram_blocking(
            iter1=self.iter1.copy(),
            q1=[1],
            q2=[1],
            output_file_path='blocking.jsonl',
            iter2=self.iter2.copy(),
            value_path1="assignee",
            value_path2="Company_Name"
        )

        # self.model = self.tk.load_model('model.pkl')
        # print "computing feature"
        # self.tk.compute_features(
        #     iter1=self.iter1.copy(),
        #     iter2=self.iter2.copy(),
        #     feature_config_name='feature_config',
        #     feature_output_path='feature.jsonl',
        #     blocking_path='blocking2.jsonl'
        # )
        #
        # print "predicting begins"
        # self.tk.predict(self.model, feature_file='feature.jsonl', predict_output_file='predicted.jsonl')
        #
        # print "filtering on the way"
        # self.tk.filter('predicted.jsonl', 'filtered.jsonl')


if __name__ == "__main__":
    classifier = Classifier()
    classifier.run()
