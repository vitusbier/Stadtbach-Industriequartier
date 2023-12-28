# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 19:44:27 2023

@author: juliu
"""

import mesa
import numpy as np
import gurobipy as gp
from gurobipy import GRB

class Storage(mesa.Agent):
        def __init__(self, unique_id, model, cap_max, cap_min, level_t):   
            super().__init__()
            
            # set agent parameter
            self.model=model
            self.cap_max = cap_max
            self.cap_min = cap_min
            self.level_t = level_t
            # time index
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # decision variables, used in optimization
            self.g_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='g_d', lb=0, ub=self.cap_max-self.level_t)
            self.g_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='g_s', lb=0, ub=self.level_t-self.cap_min)
            self.level_t_post = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='level_t_post')
            
            # non-decision variables, used for tracking results
            self.level_t0 = 0.5*self.cap_max
            self.levelT = 0.5*self.cap_max
            
            # update data and set up model
            self.update_data()
            self.setup_model()
            
        def update_data(self):
            #code
            return
            
        def setup_model(self):
            # time index
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # storage model
            self.m = gp.Model(f'storage_{self.unique_id}')
            self.m.Params.OutputFlag = 0
            # target funktion
            self.m.setObjective(gp.quicksum(self.q_d[i] + self.q_s[i] for i in rti), GRB.MAXIMIZE)

            # constraints
            for j in rti:
                self.m.addConstr(self.level_t_post[j] == (self.level_t[j] + self.q_d[j] - self.q_s[j]), name=f'set_level_next_period_{j}')
                self.m.addConstr(self.q_s[j] <= (self.level_t[j] - self.cap_min), name=f'max_quantity_selling_{j}') 
                self.m.addConstr(self.q_d[j] <= (self.cap_max - self.level_t[j]), name=f'max_quantity_buying_{j}')
                self.m.addConstr(self.level_t_post[len(rti)-1], name=f'set_level_last_periode_{j}')
            return
        
        def run_model(self):
            rti = list(range(len(self.model.time_index)))
            self.m.optimize()
            # get values of decision variables
            results = np.array([var.X for var in self.m.getVars() if 'g_d[' in var.VarName] + [var.X for var in self.m.getVars() if 'g_s[' in var.VarName])
            
            return results
            