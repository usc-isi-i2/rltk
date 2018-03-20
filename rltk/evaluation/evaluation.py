from rltk.evaluation.trial import Trial

class Evaluation():
    def __init__(self):
        pass

    def add_trial(self):
        pass

    def false_positives(self, trial: Trial) -> float:
        pass

    def true_positives(self, trial: Trial) -> float:
        pass

    def false_negatives(self, trial: Trial) -> float:
        pass

    def true_negatives(self, trial: Trial) -> float:
        pass

    def precision(self, trial: Trial) -> float:
        pass

    def recall(self, trial: Trial) -> float:
        pass

    def f_measure(self, trial: Trial) -> float:
        pass