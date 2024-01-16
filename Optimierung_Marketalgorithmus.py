# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 15:30:04 2024

@author: juliu
"""

import mesa
import numpy as np
import gurobipy as gp
from gurobipy import GRB
import Transformation_Nachfragefunktion_class

class MarketClearingOptimazation():
        def __init__(self):
#class MarketClearingOptimazation(mesa.Agent):
        #def __init__(self, unique_id, mode):   
            #super().__init__()
            # non-decision variables, used for tracking results
            transformation = Transformation_Nachfragefunktion_class.Transformation()
            self.vol_d = transformation.demand_vol #[24500.0, 12000.0, 8000.0, 7850.0, 6350.0, 6250.0, 4750.0]
            self.vol_s = transformation.supply_vol #[8010.0, 8010.0, 8010.0, 8010.0, 8010.0, 8010.0, 8010.0] 
            self.demand_MAN = transformation.demand_MAN #[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            self.supply_MAN = transformation.supply_MAN #[1010.0, 1010.0, 1010.0, 1010.0, 1010.0, 1010.0, 1010.0]
            self.demand_MTA = transformation.demand_MTA #[7500.0, 7500.0, 3500.0, 3500.0, 2000.0, 1900.0, 1900.0]
            self.supply_MTA = transformation.supply_MTA #[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            self.demand_UPM = transformation.demand_UPM #[15000.0, 2500.0, 2500.0, 2350.0, 2350.0, 2350.0, 850.0]
            self.supply_UPM = transformation.supply_UPM #[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            self.demand_storage = transformation.demand_storage #2000.0
            self.supply_storage = transformation.supply_storage #7000.0
            self.vol_max = transformation.vol_max #[8010.0, 8010.0, 8000.0, 7850.0, 6350.0, 6250.0, 4750.0]
            self.price_levels = transformation.price_levels #[4.8, 5.5, 6.0, 6.5, 7.0, 7.5, 13.0]
            self.p_tele_d = 12 #self.model.database.optimization_parameter['p_tele_d']
            self.p_tele_s = 5 #self.model.database.optimization_parameter['p_tele_s']
            self.p_fees = 0.01 #self.model.database.optimization_parameter['p_fees']
            self.cap_MAN = 10000.0 #self.model.database.optimization_parameter['cap_MAN']
            self.cap_MTA = 7500.0 #self.model.database.optimization_parameter['cap_MTA']
            self.cap_UPM = 15000.0 #self.model.database.optimization_parameter['cap_UPM']
            self.cap_storage = 15000.0 #self.model.database.optimization_parameter['cap_storage']

            self.setup_model()
            
        def update_data(self):
            #code
            return
            
        def setup_model(self):
            self.results = []
            for i in range(len(self.price_levels)):
                if self.price_levels[i] < self.p_tele_s + self.p_fees:
                    continue
                if self.price_levels[i] > self.p_tele_d:
                    continue
                self.m = gp.Model()
                # decision variables, used in optimization
                self.vol = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol', lb=0, ub=GRB.INFINITY)
                #self.p = self.m.addVar(
                #    vtype=GRB.CONTINUOUS, name='p', lb=0, ub=GRB.INFINITY)
                self.ratio_d = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='ratio_d', lb=0, ub=GRB.INFINITY)
                self.ratio_s = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='ratio_s', lb=0, ub=GRB.INFINITY)
                self.vol_d_MAN = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol_d_MAN', lb=0, ub=GRB.INFINITY)
                self.vol_s_MAN = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol_s_MAN', lb=0, ub=GRB.INFINITY)
                self.vol_d_MTA = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol_d_MTA', lb=0, ub=GRB.INFINITY)
                self.vol_s_MTA = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol_s_MTA', lb=0, ub=GRB.INFINITY)
                self.vol_d_UPM = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol_d_UPM', lb=0, ub=GRB.INFINITY)
                self.vol_s_UPM = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol_s_UPM', lb=0, ub=GRB.INFINITY)
                self.vol_d_storage = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol_d_storage', lb=0, ub=GRB.INFINITY)
                self.vol_s_storage = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol_s_storage', lb=0, ub=GRB.INFINITY)
                
                self.p = self.price_levels[i]
                vol_max = self.vol_max[i]
                vol_d=self.vol_d[i]
                vol_s=self.vol_s[i]
                demand_MAN = self.demand_MAN[i]
                supply_MAN = self.supply_MAN[i]
                demand_MTA = self.demand_MTA[i]
                supply_MTA = self.supply_MTA[i]
                demand_UPM = self.demand_UPM[i]
                supply_UPM = self.supply_UPM[i]
                # market model
                #self.m = gp.Model(f'storage_{self.unique_id}')
                self.m.Params.OutputFlag = 0
                # target funktion
                self.m.setObjective(self.vol*self.p, GRB.MAXIMIZE)
    
                # constraints            
                self.m.addConstr(self.vol <= vol_max, name='set_vol_max')
                self.m.addConstr(self.ratio_d == self.vol/vol_d)
                self.m.addConstr(self.ratio_s == self.vol/ vol_s)
                
                self.m.addConstr(self.vol_d_MAN==self.ratio_d*demand_MAN)
                self.m.addConstr(self.vol_s_MAN==self.ratio_s*supply_MAN)
                self.m.addConstr(self.vol_d_MTA==self.ratio_d*demand_MTA)
                self.m.addConstr(self.vol_s_MTA==self.ratio_s*supply_MTA)
                self.m.addConstr(self.vol_d_UPM==self.ratio_d*demand_UPM)
                self.m.addConstr(self.vol_s_UPM==self.ratio_s*supply_UPM)
                self.m.addConstr(self.vol_d_storage==self.ratio_d*self.demand_storage)
                self.m.addConstr(self.vol_s_storage==self.ratio_s*self.supply_storage)
                self.m.addConstr(self.vol_d_MAN<=self.cap_MAN)
                self.m.addConstr(self.vol_s_MAN<=self.cap_MAN)
                self.m.addConstr(self.vol_d_MTA<=self.cap_MTA)
                self.m.addConstr(self.vol_s_MTA<=self.cap_MTA)
                self.m.addConstr(self.vol_d_UPM<=self.cap_UPM)
                self.m.addConstr(self.vol_s_UPM<=self.cap_UPM)
                self.m.addConstr(self.vol_d_storage<=self.cap_storage)
                self.m.addConstr(self.vol_s_storage<=self.cap_storage)
                self.results.append(self.run_model(i))

            # Bestimmung des optimalen Preisniveaus durch absteigende Sortierung der einzelnen Ergebnisse nach Handelsvolumen (Volumen * Preis) und Speicherung des 0. Elements
            self.results = np.array(self.results)
            self.results = self.results[self.results[:, 0].argsort()[::-1]]
            # Optimales Ergebnis in folgender Form als np Array: Handelsvolumen, Index des Preisviveaus, Preisviveau, gehandelte Wärmemenge, gekaufte Wärmemenge MAN, verkaufte Wärmemenge MAN, gekaufte Wärmemenge MTA, verkaufte Wärmemenge MTA, gekaufte Wärmemenge UPM, verkaufte Wärmemenge UPM, gekaufte Wärmemenge Speicher, verkaufte Wärmemenge Speicher
            self.optimales_Ergebnis=self.results[0]
            print(self.optimales_Ergebnis)
            return
                
        
        def run_model(self, i):
            self.m.optimize()
            if self.m.Status == GRB.OPTIMAL:
                # Erhalten Sie den Endwert von self.vol
                value_target = self.m.ObjVal
                #print("Endwert der Zielfunktion: ", endwert_zielfunktion)
                #print(f"Handelsvolumen: {self.vol.x}")
                #print(f"Marktpreis: {self.p}")
                #print(f"Nachfrage MAN: {self.vol_d_MAN.x}")
                #print(f"Angebot MAN: {self.vol_s_MAN.x}")
                #print(f"Nachfrage MTA: {self.vol_d_MTA.x}")
                #print(f"Angebot MTA: {self.vol_s_MTA.x}")
                #print(f"Nachfrage UPM: {self.vol_d_UPM.x}")
                #print(f"Angebot UPM: {self.vol_s_UPM.x}")
                #print(f"Nachfrage Speicher: {self.vol_d_storage.x}")
                #print(f"Angebot Speicher: {self.vol_s_storage.x}")
                results = [value_target, i, self.p, self.vol.x, self.vol_d_MAN.x, self.vol_s_MAN.x, self.vol_d_MTA.x, self.vol_s_MTA.x, self.vol_d_UPM.x, self.vol_s_UPM.x, self.vol_d_storage.x, self.vol_s_storage.x]
            else:
                #print("Die Optimierung war nicht erfolgreich.")
                #print(f"Gurobi Status: {self.m.Status}")
                results = [0]*12
            # get values of decision variables
            #results = np.array([var.X for var in self.m.getVars() if 'g_d[' in var.VarName] + [var.X for var in self.m.getVars() if 'g_s[' in var.VarName])
            
            return results
        
marketClearingOptimazation = MarketClearingOptimazation()