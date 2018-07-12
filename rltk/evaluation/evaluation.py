import matplotlib.pyplot as plt
from rltk.evaluation.trial import Trial


class Evaluation(object):
    def __init__(self, trial_list: list = None):
        if not trial_list:
            trial_list = []
        self.trial_list = trial_list

    def add_trial(self, trial: Trial):
        self.trial_list.append(trial)

    def plot(self, parameter_list, area):
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
           area (bool): whether AUC (area under the curve) is desired
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
        
        if area:
            coords = sorted([(x[i], y[i]) for i in range(len(x))])
            coords_reduced = dict()
            prev = coords[0][0]
            max_y = coords[0][1]
            for c in coords:
                if prev == c[0]:
                    if c[1] > max_y:
                        max_y = c[1]
                else:
                    coords_reduced[prev] = max_y
                    prev = c[0]
                    max_y = c[1]
            coords_reduced[prev] = max_y
            
            area = 0
            x1 = 0
            y1 = 0
            first = True
            for key, value in coords_reduced.items():
                if not first:
                    area +=  (key - x1) * (value + y1) / 2
                x1 = key
                y1 = value
                first = False
                
            plt.text(x[-1], y[-1], 'Area: ' + ('%.5f' % area))

        plt.xlim(0, 1.05)
        plt.ylim(0, 1.05)
        
        plt.show()

    def plot_precision_recall(self):
        return self.plot([{
            'x': 'recall',
            'y': 'precision'
        }], False)
