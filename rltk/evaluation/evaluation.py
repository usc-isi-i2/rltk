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

    def draw(self, parameter_y):
        if self.trial_list == None:
            raise Exception("Empty Trial List, init it Firstly")
        x = []
        y = []
        labels = []

        for trial in self.trial_list:
            if getattr(trial, parameter_y) == None:
                raise Exception("Properity not exist")
            x.append(trial.parameter_x)
            y.append(getattr(trial, parameter_y))
            labels.append(trial.label)

        plt.figure()
        plt.plot(x, y)
        plt.show()
