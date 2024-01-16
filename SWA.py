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
        def __init__(self, unique_id, model):   
            super().__init__()
            
            # set agent parameter
            self.model=model

            # time index
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # non-decision variables, used for tracking results
            self.cap_max_ih = self.model.database.optimization_parameter['cap_max_ih']
            self.Res_pre = self.model.database.optimization_parameter['Res_pre']
            self.e_q_s = self.model.database.optimization_parameter['e_q_s']
            self.e_t_s = self.model.database.optimization_parameter['e_t_s']
            self.c_ih_d = self.model.database.optimization_parameter['c_ih_d']
            self.c_q_d = self.model.database.optimization_parameter['c_q_d']
            self.e_q = self.model.database.optimization_parameter['e_q']
            self.e_ih = self.model.database.optimization_parameter['e_ih']
            self.epsilon_max_kWh = self.model.database.optimization_parameter['epsilon_max_kWh']
            
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
            self.q_ih_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_ih', lb=0, ub=self.cap_max_ih)
            self.q_q_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_q_s', lb=0, ub=GRB.INFINITY)
            self.q_q_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_q_d', lb=0, ub=GRB.INFINITY)
            self.q_t_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_t_s', lb=0, ub=GRB.INFINITY)
            self.Epsilon_max = self.m.addVar(
                vtype=GRB.CONTINUOUS, name='Epsilon_max', lb=0, ub=GRB.INFINITY)
            
            # target funktion
            self.m.setObjective(gp.quicksum(self.q_q_s[i]*self.e_q_s[i]- self.q_t_s[i]*self.e_t_s[i]- self.q_ih_d[i]*self.c_ih_d[i] -self.q_q_d[i]*self.c_q_d[i] for i in rti), GRB.MAXIMIZE)

            # constraints
            for j in rti:
                if j==0:
                    self.m.addConstr(self.q_q_d[j]>=0, name=f'q_q_d_min_1{j}')
                    self.m.addConstr(self.q_q_s[j]>=0, name=f'q_q_s_min_1{j}')
                elif self.Res_pre >=0:
                    self.m.addConstr(self.q_q_d[j] >= self.Res_pre[j], name=f'q_q_d_min_Res>=0{j}')
                elif self.Res_pre <0:
                    self.m.addConstr(self.q_q_s[j] >= self.Res_pre[j], name=f'q_q_s_min_Res<=0{j}')
            self.m.addConstr(self.Epsilon_max==self.epsilon_max_kWh_max*gp.quicksum(self.q_q_d[j]+self.q_ih_d[j] for j in rti), name='calculation_Epsilon_max')
            self.m.addConstr(0<=gp.quicksum(self.q_q_d[j]+self.q_ih_d[j]-self.q_t_s-self.q_q_s for j in rti), name='demand>=supply')
            self.m.addConstr(self.Epsilon_max <= gp.quicksum(self.q_q_d[j]*self.e_q+self.q_ih_d[j]*self.e_ih for j in rti), name='Emissions')
            self.results = self.run_model()
            return
        
        def run_model(self):
            rti = list(range(len(self.model.time_index)))
            self.m.optimize()

            if self.m.status == GRB.OPTIMAL:
                print("Optimal solution found.")
                # Get values of decision variables
                results = np.array([var.X for var in self.m.getVars()])
                value_target = self.m.ObjVal
                return results, value_target
            else:
                print("Optimization did not converge to an optimal solution.")
                self.m.computeIIS()
                self.m.write("model.ilp")
                return None, 0