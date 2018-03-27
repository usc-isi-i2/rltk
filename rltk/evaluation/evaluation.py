from rltk.evaluation.trial import Trial


class Evaluation():
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    def __init__(self):
        pass

    def add_trial(self, trial: Trial):
        self.tp, self.tn, self.fp, self.fn = self.__statistics_trial(trial)

    # def false_positives(self, trial: Trial) -> float:
    #     tp, tn, fp, fn = self.__statistics_trial(trial)
    #     return fp / (fp + tn)
    #
    # def true_positives(self, trial: Trial) -> float:
    #     tp, tn, fp, fn = self.__statistics_trial(trial)
    #     return tp / (tp + fn)
    #
    # def false_negatives(self, trial: Trial) -> float:
    #     tp, tn, fp, fn = self.__statistics_trial(trial)
    #     return fp / (tp + fn)
    #
    # def true_negatives(self, trial: Trial) -> float:
    #     tp, tn, fp, fn = self.__statistics_trial(trial)
    #     return tn / (fp + tn)

    def precision(self, trial: Trial) -> float:
        pass

    def recall(self, trial: Trial) -> float:
        pass

    def f_measure(self, trial: Trial) -> float:
        pass

    def false_positives(self) -> float:
        if (self.fp + self.tn) == 0:
            return 0
        return self.fp / (self.fp + self.tn)

    def true_positives(self) -> float:
        if (self.tp + self.fn) == 0:
            return 0
        return self.tp / (self.tp + self.fn)

    def false_negatives(self) -> float:
        if (self.tp + self.fn) == 0:
            return 0
        return self.fp / (self.tp + self.fn)

    def true_negatives(self) -> float:
        if (self.fp + self.tn) == 0:
            return 0
        return self.tn / (self.fp + self.tn)

    def __statistics_trial(self, trial: Trial):
        fp = 0
        fn = 0
        tp = 0
        tn = 0
        ground_truth = trial.get_ground_truth()

        for trial_result in trial.get_all_data():
            gt_val = ground_truth.is_positive(trial_result.record1, trial_result.record2)
            cal_val = trial_result.is_positive

            if cal_val and gt_val:
                tp += 1
            elif not cal_val and not gt_val:
                tn += 1
            elif cal_val and not gt_val:
                fp += 1
            elif not cal_val and gt_val:
                fn += 1

        return tp, tn, fp, fn
