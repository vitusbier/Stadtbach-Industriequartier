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
        def __init__(self, unique_id, model, level_t):   
            super().__init__()
            
            # set agent parameter
            self.model=model
            self.unique_id = unique_id
            self.cap_max = self.model.database.optimization_parameter['cap_max']
            self.cap_min = self.model.database.optimization_parameter['cap_min']
            self.level_t = level_t           

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
            
            # decision variables, used in optimization
            self.q_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_d', lb=0, ub=self.cap_max-self.level_t)
            self.q_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_s', lb=0, ub=self.level_t-self.cap_min)
            self.level_t_post = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='level_t_post')
            
            # target funktion
            self.m.setObjective(gp.quicksum(self.q_d[i] + self.q_s[i] for i in rti), GRB.MAXIMIZE)

            # constraints
            for j in rti:
                self.m.addConstr(self.level_t_post[j] == (self.level_t[j] + self.q_d[j] - self.q_s[j]), name=f'set_level_next_period_{j}')
                self.m.addConstr(self.q_s[j] <= (self.level_t[j] - self.cap_min), name=f'max_quantity_selling_{j}') 
                self.m.addConstr(self.q_d[j] <= (self.cap_max - self.level_t[j]), name=f'max_quantity_buying_{j}')
                self.m.addConstr(self.level_t_post[len(rti)-1], name=f'set_level_last_periode_{j}')
                
            self.results = self.run_model()
            return
        
        def run_model(self):
            if self.m.status == GRB.OPTIMAL:
                print("Optimal solution found.")
                # Get values of decision variables
                results = np.array([var.X for var in self.m.getVars()])
                value_target = self.m.ObjVal
                return results, value_target
            else:
                print("Optimization did not converge to an optimal solution.")
                return None, 0
            

            