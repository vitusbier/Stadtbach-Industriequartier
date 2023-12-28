# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 13:08:06 2023

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
            self.q_ih_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_ih', lb=0, ub=self.cap_max_ih)
            self.q_q_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_q_s', lb=0, ub=GRB.INFINITY)
            self.q_q_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_q_d', lb=0, ub=GRB.INFINITY)
            self.q_t_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_t_s', lb=0, ub=GRB.INFINITY)
            
            # non-decision variables, used for tracking results
            self.cap_max_ih = self.model.database.optimization_parameter['cap_max_ih']
            self.Res_pre = self.model.database.optimization_parameter['Res_pre']
            self.p_q_s = self.model.database.optimization_parameter['p_q_s']
            self.p_t_s = self.model.database.optimization_parameter['p_t_s']
            self.p_ih_d = self.model.database.optimization_parameter['p_ih_d']
            self.p_q_d = self.model.database.optimization_parameter['p_q_d']
            
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
            self.m.setObjective(gp.quicksum(self.q_q_s[i]*self.p_q_s[i]- self.q_t_s[i]*self.p_t_s[i]- self.q_ih_d[i]*self.p_ih_s[i] -self.q_q_d[i]*self.p_ih_s[i] for i in rti), GRB.MAXIMIZE)

            # constraints
            for j in rti:
                if j==0:
                    self.m.addConstr(self.q_q_d>=0, name=f'q_q_d_min_1{j}')
                    self.m.addConstr(self.q_q_s>=0, name=f'q_q_d_min_1{j}')
                    
            return
        
        def run_model(self):
            rti = list(range(len(self.model.time_index)))
            self.m.optimize()
            # get values of decision variables
            results = np.array([var.X for var in self.m.getVars() if 'g_d[' in var.VarName] + [var.X for var in self.m.getVars() if 'g_s[' in var.VarName])
            
            return results