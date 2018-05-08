import json
import heapq

import matplotlib.pyplot as plt
import numpy as np
from rltk.evaluation.trial import Trial
from rltk.record import Record, cached_property
from rltk.evaluation.ground_truth import GroundTruth


class Evaluation(object):
    def __init__(self, trial_list: list = []):
        self.trial_list = trial_list

    def add_trial(self, trial: Trial):
        if self.trial_list == None:
            self.trial_list = []
        self.trial_list.append(trial)

    def plot(self, parameter_list):

        if self.trial_list == None:
            raise Exception("Empty Trial List, init it Firstly")

        plt.figure()
        for param in parameter_list:

            x, y = [], []

            x_key, y_key = param['x'], param['y']
            print(x_key, y_key)

            for trial in self.trial_list:
                x.append(getattr(trial, x_key))
                y.append(getattr(trial, y_key))

            other_parameters = {}
            for k in param.keys():
                if k in ('x', 'y'):
                    continue
                other_parameters[k] = param[k]

            print (other_parameters)
            plt.plot(x, y, **other_parameters)

        plt.legend(loc='upper right')
        plt.show()

