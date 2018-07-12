import matplotlib.pyplot as plt
from rltk.evaluation.trial import Trial


class Evaluation(object):
    def __init__(self, trial_list: list = None):
        if not trial_list:
            trial_list = []
        self.trial_list = trial_list

    def add_trial(self, trial: Trial):
        self.trial_list.append(trial)

    def plot(self, parameter_list):
        """
        Args:
            parameter_list (list): list of object
                ```
                {
                    'x': 'name of a property in Trial',
                    'y': 'name of a property in Trial',
                    'label': 'label name',
                    ...
                }
                ```
        """

        if len(self.trial_list) == 0:
            raise Exception("Empty trial list")

        plt.figure()

        for param in parameter_list:
            x, y = [], []

            x_key, y_key = param['x'], param['y']
            other_parameters = {}
            for k in param.keys():
                if k in ('x', 'y'):
                    continue
                other_parameters[k] = param[k]

            for trial in self.trial_list:
                x.append(getattr(trial, x_key))
                y.append(getattr(trial, y_key))

            plt.plot(x, y, **other_parameters)

        plt.legend(loc='upper right')
        plt.show()

    def plot_precision_recall(self):
        return self.plot([{
            'x': 'recall',
            'y': 'precision'
        }])
