from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

def get_classifier_class(class_name):
    name_table = {
        'svm': SVC,
        'k_neighbors': KNeighborsClassifier,
        'gaussian_process': GaussianProcessClassifier,
        'decision_tree': DecisionTreeClassifier,
        'random_forest': RandomForestClassifier,
        'ada_boost': AdaBoostClassifier,
        'mlp': MLPClassifier,
        'gaussian_naive_bayes': GaussianNB,
        'quadratic_discriminant_analysis': QuadraticDiscriminantAnalysis
    }

    if class_name not in name_table:
        raise ValueError('No such classifier')

    return name_table[class_name]
