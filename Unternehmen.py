# -*- coding: utf-8 -*-
# Importieren der benötigten Bibliotheken
import mesa
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# Klasse für den Unternehmens-Agenten, die von mesa.Agent erbt
class Unternehmen(mesa.Agent):
        def __init__(self, unique_id, model, t, results_Unternehmen, results_P2P_trading):   
            super().__init__()
            
            # Anlegen der Agentenparameter
            self.model = model
            self.unique_id = unique_id
            self.t = t
            self.results_Unternehmen = results_Unternehmen
            self.results_P2P_trading = results_P2P_trading
            self.e_E_el_s = self.model.database.optimization_parameter['e_E_el_s']
            self.c_E_el_d = self.model.database.optimization_parameter['c_E_el_d']
            self.c_kwk = self.model.database.optimization_parameter['c_kwk']
            self.c_w = self.model.database.optimization_parameter['c_w']
            self.c_E_g_grid = self.model.database.optimization_parameter['c_E_g_grid']
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
            self.E_el_pv = self.model.database.optimization_parameter['E_el_pv'] #evtl. Berechnung aus Wetterdaten
            self.E_el_res = self.model.database.optimization_parameter['E_el_res']
            self.const_E_el_to_h = self.model.database.optimization_parameter['const_E_el_to_heat'] 
            self.const_E_g_to_h = self.model.database.optimization_parameter['const_E_g_to_heat']
            self.c_kWh = self.model.database.optimization_parameter['c_kWh']
            self.c_dr = self.model.database.optimization_parameter['c_dr']
            self.t_lenght = self.model.database.optimization_parameter['t_lenght']
            self.epsilon_kwk = self.model.database.optimization_parameter['epsilon_kwk'] 
            self.epsilon_w = self.model.database.optimization_parameter['epsilon_w']
            self.epsilon_g = self.model.database.optimization_parameter['epsilon_g']
            self.epsilon_E_el = self.model.database.optimization_parameter['epsilon_E_el']
            self.epsilon_q = self.model.database.optimization_parameter['epsilon_q']
            #self.epsilon_s = self.model.database.optimization_parameter['epsilon_s']
            self.epsilon_t = self.model.database.optimization_parameter['epsilon_t']
            self.epsilon_max_kWh = self.model.database.optimization_parameter['epsilon_max_kWh']
            self.M = self.model.database.optimization_parameter['M'] #Definition des Ms notwendig
            return
        
        # Methode zur Initialisierung des Optimierungsmodells, falls erste Periode (Index = 0)
        def setup_model_t1(self, no_net_dicount, min_net_discount, mid_net_discount, max_net_discount):
            # Anlegen Zeitindex
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # Initialisierung des Modells
            self.m = gp.Model(f'industry_{self.unique_id}')
            self.m.Params.OutputFlag = 0 #Output-Parameter werden nicht ausgegeben, wenn 0
            
            # Anlegen der Entscheidungsvariablen
            # m.addVars mit Zeitindex rti -> Die EV wird als Array mit Eintrag für jede Periode angelegt
            # m.addVar -> eine einzelne EV für der Gesamtzeitraum
            self.E_el_kwk = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_kwk', lb=0, ub=self.cap_max_kwk)
            self.q_w = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_w', lb=0, ub=self.cap_max_w)
            self.E_g_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_g_d_grid', lb=0, ub=GRB.INFINITY)
            self.E_el_total_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_total_d', lb=0, ub=GRB.INFINITY)
            self.E_el_total_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_total_s', lb=0, ub=GRB.INFINITY)
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
            self.q_E_el_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_E_el_d', lb=0, ub=self.cap_max_e)
            self.q_E_g_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_E_g_d', lb=0, ub=self.cap_max_g)
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
            self.b_E_el_total_d = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_E_el_total_d')
            self.b_E_el_total_s = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_E_el_total_s')
            self.E_el_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_d_grid', lb=0, ub=GRB.INFINITY)
            self.b_oh = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_oh')
            self.P_el_max = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='P_el_max', lb=0, ub=GRB.INFINITY)
            self.OH = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='OH', lb=0, ub=GRB.INFINITY)
            self.E_el_total = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='E_el_total', lb=0, ub=GRB.INFINITY)
            self.epsilon_max = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='epsilon_max', lb=0, ub=GRB.INFINITY)
            self.epsilon_total = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='epsilon_total', lb=0, ub=GRB.INFINITY)
            self.d_t = self.m.addVars(
            rti, vtype=GRB.BINARY, name='d_t')
            
            # Anlegen der Zielfunktion
            self.m.setObjective(gp.quicksum(self.E_el_kwk.x[self.t]*self.c_kwk[i] + self.q_w[i]*self.c_w[i] + self.E_g_d_grid[i] * self.c_E_g_grid[i] + self.E_el_total_d[i]*self.c_E_el_d[i] - self.E_el_total_s[i]*self.e_E_el_s[i] + self.c_net[i] + self.q_hs[i]*self.c_hs[i] + self.q_q_d[i]*self.c_q_d[i] - self.q_q_s[i]*self.e_q_s[i] + self.q_t_d[i]*self.c_t_d[i] - self.q_t_s[i]*self.e_t_s[i]  for i in rti), GRB.MINIMIZE)
            
            # Anlegen der Variablen für die Emissionsbilanzierung
            self.epsilon_average_t = [0]*rti
            self.epsilon_total_t = [0]*rti
            
            # Anlegen der Nebenbedingungen
            for j in rti:
                self.m.addConstr(-(self.M*self.b_ih[j])+self.q_E_g_d[j]+self.q_E_el_d[j]+self.q_w[j] <= self.D_heat[j], name=f'if_production1{j}')
                self.m.addConstr((self.M-self.b_ih[j])+self.q_E_g_d[j]+self.q_E_el_d[j]+self.q_w[j] >= self.D_heat[j], name=f'if_production2{j}')
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
                self.m.addConstr(self.d_t[j]==self.q_E_el_d[j]+self.q_E_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j], name=f'calculate_demand_in_{j}')
                self.m.addConstr(self.d_t[j]<=self.D_heat[j]*(1+self.f_heat), name=f'demand_satisfaction_max{j}')
                self.m.addConstr(self.d_t[j]>=self.D_heat[j]*(1-self.f_heat), name=f'demand_satisfaction_min{j}')
                self.m.addConstr(self.b_t_d[j]*self.M>=self.q_t_d[j], name=f'b_t_d{j}')
                self.m.addConstr(self.b_t_s[j]*self.M>=self.q_t_s[j], name=f'b_t_s{j}')
                self.m.addConstr(self.b_t_d[j]*self.b_t_s[j]<=1, name=f'b_t_d_vs.b_t_s{j}')
                if self.q_E_el_d[j]>0:
                    self.m.addConstr(self.q_E_el_d[j]>=self.cap_min_e, name=f'q_E_el_d_cap_min{j}')
                if self.q_E_g_d[j]>0:
                    self.m.addConstr(self.q_E_g_d[j]>=self.cap_min_g, name=f'q_E_g_d_cap_min{j}')
                if self.E_el_kwk[j]>0:
                    self.m.addConstr(self.E_el_kwk[j]>=self.cap_min_kwk, name=f'E_el_kwk_d_cap_min{j}')    
                if self.q_w[j]>0:
                    self.m.addConstr(self.q_w[j]>=self.cap_min_w, name=f'q_w_d_cap_min{j}')   
                self.m.addConstr(self.E_el_d_grid[j]==self.q_E_el_d[j]*self.const_E_el_to_h, name=f'q_E_el_d -> E_el_d_grid{j}')
                self.m.addConstr(self.E_g_d_grid[j]==self.q_E_g_d[j]*self.const_E_g_to_h, name=f'q_E_g_d -> E_g_d_grid{j}')
                self.m.addConstr(self.E_el_total_d[j]-self.E_el_total_s[j]==self.E_el_d_grid[j]+self.E_el_res[j]-self.E_el_pv[j]-self.E_el_kwk[j], f'calculate_E_el_total{j}')
                self.m.addConstr(self.b_E_el_total_d[j]*self.M>=self.E_el_total_d[j], name=f'b_E_el_total_d{j}')
                self.m.addConstr(self.b_E_el_total_s[j]*self.M>=self.E_el_total_s[j], name=f'b_E_el_total_s{j}')
                self.m.addConstr(self.b_E_el_total_d[j]+self.b_E_el_total_s[j]<=1, name=f'b_E_el_total_d_vs.b_E_el_total_s{j}')
            
            self.m.addConstr(self.E_el_total==gp.quicksum(self.E_el_total_d[j] -self.E_el_total_s[j] for j in rti), name='calculate_E_el_total')
            if min_net_discount or mid_net_discount or max_net_discount:
                self.m.addConstr(self.E_el_total>=1000000, name='E_el_total>=10Gw')
            self.m.addConstr(gp.quicksum((self.q_E_el_d[j]+self.q_E_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j]) for j in rti)>=self.D_heat[j] , name=f'demand_satisfaction_total{j}')
            self.m.addConstr(self.P_el_max==np.max(self.E_el_total_d), name='calculate_P_el_max') # Wie berechnen wir die Maximallast je Periode?
            self.m.addConstr(self.OH==self.E_el_total/self.P_el_max, name='calculate_OH')
            if no_net_dicount:
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max), name='calculate_c_net')
            if min_net_discount:
                self.m.addConstr(self.OH>=7000, name='OH>=7000')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.2, name='calculate_c_net')
            if mid_net_discount:
                self.m.addConstr(self.OH>=7500, name='OH>=7500')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.15, name='calculate_c_net')
            if max_net_discount:
                self.m.addConstr(self.OH>=8000, name='OH>=8000')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.1, name='calculate_c_net')
            self.m.addConstr(self.epsilon_max == self.epsilon_max_kWh*gp.quicksum(self.q_E_el_d[i]+self.q_E_g_d[i]+self.q_q_d[i]+self.q_t_d[i]+self.q_w[i] for i in rti), name='calculate_epsilon_max')
            self.m.addConstr(self.epsilon_total== gp.quicksum((self.E_el_total_d[i]-self.E_el_total_s[i])*self.epsilon_E_el[i]+self.E_g_d_grid[i]*self.epsilon_g[i]+self.E_el_kwk[i]*self.epsilon_kwk[i]+self.q_w[i]*self.epsilon_w[i]+self.q_q_d[i]*self.epsilon_q[i]+self.q_t_d[i]*self.epsilon_t[i] for i in rti), name='check_epsilon_max')
            self.m.addConstr(self.epsilon_max >= self.epsilon_total, name='check_epsilon_max')
            return
        
        # Methode zur Initialisierung des Optimierungsmodells, falls zweite Periode (Index = 1)
        def setup_model_t2(self, no_net_dicount, min_net_discount, mid_net_discount, max_net_discount):
            # Anlegen Zeitindex
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # Anpassen der Kosten-/ Erlösparameter des P2P-Handels für die zweite (Index = 1) -> Annahme: ex ante Kosten-/ Erlösparameter der Vorperiode werden für die Planung der aktuellen Periode verwendet
            self.c_q_d[1]= self.results_P2P_trading[0][2]
            self.e_q_s[1]= self.results_P2P_trading[0][2]
            
            # Initialisierung des Modells
            self.m = gp.Model(f'industry_{self.unique_id}')
            self.m.Params.OutputFlag = 0 #Output-Parameter werden nicht ausgegeben, wenn 0
            
            # Anlegen der Entscheidungsvariablen
            # m.addVars mit Zeitindex rti -> Die EV wird als Array mit Eintrag für jede Periode angelegt
            # m.addVar -> eine einzelne EV für der Gesamtzeitraum
            self.E_el_kwk = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_kwk', lb=0, ub=self.cap_max_kwk)
            self.q_w = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_w', lb=0, ub=self.cap_max_w)
            self.E_g_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_g_d_grid', lb=0, ub=GRB.INFINITY)
            self.E_el_total_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_total_d', lb=0, ub=GRB.INFINITY)
            self.E_el_total_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_total_s', lb=0, ub=GRB.INFINITY)
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
            self.q_E_el_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_E_el_d', lb=0, ub=self.cap_max_e)
            self.q_E_g_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_E_g_d', lb=0, ub=self.cap_max_g)
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
            self.b_E_el_total_d = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_E_el_total_d')
            self.b_E_el_total_s = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_E_el_total_s')
            self.E_el_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_d_grid', lb=0, ub=GRB.INFINITY)
            self.b_oh = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_oh')
            self.P_el_max = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='P_el_max', lb=0, ub=GRB.INFINITY)
            self.OH = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='OH', lb=0, ub=GRB.INFINITY)
            self.E_el_total = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='E_el_total', lb=0, ub=GRB.INFINITY)
            self.epsilon_max = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='epsilon_max', lb=0, ub=GRB.INFINITY)
            self.epsilon_total = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='epsilon_total', lb=0, ub=GRB.INFINITY)
            self.d_t = self.m.addVars(
            rti, vtype=GRB.BINARY, name='d_t')

            # Anlegen der Zielfunktion
            self.m.setObjective(gp.quicksum(self.E_el_kwk[i]*self.c_kwk[i] + self.q_w[i]*self.c_w[i] + self.E_g_d_grid[i] * self.c_E_g_grid[i] + self.E_el_total_d[i]*self.c_E_el_d[i] - self.E_el_total_s[i]*self.e_E_el_s[i] + self.c_net[i] + self.q_hs[i]*self.c_hs[i] + self.q_q_d[i]*self.c_q_d[i] - self.q_q_s[i]*self.e_q_s[i] + self.q_t_d[i]*self.c_t_d[i] - self.q_t_s[i]*self.e_t_s[i]  for i in rti), GRB.MINIMIZE)
            
            # Anlegen der Variablen für die Emissionsbilanzierung 
            self.epsilon_average_t = [0]*rti
            self.epsilon_total_t = [0]*rti
            
            # Anlegen der Nebenbedingungen
            for j in rti:
                self.m.addConstr(-(self.M*self.b_ih[j])+self.q_E_g_d[j]+self.q_E_el_d[j]+self.q_w[j] <= self.D_heat[j], name=f'if_production1{j}')
                self.m.addConstr((self.M-self.b_ih[j])+self.q_E_g_d[j]+self.q_E_el_d[j]+self.q_w[j] >= self.D_heat[j], name=f'if_production2{j}')
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
                self.m.addConstr(self.d_t[j]==self.q_E_el_d[j]+self.q_E_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j], name=f'calculate_demand_in_{j}')
                self.m.addConstr(self.d_t[j]<=self.D_heat[j]*(1+self.f_heat), name=f'demand_satisfaction_max{j}')
                self.m.addConstr(self.d_t[j]>=self.D_heat[j]*(1-self.f_heat), name=f'demand_satisfaction_min{j}')
                self.m.addConstr(self.b_t_d[j]*self.M>=self.q_t_d[j], name=f'b_t_d{j}')
                self.m.addConstr(self.b_t_s[j]*self.M>=self.q_t_s[j], name=f'b_t_s{j}')
                self.m.addConstr(self.b_t_d[j]*self.b_t_s[j]<=1, name=f'b_t_d_vs.b_t_s{j}')
                if self.q_E_el_d[j]>0:
                    self.m.addConstr(self.q_E_el_d[j]>=self.cap_min_e, name=f'q_E_el_d_cap_min{j}')
                if self.q_E_g_d[j]>0:
                    self.m.addConstr(self.q_E_g_d[j]>=self.cap_min_g, name=f'q_E_g_d_cap_min{j}')
                if self.E_el_kwk[j]>0:
                    self.m.addConstr(self.E_el_kwk[j]>=self.cap_min_kwk, name=f'E_el_kwk_d_cap_min{j}')    
                if self.q_w[j]>0:
                    self.m.addConstr(self.q_w[j]>=self.cap_min_w, name=f'q_w_d_cap_min{j}')   
                self.m.addConstr(self.E_el_d_grid[j]==self.q_E_el_d[j]*self.const_E_el_to_h, name=f'q_E_el_d -> E_el_d_grid{j}')
                self.m.addConstr(self.E_g_d_grid[j]==self.q_E_g_d[j]*self.const_E_g_to_h, name=f'q_E_g_d -> E_g_d_grid{j}')
                self.m.addConstr(self.E_el_total_d[j]-self.E_el_total_s[j]==self.E_el_d_grid[j]+self.E_el_res[j]-self.E_el_pv[j]-self.E_el_kwk[j], f'calculate_E_el_total{j}')
                self.m.addConstr(self.b_E_el_total_d[j]*self.M>=self.E_el_total_d[j], name=f'b_E_el_total_d{j}')
                self.m.addConstr(self.b_E_el_total_s[j]*self.M>=self.E_el_total_s[j], name=f'b_E_el_total_s{j}')
                self.m.addConstr(self.b_E_el_total_d[j]+self.b_E_el_total_s[j]<=1, name=f'b_E_el_total_d_vs.b_E_el_total_s{j}')
            
            self.m.addConstr(self.E_el_total==gp.quicksum(self.E_el_total_d[j] -self.E_el_total_s[j] for j in rti), name='calculate_E_el_total')
            if min_net_discount or mid_net_discount or max_net_discount:
                self.m.addConstr(self.E_el_total>=1000000, name='E_el_total>=10Gw')
            self.m.addConstr(gp.quicksum((self.q_E_el_d[j]+self.q_E_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j]) for j in rti)>=self.D_heat[j] , name=f'demand_satisfaction_total{j}')
            self.m.addConstr(self.P_el_max==np.max(self.E_el_total_d), name='calculate_P_el_max') # Wie berechnen wir die Maximallast je Periode?
            self.m.addConstr(self.OH==self.E_el_total/self.P_el_max, name='calculate_OH')
            if no_net_dicount:
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max), name='calculate_c_net')
            if min_net_discount:
                self.m.addConstr(self.OH>=7000, name='OH>=7000')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.2, name='calculate_c_net')
            if mid_net_discount:
                self.m.addConstr(self.OH>=7500, name='OH>=7500')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.15, name='calculate_c_net')
            if max_net_discount:
                self.m.addConstr(self.OH>=8000, name='OH>=8000')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.1, name='calculate_c_net')
            self.m.addConstr(self.epsilon_max == self.epsilon_max_kWh*gp.quicksum(self.q_E_el_d[i]+self.q_E_g_d[i]+self.q_q_d[i]+self.q_t_d[i]+self.q_w[i] for i in rti), name='calculate_epsilon_max')
            self.m.addConstr(self.epsilon_total== gp.quicksum((self.E_el_total_d[i]-self.E_el_total_s[i])*self.epsilon_E_el[i]+self.E_g_d_grid[i]*self.epsilon_g[i]+self.E_el_kwk[i]*self.epsilon_kwk[i]+self.q_w[i]*self.epsilon_w[i]+self.q_q_d[i]*self.epsilon_q[i]+self.q_t_d[i]*self.epsilon_t[i] for i in rti), name='check_epsilon_max')
            self.m.addConstr(self.epsilon_max >= self.epsilon_total, name='check_epsilon_max')
            
            # Fixierung des Bedarfs und der P2P-Handelsmengen für die erste Periode (Index = 0)
            self.m.addConstr(self.d_t[0]==self.results_Unternehmen[0][27])
            self.m.addConstr(self.q_q_d[0]==self.results_Unternehmen[0][7])
            self.m.addConstr(self.q_q_s[0]==self.results_Unternehmen[0][8])
            return
        
        # Methode zur Initialisierung des Optimierungsmodells ab der dritten Periode (Index >= 2)
        def setup_model_t3(self, no_net_dicount, min_net_discount, mid_net_discount, max_net_discount):
            # Anlegen Zeitindex
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # Anpassen der Kosten-/ Erlösparameter des P2P-Handels für alle Vorperioden mit Index > 0-> Annahme: ex ante Kosten-/ Erlösparameter der Vorperiode werden für die Planung der aktuellen Periode verwendet
            for i in range(1, self.t+1):
                self.c_q_d[i]= self.results_P2P_trading[i-1][2]
                self.e_q_s[i]= self.results_P2P_trading[i-1][2]
            
            # Initialisierung des Modells
            self.m = gp.Model(f'industry_{self.unique_id}')
            self.m.Params.OutputFlag = 0 #Output-Parameter werden nicht ausgegeben, wenn 0
            
            # Anlegen der Entscheidungsvariablen
            # m.addVars mit Zeitindex rti -> Die EV wird als Array mit Eintrag für jede Periode angelegt
            # m.addVar -> eine einzelne EV für der Gesamtzeitraum
            self.E_el_kwk = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_kwk', lb=0, ub=self.cap_max_kwk)
            self.q_w = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_w', lb=0, ub=self.cap_max_w)
            self.E_g_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_g_d_grid', lb=0, ub=GRB.INFINITY)
            self.E_el_total_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_total_d', lb=0, ub=GRB.INFINITY)
            self.E_el_total_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_total_s', lb=0, ub=GRB.INFINITY)
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
            self.q_E_el_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_E_el_d', lb=0, ub=self.cap_max_e)
            self.q_E_g_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_E_g_d', lb=0, ub=self.cap_max_g)
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
            self.b_E_el_total_d = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_E_el_total_d')
            self.b_E_el_total_s = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_E_el_total_s')
            self.E_el_d_grid = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='E_el_d_grid', lb=0, ub=GRB.INFINITY)
            self.b_oh = self.m.addVars(
            rti, vtype=GRB.BINARY, name='b_oh')
            self.P_el_max = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='P_el_max', lb=0, ub=GRB.INFINITY)
            self.OH = self.m.addVars(
            rti, vtype=GRB.CONTINUOUS, name='OH', lb=0, ub=GRB.INFINITY)
            self.E_el_total = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='E_el_total', lb=0, ub=GRB.INFINITY)
            self.epsilon_max = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='epsilon_max', lb=0, ub=GRB.INFINITY)
            self.epsilon_total = self.m.addVar(
            vtype=GRB.CONTINUOUS, name='epsilon_total', lb=0, ub=GRB.INFINITY)
            self.d_t = self.m.addVars(
            rti, vtype=GRB.BINARY, name='d_t')

            # Anlegen der Zielfunktion
            self.m.setObjective(gp.quicksum(self.E_el_kwk[i]*self.c_kwk[i] + self.q_w[i]*self.c_w[i] + self.E_g_d_grid[i] * self.c_E_g_grid[i] + self.E_el_total_d[i]*self.c_E_el_d[i] - self.E_el_total_s[i]*self.e_E_el_s[i] + self.c_net[i] + self.q_hs[i]*self.c_hs[i] + self.q_q_d[i]*self.c_q_d[i] - self.q_q_s[i]*self.e_q_s[i] + self.q_t_d[i]*self.c_t_d[i] - self.q_t_s[i]*self.e_t_s[i]  for i in rti), GRB.MINIMIZE)
            
            # Anlegen der Variablen für die Emissionsbilanzierung
            self.epsilon_average_t = [0]*rti
            self.epsilon_total_t = [0]*rti
            
            # Anlegen der Nebenbedingungen    
            for j in rti:
                self.m.addConstr(-(self.M*self.b_ih[j])+self.q_E_g_d[j]+self.q_E_el_d[j]+self.q_w[j] <= self.D_heat[j], name=f'if_production1{j}')
                self.m.addConstr((self.M-self.b_ih[j])+self.q_E_g_d[j]+self.q_E_el_d[j]+self.q_w[j] >= self.D_heat[j], name=f'if_production2{j}')
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
                self.m.addConstr(self.d_t[j]==self.q_E_el_d[j]+self.q_E_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j], name=f'calculate_demand_in_{j}')
                self.m.addConstr(self.d_t[j]<=self.D_heat[j]*(1+self.f_heat), name=f'demand_satisfaction_max{j}')
                self.m.addConstr(self.d_t[j]>=self.D_heat[j]*(1-self.f_heat), name=f'demand_satisfaction_min{j}')
                self.m.addConstr(self.b_t_d[j]*self.M>=self.q_t_d[j], name=f'b_t_d{j}')
                self.m.addConstr(self.b_t_s[j]*self.M>=self.q_t_s[j], name=f'b_t_s{j}')
                self.m.addConstr(self.b_t_d[j]*self.b_t_s[j]<=1, name=f'b_t_d_vs.b_t_s{j}')
                if self.q_E_el_d[j]>0:
                    self.m.addConstr(self.q_E_el_d[j]>=self.cap_min_e, name=f'q_E_el_d_cap_min{j}')
                if self.q_E_g_d[j]>0:
                    self.m.addConstr(self.q_E_g_d[j]>=self.cap_min_g, name=f'q_E_g_d_cap_min{j}')
                if self.E_el_kwk[j]>0:
                    self.m.addConstr(self.E_el_kwk[j]>=self.cap_min_kwk, name=f'E_el_kwk_d_cap_min{j}')    
                if self.q_w[j]>0:
                    self.m.addConstr(self.q_w[j]>=self.cap_min_w, name=f'q_w_d_cap_min{j}')   
                self.m.addConstr(self.E_el_d_grid[j]==self.q_E_el_d[j]*self.const_E_el_to_h, name=f'q_E_el_d -> E_el_d_grid{j}')
                self.m.addConstr(self.E_g_d_grid[j]==self.q_E_g_d[j]*self.const_E_g_to_h, name=f'q_E_g_d -> E_g_d_grid{j}')
                self.m.addConstr(self.E_el_total_d[j]-self.E_el_total_s[j]==self.E_el_d_grid[j]+self.E_el_res[j]-self.E_el_pv[j]-self.E_el_kwk[j], f'calculate_E_el_total{j}')
                self.m.addConstr(self.b_E_el_total_d[j]*self.M>=self.E_el_total_d[j], name=f'b_E_el_total_d{j}')
                self.m.addConstr(self.b_E_el_total_s[j]*self.M>=self.E_el_total_s[j], name=f'b_E_el_total_s{j}')
                self.m.addConstr(self.b_E_el_total_d[j]+self.b_E_el_total_s[j]<=1, name=f'b_E_el_total_d_vs.b_E_el_total_s{j}')
            
            self.m.addConstr(self.E_el_total==gp.quicksum(self.E_el_total_d[j] -self.E_el_total_s[j] for j in rti), name='calculate_E_el_total')
            if min_net_discount or mid_net_discount or max_net_discount:
                self.m.addConstr(self.E_el_total>=1000000, name='E_el_total>=10Gw')
            self.m.addConstr(gp.quicksum((self.q_E_el_d[j]+self.q_E_g_d[j]+self.q_q_d[j]+self.q_t_d[j]+self.q_w[j]-self.q_q_s[j]-self.q_t_s[j]-self.q_hs[j]) for j in rti)>=self.D_heat[j] , name=f'demand_satisfaction_total{j}')
            self.m.addConstr(self.P_el_max==np.max(self.E_el_total_d), name='calculate_P_el_max') # Wie berechnen wir die Maximallast je Periode?
            self.m.addConstr(self.OH==self.E_el_total/self.P_el_max, name='calculate_OH')
            if no_net_dicount:
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max), name='calculate_c_net')
            if min_net_discount:
                self.m.addConstr(self.OH>=7000, name='OH>=7000')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.2, name='calculate_c_net')
            if mid_net_discount:
                self.m.addConstr(self.OH>=7500, name='OH>=7500')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.15, name='calculate_c_net')
            if max_net_discount:
                self.m.addConstr(self.OH>=8000, name='OH>=8000')
                self.m.addConstr(self.c_net==(self.c_kWh*self.E_el_total + self.c_dr*self.P_el_max)*0.1, name='calculate_c_net')
            self.m.addConstr(self.epsilon_max == self.epsilon_max_kWh*gp.quicksum(self.q_E_el_d[i]+self.q_E_g_d[i]+self.q_q_d[i]+self.q_t_d[i]+self.q_w[i] for i in rti), name='calculate_epsilon_max')
            self.m.addConstr(self.epsilon_total== gp.quicksum((self.E_el_total_d[i]-self.E_el_total_s[i])*self.epsilon_E_el[i]+self.E_g_d_grid[i]*self.epsilon_g[i]+self.E_el_kwk[i]*self.epsilon_kwk[i]+self.q_w[i]*self.epsilon_w[i]+self.q_q_d[i]*self.epsilon_q[i]+self.q_t_d[i]*self.epsilon_t[i] for i in rti), name='check_epsilon_max')
            self.m.addConstr(self.epsilon_max >= self.epsilon_total, name='check_epsilon_max')
            
            # Fixierung des Bedarfs und der P2P-Handelsmengen für die der direkten Vorperiode
            self.m.addConstr(self.d_t[self.t-1]==self.results_Unternehmen[self.t-1][28])
            self.m.addConstr(self.q_q_d[self.t-1]==self.results_Unternehmen[self.t-1][7])
            self.m.addConstr(self.q_q_s[self.t-1]==self.results_Unternehmen[self.t-1][8])
            
            # Fixierung aller Entscheidungsvariablen der indirekten Vorperioden
            for i in range(0, self.t-1):
                # Alle Entscheidungsvariablen der Vorperioden fixieren
                self.m.addConstr(self.E_el_kwk[i]==self.results_Unternehmen[i][0])
                self.m.addConstr(self.q_w[i]==self.results_Unternehmen[i][1])
                self.m.addConstr(self.E_g_d_grid[i]==self.results_Unternehmen[i][2])
                self.m.addConstr(self.E_el_total_d[i]==self.results_Unternehmen[i][3])
                self.m.addConstr(self.E_el_total_s[i]==self.results_Unternehmen[i][4])
                self.m.addConstr(self.q_hs[i]==self.results_Unternehmen[i][5])
                self.m.addConstr(self.c_net[i]==self.results_Unternehmen[i][6])
                self.m.addConstr(self.q_q_d[i]==self.results_Unternehmen[i][7])
                self.m.addConstr(self.q_q_s[i]==self.results_Unternehmen[i][8])
                self.m.addConstr(self.q_t_d[i]==self.results_Unternehmen[i][9])
                self.m.addConstr(self.q_t_s[i]==self.results_Unternehmen[i][10])
                self.m.addConstr(self.q_E_el_d[i]==self.results_Unternehmen[i][11])
                self.m.addConstr(self.q_E_g_d[i]==self.results_Unternehmen[i][12])
                self.m.addConstr(self.b_ih[i]==self.results_Unternehmen[i][13])
                self.m.addConstr(self.b_q_d[i]==self.results_Unternehmen[i][14])
                self.m.addConstr(self.b_q_s[i]==self.results_Unternehmen[i][15])
                self.m.addConstr(self.b_t_d[i]==self.results_Unternehmen[i][16])
                self.m.addConstr(self.b_t_s[i]==self.results_Unternehmen[i][17])
                self.m.addConstr(self.b_E_el_total_d[i]==self.results_Unternehmen[i][18])
                self.m.addConstr(self.b_E_el_total_s[i]==self.results_Unternehmen[i][19])
                self.m.addConstr(self.E_el_d_grid[i]==self.results_Unternehmen[i][20])
                self.m.addConstr(self.b_oh[i]==self.results_Unternehmen[i][21])
                self.m.addConstr(self.P_el_max[i]==self.results_Unternehmen[i][22])
                self.m.addConstr(self.OH[i]==self.results_Unternehmen[i][23])
                self.m.addConstr(self.E_el_total[i]==self.results_Unternehmen[i][24])
                self.m.addConstr(self.epsilon_max[i]==self.results_Unternehmen[i][25])
                self.m.addConstr(self.epsilon_total[i]==self.results_Unternehmen[i][26])
                self.m.addConstr(self.d_t[i]==self.results_Unternehmen[i][27])
            return
        
        # Berechnung der Emissione
        def calculate_epsilon(self, epsilon_average_q, i, q_s, q_d):
            self.epsilon_total_t[i] = (self.E_el_total_d[i]-self.E_el_total_s)*self.epsilon_E_el[i]+self.E_g_d_grid[i]*self.epsilon_g[i]+self.E_el_kwk[i]*self.epsilon_kwk[i]+self.q_w[i]*self.epsilon_w[i]+self.q_t_d[i]*self.epsilon_t[i]+epsilon_average_q*q_d-epsilon_average_q*q_s
            self.epsilon_average_t[i] = self.epsilon_total_t[i]/(self.q_E_el_d[i]+self.q_E_g_d[i]+self.q_t_d[i]+self.q_w[i]+q_d-q_s)
            return self.epsilon_average_t[i]
        
        # Schritt-Funktion zur Durchführung eines Zeitschritts
        def step(self):
            # Anlegen einer leeren Variable für die Ergebnisse
            self.results = []
            
            # Initialisierung des Modells für alle vier Szenarien bei der Netzentgeltberechnung
            if self.t==0:
                self.setup_model_t1(True, False, False, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t1(False, True, False, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t1(False, False, True, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t1(False, False, False, True)
                result = self.run_model()
            elif self.t==1:
                self.setup_model_t2(True, False, False, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t2(False, True, False, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t2(False, False, True, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t2(False, False, False, True)
                result = self.run_model()
            else:
                self.setup_model_t3(True, False, False, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t3(False, True, False, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t3(False, False, True, False)
                result = self.run_model()
                self.results.append(result)
                self.setup_model_t3(False, False, False, True)
                result = self.run_model()
                self.results.append(result)
            
            # Bestimmung des Szanarios der Netzentgeltberechnung mit den geringsten Gesamtkosten
            opt_list = self.results[0][1], self.results[1][1], self.results[2][1], self.results[3][1]
            min_value = min(opt_list)
            min_index = opt_list.index(min_value)
            self.opt = self.results[min_index][0]
            return
        
        # Methode zur Rückgabe des Optimums
        def get_opt(self):
            return self.opt
        
        # Methode zur Rückgabe der Kosten der Abwärmenutzung
        def get_c_w(self):
            return self.c_w
        
        # Methode zur Rückgabe der Stromkosten je kWh
        def get_c_E_el_d(self):
            return self.c_E_el_d
        
        # Methode zur Rückgabe der Konstante zur Umrechnung von Strom- in Wärmemenge
        def get_const_E_el_to_h(self):
            return self.const_E_el_to_h
        
        # Methode zur Rückgabe der Gaskosten je kWh
        def get_c_E_g_grid(self):
            return self.c_E_g_grid
        
        # Methode zur Rückgabe der Konstante zur Umrechnung von Gas- in Wärmemenge
        def get_const_E_g_to_h(self):
            return self.const_E_g_to_h
        
        # Methode zur Rückgabe der Kosten der Fernwärme je kWh
        def get_c_t_d(self):
            return self.c_t_d
        
        # Methode zur Rückgabe der Kosten des P2P-Handels je kWh
        def get_c_q_d(self):
            return self.c_q_d
        
        # Optimierung zum Lösen des Modells
        def run_model(self):
            # Optimierung des Modells ausführen
            self.m.optimize()
            
            # Rückgabe der Ergebnisse, falls Optimium gefunden
            if self.m.status == GRB.OPTIMAL:
                print("Optimal solution found.")
                # Get values of decision variables                
                results = [self.E_el_kwk.x[self.t], self.q_w.x[self.t], self.E_g_d_grid.x[self.t], self.E_el_total_d.x[self.t], self.E_el_total_s.x[self.t], self.q_hs.x[self.t], self.c_net.x[self.t], self.q_q_d.x[self.t], self.q_q_s.x[self.t], self.q_t_d.x[self.t], self.q_t_s.x[self.t], self.q_E_el_d.x[self.t], self.q_E_g_d.x[self.t], self.b_ih.x[self.t], self.b_q_d.x[self.t], self.b_q_s.x[self.t], self.b_t_d.x[self.t], self.b_t_s.x[self.t], self.b_E_el_total_d.x[self.t], self.b_E_el_total_s.x[self.t], self.E_el_d_grid.x[self.t], self.b_oh.x[self.t], self.P_el_max.x[self.t], self.OH.x[self.t], self.E_el_total.x[self.t], self.epsilon_max.x[self.t], self.epsilon_total.x[self.t], self.d_t.x[self.t]]                
                #results = np.array([var.X for var in self.m.getVars()]) #Format: results[Entscheidungsvariable][Zeitindex]
                value_target = self.m.ObjVal
                return [results, value_target]
            # Rückgabe von None-Werten bzw. M als Parameter für hinreichend hohe Kosten, dass das Ergebnis nicht berücksichtigt wird, falls kein Optimium gefunden
            else:
                print("Optimization did not converge to an optimal solution.")
                self.m.computeIIS()
                self.m.write("model.ilp")
                return None, self.M