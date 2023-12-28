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
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # decision variables, used in optimization
            self.q_kwk = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_kwk', lb=0, ub=self.cap_max_kwk)
            self.q_w = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_w', lb=0, ub=self.cap_max_w)
            self.q_g_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_g_grid', lb=0, ub=GRB.INFINITY)
            self.q_e_total_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_e_total_d', lb=0, ub=GRB.INFINITY)
            self.q_e_total_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_e_total_s', lb=0, ub=GRB.INFINITY)
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
            self.q_e_res = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_e_res', lb=0, ub=GRB.INFINITY)
            self.q_e_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_e_d_grid', lb=0, ub=GRB.INFINITY)
            self.b_e_d_grid = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_g_grid')
            self.b_oh = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_oh')
            self.q_e_max = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='q_e_max', lb=0, ub=GRB.INFINITY)
            self.OH = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='OH', lb=0, ub=GRB.INFINITY)
            self.Q_e_total = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='Q_e_total', lb=0, ub=GRB.INFINITY)
            self.E_ges = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='E_ges', lb=0, ub=GRB.INFINITY)
            
            # non-decision variables, used for tracking results
            self.p_e_s = self.model.database.optimization_parameter['p_e_s']
            self.p_e_d = self.model.database.optimization_parameter['p_e_d']
            self.p_kwk = self.model.database.optimization_parameter['p_kwk']
            self.p_w = self.model.database.optimization_parameter['p_w']
            self.p_g_grid = self.model.database.optimization_parameter['p_g_grid']
            self.p_hs = self.model.database.optimization_parameter['p_hs']
            self.p_q_d = self.model.database.optimization_parameter['p_q_d']
            self.p_q_s = self.model.database.optimization_parameter['p_q_s']
            self.p_t_d = self.model.database.optimization_parameter['p_t_d']
            self.p_t_s = self.model.database.optimization_parameter['p_t_s']
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
            self.q_pv = self.model.database.optimization_parameter['q_pv'] #evtl. Berechnung aus Wetterdaten
            self.c_e_to_h = self.model.database.optimization_parameter['c_e_to_heat'] 
            self.c_g_to_h = self.model.database.optimization_parameter['p_g_to_heat']
            self.p_e_d = self.model.database.optimization_parameter['p_e_d']
            self.p_e_s = self.model.database.optimization_parameter['p_e_s']
            self.q_oh_min = self.model.database.optimization_parameter['q_oh_min']
            self.p_kWh = self.model.database.optimization_parameter['p_kWh']
            self.p_dr = self.model.database.optimization_parameter['p_dr']
            self.t_lenght = self.model.database.optimization_parameter['t_lenght']
            self.e_kwk = self.model.database.optimization_parameter['e_kwk'] 
            self.e_w = self.model.database.optimization_parameter['e_w']
            self.e_g = self.model.database.optimization_parameter['e_g']
            self.e_e = self.model.database.optimization_parameter['e_e']
            self.e_q = self.model.database.optimization_parameter['e_q']
            #self.e_s = self.model.database.optimization_parameter['e_s']
            self.e_t = self.model.database.optimization_parameter['e_t']
            self.M = self.model.database.optimization_parameter['M'] #Definition des Ms notwendig
            
            # update data and set up model
            self.update_data()
            self.setup_model(True, False, False, False)
            self.setup_model(False, True, False, False)
            self.setup_model(False, False, True, False)
            self.setup_model(False, False, False, True)
            
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
            # target funktion
            self.m.setObjective(gp.quicksum(self.q_kwk[i]*self.p_kwk[i] + self.q_w[i]*self.p_w[i] + self.q_g_grid[i] * self.p_g_grid[i] + self.q_e_total_d[i]*self.p_e_d[i] - self.q_e_total_s*self.p_e_s + self.c_net[i] + self.q_hs[i]*self.p_hs[i] + self.q_q_d[i]*self.p_q_d[i] - self.q_q_s[i]*self.p_q_s[i] + self.q_t_d[i]*self.p_t_d[i] - self.q_t_s[i]*self.p_t_s[i]  for i in rti), GRB.MINIMIZE)
           
            # constraints
            for j in rti:
                self.m.addConstr(-(self.M*self.b_ih[j])+self.q_g_d[j]+self.q_e_d[j]+self.q_w[j] <= self.D_heat[j], name=f'if_production1{j}')
                self.m.addConstr((self.M-self.b_ih[j])+self.q_g_d[j]+self.q_e_d[j]+self.q_w[j] >= self.D_heat[j], name=f'if_production2{j}')
                if self.b_ih==1:
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
                self.m.addConstr((self.q_e_d[j]+self.q_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j])>=self.D_heat[j]*(1-self.f_heat), name=f'demand_satisfaction_max{j}')
                self.m.addConstr(self.b_t_d[j]*self.M>=self.q_t_d[j], name=f'b_t_d{j}')
                self.m.addConstr(self.b_t_s[j]*self.M>=self.q_t_s[j], name=f'b_t_s{j}')
                self.m.addConstr(self.b_t_d[j]*self.b_t_s[j]<=1, name=f'b_t_d_vs.b_t_s{j}')
                self.m.addConstr(self.b_e_total_d[j]*self.M>=self.q_e_total_d[j], name=f'b_e_total_d{j}')
                self.m.addConstr(self.b_e_total_s[j]*self.M>=self.q_e_total_s[j], name=f'b_e_total_s{j}')
                self.m.addConstr(self.b_e_total_d[j]*self.b_e_total_s[j]<=1, name=f'b_e_total_d_vs.b_e_total_s{j}')
                if self.q_e_d[j]>0:
                    self.m.addConstr(self.q_e_d[j]>=self.cap_min_e, name=f'q_e_d_cap_min{j}')
                if self.q_g_d[j]>0:
                    self.m.addConstr(self.q_g_d[j]>=self.cap_min_g, name=f'q_g_d_cap_min{j}')
                if self.q_kwk[j]>0:
                    self.m.addConstr(self.q_kwk[j]>=self.cap_min_kwk, name=f'q_kwk_d_cap_min{j}')    
                if self.q_w[j]>0:
                    self.m.addConstr(self.q_w[j]>=self.cap_min_w, name=f'q_w_d_cap_min{j}')   
                self.m.addConstr(self.q_e_d_grid[j]==self.q_e_d[j]*self.c_e_to_h, name=f'q_e_d -> q_e_d_grid{j}')
                self.m.addConstr(self.q_g_d_grid[j]==self.q_g_d[j]*self.c_g_to_h, name=f'q_g_d -> q_g_d_grid{j}')
                self.m.addConstr(self.q_e_total_d[j]-self.q_e_total_s[j]==self.q_e_d_grid[j]+self.q_e_res[j]-self.q_pv[j]-self.q_kwk[j], f'calculate_q_e_total{j}')
            
            self.m.addConstr(self.Q_e_total==gp.quicksum(self.q_e_total_d[j] -self.q_e_total_s[j] for i in rti), name='calculate_Q_e_total')
            if min_net_discount or mid_net_discount or max_net_discount:
                self.m.addConstr(self.Q_e_total>=1000000, name='Q_e_total>=10Gw')
            self.m.addConstr(gp.quicksum((self.q_e_d[j]+self.q_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j]) for j in rti)>=self.D_heat[j] , name=f'demand_satisfaction_total{j}')
            self.m.addConstr(self.q_e_max==np.max(self.q_e_total_d), name='calculate_q_e_max')
            self.m.addConstr(self.OH==self.Q_e_total/self.q_e_max, name='calculate_OH')
            if no_net_dicount:
                self.m.addConstr(self.c_net==(gp.quicksum(self.p_kWh*self.q_e_total[i] for i in rti)+self.p_dr*self.q_e_max), name=f'calculate_c_net{j}')
            if min_net_discount:
                self.m.addConstr(self.OH>=7000, name='OH>=7000')
                self.m.addConstr(self.c_net==(gp.quicksum(self.p_kWh*self.q_e_total[i] for i in rti)+self.p_dr*self.q_e_max)*0.2, name=f'calculate_c_net{j}')
            if mid_net_discount:
                self.m.addConstr(self.OH>=7500, name='OH>=7500')
                self.m.addConstr(self.c_net==(gp.quicksum(self.p_kWh*self.q_e_total[i] for i in rti)+self.p_dr*self.q_e_max)*0.15, name=f'calculate_c_net{j}')
            if max_net_discount:
                self.m.addConstr(self.OH>=8000, name='OH>=8000')
                self.m.addConstr(self.c_net==(gp.quicksum(self.p_kWh*self.q_e_total[i] for i in rti)+self.p_dr*self.q_e_max)*0.1, name=f'calculate_c_net{j}')
            self.m.addConstr(self.E_ges<=gp.quicksum((self.q_e_total_d[i]-self.q_e_total_s)*self.e_e[i]+self.q_g_grid[i]*self.e_g[i]+self.q_kwk[i]*self.e_kwk[i]+self.q_w[i]*self.e_w[i]+self.q_q_d[i]*self.e_q[i]+self.q_t_d[i]*self.e_t[i]-self.q_q_s[i]*self.e_q[i]-self.q_t_s[i]*self.e_t[i] for i in rti))
            return
        
        def run_model(self):
            rti = list(range(len(self.model.time_index)))
            self.m.optimize()
        
            # Check optimization status
            if self.m.status == GRB.OPTIMAL:
                print("Optimal solution found.")
            else:
                print("Optimization did not converge to an optimal solution.")
        
            # Get values of decision variables
            results = np.array([var.X for var in self.m.getVars()])
        
            return results
