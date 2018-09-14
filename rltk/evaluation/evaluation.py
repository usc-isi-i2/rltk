from rltk.evaluation.trial import Trial
import matplotlib.pyplot as plt


class Evaluation(object):
    """
    A collection of :meth:`Trial` s. It can be used to plot chart for multiple Trials.
    
    Args:
        trial_list (list[Trial], optional): List of Trials, default is None.
    """

    def __init__(self, trial_list: list = None):
        if not trial_list:
            trial_list = []
        self.trial_list = trial_list

    def add_trial(self, trial: Trial):
        """
        Add a Trial
        
        Args:
            trial (Trial): A Trial.
        """
        self.trial_list.append(trial)

    def auc(self, x, y):
        """
        Compute AUC (Area Under Curve)
        
        Args:
            x (list): list of x coordinates
            y (list): list of y coordinates
            
        Returns:
            tuple:
                float: AUC 
                list: X-axis
                list: Y-axis
        """
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

        x1 = 0
        y1 = 0
        auc = 0
        first = True
        for key, value in coords_reduced.items():
            if not first:
                auc += (key - x1) * (value + y1) / 2
            x1 = key
            y1 = value
            first = False
        return [auc, list(coords_reduced.keys()), list(coords_reduced.values())]

    def plot(self, parameter_list, label_max=False, label_min=False, auc_params=None, aoc_params=None,
             x_label=None, y_label=None):
        """
        General purpose plotting interface.
        
        Args:
            parameter_list (list): list of object::
            
                [{
                    'x': 'name of a property in Trial',
                    'y': 'name of a property in Trial',
                    'fmt': 'formatting of color, line style. defaults to b-',
                    'label': 'label name, this can be empty'
                }]
                
            label_max (bool, optional): whether to label max
            label_min (bool, optional): whether to label min
            auc_params (list, optional): list of AUC labelling and shading parameters::
            
                [
                    desired x coordinate of AUC label (float),
                    desired y coordinate of AUC label (float),
                    whether to shading AUC is desired (bool)
                ]
                
            aoc_params (list, optional): list of AOC labelling and shading parameters::
            
                [
                    desired x coordinate of AOC label (float),
                    desired y coordinate of AOC label (float),
                    whether to shading AOC is desired (bool)
                ]
            
            x_labels (str, optional): Label of X-axis, defaults to None.
            y_labels (str, optional): Label of Y-axis, defaults to None.
            
        Returns:
            matplotlib.pyplot:
        """

        if len(self.trial_list) == 0:
            raise Exception("Empty trial list")

        plt.figure()

        for param in parameter_list:
            x, y = [], []

            x_key, y_key = param['x'], param['y']
            fmt = param.get('fmt', 'b-')
            other_parameters = {}
            for k in param.keys():
                if k in ('x', 'y', 'fmt'):
                    continue
                other_parameters[k] = param[k]

            for trial in self.trial_list:
                x.append(getattr(trial, x_key))
                y.append(getattr(trial, y_key))

            plt.plot(x, y, fmt, **other_parameters)

        plt.legend(loc='upper right')
        if x_label:
            plt.xlabel(x_label)
        if y_label:
            plt.ylabel(y_label)

        if label_max:
            global_max = max([(x[i], y[i]) for i in range(len(x))], key=lambda i: (i[1], -i[0]))
            plt.annotate("(" + ("%.3f" % global_max[0]) + ", " + ("%.3f" % global_max[1]) + ")",
                         xy=(global_max[0] - 0.1, global_max[1] + 0.05))

        if label_min:
            global_min = min([(x[i], y[i]) for i in range(len(x))], key=lambda i: (i[1], -i[0]))
            plt.annotate("(" + ("%.3f" % global_min[0]) + ", " + ("%.3f" % global_min[1]) + ")",
                         xy=(global_min[0] - 0.1, global_min[1] - 0.05))

        if auc_params:
            vals = self.auc(x, y)
            auc = vals[0]
            area_label = 'AUC: ' + ('%.5f' % auc)
            plt.annotate(area_label, xy=(auc_params[0], auc_params[1]))

            if auc_params[2]:
                x_vals = vals[1]
                y_vals = vals[2]
                plt.fill_between(x, y)

        if aoc_params:
            vals = self.auc(x, y)
            aoc = 1 - vals[0]
            area_label = 'AOC: ' + ('%.5f' % aoc)
            plt.annotate(area_label, xy=(aoc_params[0], aoc_params[1]))

            if aoc_params[2]:
                x_vals = vals[1]
                y_vals = vals[2]
                plt.fill_between(x, y, y2=1)

        plt.xlim(0, 1.05)
        plt.ylim(0, 1.05)

        return plt

    def plot_precision_recall(self, show_points: bool = False):
        """
        Plot precision recall curve. X-axis is recall, Y-axis is precision.
        
        Args:
            show_points (bool, optional): Show points or not. Default is False.
        
        Returns:
            matplotlib.pyplot:
        """

        p_list = [{
            'x': 'recall',
            'y': 'precision',
            'fmt': 'b-',
            'label': 'Precision - Recall',
        }]
        if show_points:
            p_list.append({
                'x': 'recall',
                'y': 'precision',
                'fmt': 'bo'
            })
        return self.plot(p_list, x_label='Precision', y_label='Recall')

    def plot_roc(self):
        """
        Plot ROC (Receiver Operating Characteristic) curve. X-axis is false positives, Y-axis is true positives.
        
        Returns:
            matplotlib.pyplot:
        """
        return self.plot([{
            'x': 'false_positives',
            'y': 'true_positives',
            'label': 'ROC'
        }], auc_params=[0.05, 0.95, True], x_label='False Positives', y_label='True Negatives')

    def plot_features(self, df, f1, f2):
        """
        Plot distribution of two features.
        
        Args:
            df (pandas.DataFrame): dataframe containing trial results and computed features
            f1 (str): feature to place on the x-axis
            f2 (str): feature to place on the y-axis
            
        Returns:
            matplotlib.pyplot:
        """
        tpX = []
        tpY = []
        fpX = []
        fpY = []
        tnX = []
        tnY = []
        fnX = []
        fnY = []
        count = 0
        
        for index, row in df.iterrows():
            count += 1
            l = row['ground_truth.label']
            p = row['is_positive']
            if int(l) == 1 and p == 1:
                tpX.append(row[f1])
                tpY.append(row[f2])
            if int(l) == 0 and p == 1:
                fpX.append(row[f1])
                fpY.append(row[f2])
            if int(l) == 1 and p == 0:
                fnX.append(row[f1])
                fnY.append(row[f2])
            if int(l) == 0 and p == 0:
                tnX.append(row[f1])
                tnY.append(row[f2])
                
        plt.subplot(1, 2, 1)
        plt.plot(tpX, tpY, 'o', color='green')
        plt.plot(fpX, fpY, 'o', color='red')
        plt.xlabel(f1)
        plt.ylabel(f2)
        plt.title(f1 + ' vs ' + f2 + ' TP and FP')
        
        plt.subplot(1, 2, 2)
        plt.plot(tnX, tnY, 'o', color='green')
        plt.plot(fnX, fnY, 'o', color='red')
        plt.xlabel(f1)
        plt.ylabel(f2)
        plt.title(f1 + ' vs ' + f2 + ' TN and FN')
        plt.tight_layout()
        return plt
