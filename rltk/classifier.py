from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve

# http://scikit-learn.org/stable/modules/classes.html

def get_classifier_class(class_name):
    name_table = {
        'logistic_regression': LogisticRegression,
        'sgd': SGDClassifier,
        'svm': SVC,
        'k_neighbors': KNeighborsClassifier,
        'gaussian_process': GaussianProcessClassifier,
        'decision_tree': DecisionTreeClassifier,
        'extra_tree': ExtraTreeClassifier,
        'random_forest': RandomForestClassifier,
        'ada_boost': AdaBoostClassifier,
        'mlp': MLPClassifier,
        'gaussian_naive_bayes': GaussianNB,
        'quadratic_discriminant_analysis': QuadraticDiscriminantAnalysis
    }

    if class_name not in name_table:
        raise ValueError('No such classifier')

    return name_table[class_name]


def cross_validation(class_name, X, y, classifier_config={}, cv=3, method=None):

    cls = get_classifier_class(class_name)
    clf = cls(**classifier_config)
    y_scores = None

    if method is not None:
        y_scores = cross_val_predict(clf, X, y, cv=cv, method=method)
    elif hasattr(cls, 'decision_function'):
        y_scores = cross_val_predict(clf, X, y, cv=cv, method='decision_function')
    elif hasattr(cls, 'predict_proba'):
        y_scores = cross_val_predict(clf, X, y, cv=cv, method='predict_proba')
        y_scores = y_scores[:, 1]
    else:
        raise Exception('Unknown cross validation method')

    return precision_recall_curve(y, y_scores)
