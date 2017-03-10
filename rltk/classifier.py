from sklearn import svm as sk_svm

def svm(kwargs):
    return sk_svm.SVC(**kwargs)
