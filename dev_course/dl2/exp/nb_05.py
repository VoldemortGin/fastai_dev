
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/05_anneal.ipynb

from exp.nb_04 import *
from functools import partial

def create_learner(model_func, loss_func, data):
    return Learner(*model_func(data), loss_func, data)

def get_model_func(lr=0.5): return partial(get_model, lr=lr)

class Recorder(Callback):
    def begin_fit(self, run):
        run.lrs=[]
        run.losses=[]
        run.stats=[]

    def after_batch(self, run):
        if run.in_train:
            run.lrs.append(run.opt.param_groups[-1]['lr'])
            run.losses.append(run.loss)

def plot_lr  (run): plt.plot(run.lrs)
def plot_loss(run): plt.plot(run.losses)

class ParamScheduler(Callback):
    _order=1
    def __init__(self, pname, sched_func): self.pname,self.sched_func = pname,sched_func

    def set_param(self, run):
        for pg in run.opt.param_groups:
            pg[self.pname] = self.sched_func(run.n_epochs/run.epochs)

    def begin_batch(self, run):
        if run.in_train: self.set_param(run)

import numpy as np

def _sched_lin_val(start, end, pos): return start + pos*(end-start)
def sched_lin(start, end): return partial(_sched_lin_val, start, end)
def _sched_cos_val(start, end, pos): return start + math.cos(math.pi*pct/2.)*(end-start)
def sched_cos(start, end): return partial(_sched_cos_val, start, end)

def combine_scheds(pcts, scheds):
    assert sum(pcts) == 1.
    assert np.all(np.array(pcts) >= 0)
    pcts = np.cumsum([0] + pcts)
    def _inner(pos):
        idx = (pos >= pcts).nonzero()[0].max()
        actual_pos = (pos-pcts[idx]) / (pcts[idx+1]-pcts[idx])
        return scheds[idx](actual_pos)
    return _inner