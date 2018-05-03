from rltk.evaluation.trial import Trial


class Evaluation():
    '''
    Evaluation compares the result of the trial and the ground truth (stored in trial),
    count and store the number of true positive, true negative, false positive, false negative.

    It can then provide the statistics of:
        true positive, true negative, false positive, false negative, f_measure, precision, false_discovery

    If save_rocord is true, it will save the record of all data in the provided trial besides the number of result

    Attributes:
        save_rocord (boolean): whether to save the record data
        tp (int): number of true positive
        tn (int): number of true negative
        fp (int): number of false positive
        fn (int): number of false negative
        tp_list (list, optional): saved true positive list
        tn_list (list, optional): saved true negative list
        fp_list (list, optional): saved false positive list
        fn_list (list, optional): saved false negative list
    '''

    def __init__(self, save_rocord=False):
        '''
        init the number of true positive, true negative, false positive, false negative to 0
        init save_rocord, default is False
        if save_rocord is True, init the true positive list, true negative list,
        false positive list, false negative list to empty list

        Args:
            save_rocord (boolean): Whether save the record of data. Defaults to False.
        '''
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0
        self.save_rocord = save_rocord
        if (self.save_rocord):
            self.tp_list = []
            self.tn_list = []
            self.fp_list = []
            self.fn_list = []

    def add_trial(self, trial: Trial):
        '''
        Based on the trial and the ground truth (stored in trial), do statistics analysis.
        Save the statistics to the Class Args.

        Args:
            trial (Trial): the Trial to be analysis
        '''
        self.tp, self.tn, self.fp, self.fn, self.tp_list, self.tn_list, self.fp_list, self.fn_list = self.__statistics_trial(
            trial)

    def precision(self) -> float:
        '''
        Based on the mathematical formula:
            precision = true positive / (true positive + false positive)
        Calculate and return the precision

        Returns:
            precision (float)
        '''
        if self.tp + self.fp == 0:
            return 0
        return self.tp / (self.tp + self.fp)

    def recall(self) -> float:
        '''
        return the true positive ratio

        Returns:
            recall (float)
        '''
        return self.true_positives()

    def f_measure(self) -> float:
        '''
        Based on the mathematical formula:
            f_measure = 2 * true positive / (2 * true positive + false positive + false negative)
        Calculate and return the f_measure

        Returns:
            f_measure (float)
        '''
        base = 2 * self.tp + self.fp + self.fn
        if base == 0:
            return 0
        return 2 * self.tp / base

    def false_positives(self) -> float:
        '''
        Based on the mathematical formula:
            false positive ratio = false positive / (false positive + true negative)
        Calculate and return the false positive ratio

        Returns:
            false positive ratio (float)
        '''
        if (self.fp + self.tn) == 0:
            return 0
        return self.fp / (self.fp + self.tn)

    def true_positives(self) -> float:
        '''
        Based on the mathematical formula:
            true positive ratio = true positive / (true positive + false negative)
        Calculate and return the true positive ratio

        Returns:
            true positive ratio (float)
        '''
        if (self.tp + self.fn) == 0:
            return 0
        return self.tp / (self.tp + self.fn)

    def false_negatives(self) -> float:
        '''
        Based on the mathematical formula:
            false negative ratio = false negative / (false negative + true positive)
        Calculate and return the false negative ratio

        Returns:
            false negative ratio (float)
        '''
        if (self.tp + self.fn) == 0:
            return 0
        return self.fn / (self.tp + self.fn)

    def true_negatives(self) -> float:
        '''
        Based on the mathematical formula:
            true negative ratio = true negative / (true negative + false positive)
        Calculate and return the true negative ratio

        Returns:
            true negative ratio (float)
        '''
        if (self.fp + self.tn) == 0:
            return 0
        return self.tn / (self.fp + self.tn)

    def false_discovery(self):
        '''
        Based on the mathematical formula:
            false discovery = false positive / (false positive + true positive)
        Calculate and return the false false discovery

        Returns:
            false discovery (float)
        '''
        if (self.fp + self.tp) == 0:
            return 0
        return self.fp / (self.fp + self.tp)

    def __statistics_trial(self, trial: Trial):
        '''
        Analysis the calculate result in trial and filter them by ground truth.
        If save_rocord is False, only the number will be saved.
        If save_rocord is True, the record items will be saved, too.

        Args:
            trial (Trial): the Trial to be analysis

        Returns:
            tp (int): number of true positive
            tn (int): number of true negative
            fp (int): number of false positive
            fn (int): number of false negative
            tp_list (list, optional): saved true positive list
            tn_list (list, optional): saved true negative list
            fp_list (list, optional): saved false positive list
            fn_list (list, optional): saved false negative list
        '''
        if self.save_rocord:
            tp_list = []
            tn_list = []
            fp_list = []
            fn_list = []

            ground_truth = trial.get_ground_truth()

            for trial_result in trial.get_all_data():
                gt_val = ground_truth.is_positive(trial_result.record1.id, trial_result.record2.id)
                cal_val = trial_result.is_positive

                if cal_val and gt_val:
                    tp_list.append(trial_result.full_data)
                elif not cal_val and not gt_val:
                    tn_list.append(trial_result.full_data)
                elif cal_val and not gt_val:
                    fp_list.append(trial_result.full_data)
                elif not cal_val and gt_val:
                    fn_list.append(trial_result.full_data)

            return len(tp_list), len(tn_list), len(fp_list), len(fn_list), tp_list, tn_list, fp_list, fn_list
        else:
            tp = 0
            tn = 0
            fp = 0
            fn = 0

            ground_truth = trial.get_ground_truth()

            for trial_result in trial.get_all_data():
                gt_val = ground_truth.is_positive(trial_result.record1.id, trial_result.record2.id)
                cal_val = trial_result.is_positive

                if cal_val and gt_val:
                    tp += 1
                elif not cal_val and not gt_val:
                    tn += 1
                elif cal_val and not gt_val:
                    fp += 1
                elif not cal_val and gt_val:
                    fn += 1

            return tp, tn, fp, fn, [], [], [], []
    # def get_true_positive_list(self):
