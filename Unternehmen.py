# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 16:09:56 2023

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
            self.unique_id = unique_id          
            
            # non-decision variables, used for tracking results
            self.e_e_s = self.model.database.optimization_parameter['e_e_s']
            self.c_e_d = self.model.database.optimization_parameter['c_e_d']
            self.c_kwk = self.model.database.optimization_parameter['c_kwk']
            self.c_w = self.model.database.optimization_parameter['c_w']
            self.c_g_grid = self.model.database.optimization_parameter['c_g_grid']
            self.c_hs = self.model.database.optimization_parameter['c_hs']
            self.c_q_d = self.model.database.optimization_parameter['c_q_d']
            self.e_q_s = self.model.database.optimization_parameter['e_q_s']
            self.c_t_d = self.model.database.optimization_parameter['c_t_d']
            self.e_t_s = self.model.database.optimization_parameter['e_t_s']
            self.D_heat = self.model.database.optimization_parameter['D_heat']
            self.f_heat= self.model.database.optimization_parameter['f_heat']
            self.cap_max_q = self.model.database.optimization_parameter['cap_max_q']
            self.cap_max_s = self.model.database.optimization_parameter['cap_max_s']
            self.cap_max_t = self.model.database.optimization_parameter['cap_max_t']
            self.cap_max_w = self.model.database.optimization_parameter['cap_max_w']
            self.cap_max_kwk = self.model.database.optimization_parameter['cap_max_kwk']
            self.cap_max_g = self.model.database.optimization_parameter['cap_max_g']
            self.cap_max_e = self.model.database.optimization_parameter['cap_max_e']
            self.cap_min_kwk = self.model.database.optimization_parameter['cap_min_kwk']
            self.cap_min_g = self.model.database.optimization_parameter['cap_min_g']
            self.cap_min_e = self.model.database.optimization_parameter['cap_min_e']
            self.E_pv = self.model.database.optimization_parameter['E_pv'] #evtl. Berechnung aus Wetterdaten
            self.const_e_to_h = self.model.database.optimization_parameter['const_e_to_heat'] 
            self.const_g_to_h = self.model.database.optimization_parameter['const_g_to_heat']
            self.c_kWh = self.model.database.optimization_parameter['c_kWh']
            self.c_dr = self.model.database.optimization_parameter['c_dr']
            self.t_lenght = self.model.database.optimization_parameter['t_lenght']
            self.epsilon_kwk = self.model.database.optimization_parameter['epsilon_kwk'] 
            self.epsilon_w = self.model.database.optimization_parameter['epsilon_w']
            self.epsilon_g = self.model.database.optimization_parameter['epsilon_g']
            self.epsilon_e = self.model.database.optimization_parameter['epsilon_e']
            self.epsilon_q = self.model.database.optimization_parameter['epsilon_q']
            #self.epsilon_s = self.model.database.optimization_parameter['epsilon_s']
            self.epsilon_t = self.model.database.optimization_parameter['epsilon_t']
            self.epsilon_max_kWh = self.model.database.optimization_parameter['epsilon_max_kWh']
            self.M = self.model.database.optimization_parameter['M'] #Definition des Ms notwendig
            
            # update data and set up model
            #self.update_data()
            self.results = []
            result = self.setup_model(True, False, False, False)
            self.results.append(result)
            result = self.setup_model(False, True, False, False)
            self.results.append(result)
            result = self.setup_model(False, False, True, False)
            self.results.append(result)
            result = self.setup_model(False, False, False, True)
            self.results.append(result)
            
            opt_list = self.results[0][1], self.results[1][1], self.results[2][1], self.results[3][1]
            max_value = max(opt_list)
            max_index = opt_list.index(max_value)
            self.opt = self.results[max_index]
            return
            
        def update_data(self):
            #code
            return
            
        def setup_model(self, no_net_dicount, min_net_discount, mid_net_discount, max_net_discount):
            # time index
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # industry model
            self.m = gp.Model(f'industry_{self.unique_id}')
            self.m.Params.OutputFlag = 0
            
            # decision variables, used in optimization
            self.E_kwk = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_kwk', lb=0, ub=self.cap_max_kwk)
            self.q_w = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_w', lb=0, ub=self.cap_max_w)
            self.g_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='g_d_grid', lb=0, ub=GRB.INFINITY)
            self.E_total_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_total_d', lb=0, ub=GRB.INFINITY)
            self.E_total_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_total_s', lb=0, ub=GRB.INFINITY)
            self.q_hs = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_hs', lb=0, ub=GRB.INFINITY)
            self.c_net = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='c_net', lb=0, ub=GRB.INFINITY)
            self.q_q_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_q_d', lb=0, ub=GRB.INFINITY)
            self.q_q_s= self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_q_s', lb=0, ub=GRB.INFINITY)
            self.q_t_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_t_d', lb=0, ub=GRB.INFINITY)
            self.q_t_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_t_s', lb=0, ub=GRB.INFINITY)
            self.q_e_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_e_d', lb=0, ub=self.cap_max_e)
            self.q_g_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_g_d', lb=0, ub=self.cap_max_g)
            self.b_ih = self.m.addVars(
                rti, vtype=GRB.BINARY, name='b_ih')
            self.b_q_d = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_q_d')
            self.b_q_s = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_q_s')
            self.b_t_d = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_t_d')
            self.b_t_s = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_t_s')
            self.b_e_total_d = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_e_total_d')
            self.b_e_total_s = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_e_total_s')
            self.E_res = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_res', lb=0, ub=GRB.INFINITY)
            self.E_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_d_grid', lb=0, ub=GRB.INFINITY)
            self.b_e_d_grid = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_g_grid')
            self.b_oh = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_oh')
            self.E_max = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='E_max', lb=0, ub=GRB.INFINITY)
            self.OH = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='OH', lb=0, ub=GRB.INFINITY)
            self.E_total = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='E_total', lb=0, ub=GRB.INFINITY)
            self.epsilon_max = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='epsilon_max', lb=0, ub=GRB.INFINITY)
            # target funktion
            self.m.setObjective(gp.quicksum(self.E_kwk[i]*self.c_kwk[i] + self.q_w[i]*self.c_w[i] + self.g_d_grid[i] * self.c_g_grid[i] + self.E_total_d[i]*self.c_e_d[i] - self.E_total_s[i]*self.e_e_s[i] + self.c_net[i] + self.q_hs[i]*self.c_hs[i] + self.q_q_d[i]*self.c_q_d[i] - self.q_q_s[i]*self.e_q_s[i] + self.q_t_d[i]*self.c_t_d[i] - self.q_t_s[i]*self.e_t_s[i]  for i in rti), GRB.MINIMIZE)
           
            # constraints
            for j in rti:
                self.m.addConstr(-(self.M*self.b_ih[j])+self.q_g_d[j]+self.q_e_d[j]+self.q_w[j] <= self.D_heat[j], name=f'if_production1{j}')
                self.m.addConstr((self.M-self.b_ih[j])+self.q_g_d[j]+self.q_e_d[j]+self.q_w[j] >= self.D_heat[j], name=f'if_production2{j}')
                if self.b_ih[j]==1:
                    self.m.addConstr(self.q_q_d[j]==0, name=f'set_P2P_trading_demand_to_zero{j}')
                    self.m.addConstr(self.q_t_d[j]==0, name=f'set_teleheating_demand_to_zero{j}')
                else:
                    self.m.addConstr(self.q_q_s[j]==0, name=f'set_P2P_trading_supply_to_zero{j}')
                    self.m.addConstr(self.q_t_s[j]==0, name=f'set_teleheating_supply_to_zero{j}')
                    self.m.addConstr(self.q_hs[j]==0, name=f'set_heat_sink_to_zero{j}')
                self.m.addConstr(self.b_q_d[j]*self.M >= self.q_q_d[j], name=f'binary_q_d{j}')
                self.m.addConstr(self.b_q_s[j]*self.M >= self.q_q_s[j], name=f'binary_q_s{j}')
                self.m.addConstr(self.b_q_d[j]+self.b_q_s[j] <=1, name=f'q_d_or_q_s{j}')
                self.m.addConstr(self.b_t_d[j]*self.M >= self.q_t_d[j], name=f'binary_t_d{j}')
                self.m.addConstr(self.b_t_s[j]*self.M >= self.q_t_s[j], name=f'binary_t_s{j}')
                self.m.addConstr(self.b_t_d[j]+self.b_t_s[j] <=1, name=f't_d_or_t_s{j}')
                self.m.addConstr((self.q_e_d[j]+self.q_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j])<=self.D_heat[j]*(1+self.f_heat), name=f'demand_satisfaction_max{j}')
                self.m.addConstr((self.q_e_d[j]+self.q_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j])>=self.D_heat[j]*(1-self.f_heat), name=f'demand_satisfaction_min{j}')
                self.m.addConstr(self.b_t_d[j]*self.M>=self.q_t_d[j], name=f'b_t_d{j}')
                self.m.addConstr(self.b_t_s[j]*self.M>=self.q_t_s[j], name=f'b_t_s{j}')
                self.m.addConstr(self.b_t_d[j]*self.b_t_s[j]<=1, name=f'b_t_d_vs.b_t_s{j}')
                if self.q_e_d[j]>0:
                    self.m.addConstr(self.q_e_d[j]>=self.cap_min_e, name=f'q_e_d_cap_min{j}')
                if self.q_g_d[j]>0:
                    self.m.addConstr(self.q_g_d[j]>=self.cap_min_g, name=f'q_g_d_cap_min{j}')
                if self.E_kwk[j]>0:
                    self.m.addConstr(self.E_kwk[j]>=self.cap_min_kwk, name=f'E_kwk_d_cap_min{j}')    
                if self.q_w[j]>0:
                    self.m.addConstr(self.q_w[j]>=self.cap_min_w, name=f'q_w_d_cap_min{j}')   
                self.m.addConstr(self.E_d_grid[j]==self.q_e_d[j]*self.const_e_to_h, name=f'q_e_d -> E_d_grid{j}')
                self.m.addConstr(self.g_d_grid[j]==self.q_g_d[j]*self.const_g_to_h, name=f'q_g_d -> g_d_grid{j}')
                self.m.addConstr(self.E_total_d[j]-self.E_total_s[j]==self.E_d_grid[j]+self.E_res[j]-self.E_pv[j]-self.E_kwk[j], f'calculate_E_total{j}')
                self.m.addConstr(self.b_e_total_d[j]*self.M>=self.E_total_d[j], name=f'b_e_total_d{j}')
                self.m.addConstr(self.b_e_total_s[j]*self.M>=self.E_total_s[j], name=f'b_e_total_s{j}')
                self.m.addConstr(self.b_e_total_d[j]+self.b_e_total_s[j]<=1, name=f'b_e_total_d_vs.b_e_total_s{j}')
            
            self.m.addConstr(self.E_total==gp.quicksum(self.E_total_d[j] -self.E_total_s[j] for j in rti), name='calculate_E_total')
            if min_net_discount or mid_net_discount or max_net_discount:
                self.m.addConstr(self.E_total>=1000000, name='E_total>=10Gw')
            self.m.addConstr(gp.quicksum((self.q_e_d[j]+self.q_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j]) for j in rti)>=self.D_heat[j] , name=f'demand_satisfaction_total{j}')
            self.m.addConstr(self.E_max==np.max(self.E_total_d), name='calculate_E_max')
            self.m.addConstr(self.OH==self.E_total/self.E_max, name='calculate_OH')
            if no_net_dicount:
                self.m.addConstr(self.c_net==(gp.quicksum(self.c_kWh*self.E_total[i] for i in rti)+self.c_dr*self.E_max), name='calculate_c_net')
            if min_net_discount:
                self.m.addConstr(self.OH>=7000, name='OH>=7000')
                self.m.addConstr(self.c_net==(gp.quicksum(self.c_kWh*self.E_total[i] for i in rti)+self.c_dr*self.E_max)*0.2, name='calculate_c_net')
            if mid_net_discount:
                self.m.addConstr(self.OH>=7500, name='OH>=7500')
                self.m.addConstr(self.c_net==(gp.quicksum(self.c_kWh*self.E_total[i] for i in rti)+self.c_dr*self.E_max)*0.15, name='calculate_c_net')
            if max_net_discount:
                self.m.addConstr(self.OH>=8000, name='OH>=8000')
                self.m.addConstr(self.c_net==(gp.quicksum(self.c_kWh*self.E_total[i] for i in rti)+self.c_dr*self.E_max)*0.1, name='calculate_c_net')
            self.m.addConstr(self.epsilon_max==self.epsilon_max_kWh*gp.quicksum(self.q_e_d[i]+self.q_g_d[i]+self.q_q_d[i]+self.q_t_d[i]+self.q_w[i] for i in rti), name='calculate_epsilon_max')
            self.m.addConstr(self.epsilon_max<=gp.quicksum((self.E_total_d[i]-self.E_total_s)*self.epsilon_e[i]+self.g_d_grid[i]*self.epsilon_g[i]+self.E_kwk[i]*self.epsilon_kwk[i]+self.q_w[i]*self.epsilon_w[i]+self.q_q_d[i]*self.epsilon_q[i]+self.q_t_d[i]*self.epsilon_t[i] for i in rti), name='check_epsilon_max')
            return self.run_model()
        
        def run_model(self):
            rti = list(range(len(self.model.time_index)))
            self.m.optimize()
        
            # Check optimization status
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
        

