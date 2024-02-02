# -*- coding: utf-8 -*-
# Importieren der benötigten Bibliotheken und Klassen
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from Transformation_Nachfragefunktion_class import Transformation_Nachfragefunktion_class

class Optimierung_Marktalgotithmus():
        def __init__(self, demand_storage, supply_storage, production_MAN, d_MAN_t, q_MAN_t, production_MTA, d_MTA_t, q_MTA_t, production_UPM, d_UPM_t, q_UPM_t, epsilon_average):  
            #super().__init__()
            # Initialisierung deiner Instanz der Transformation_Nachfragefunktion_class-Klasse zur Transformation der Optimierungsergebnisse zu Nachfrage-/ Angebotsfunktionen
            transformation = Transformation_Nachfragefunktion_class(demand_storage, supply_storage, production_MAN, d_MAN_t, q_MAN_t, production_MTA, d_MTA_t, q_MTA_t, production_UPM, d_UPM_t, q_UPM_t)
            
            # Übernahme der Optimierungsparameter der Tramsformations-Klasse
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
            self.epsilon_average = epsilon_average #[0.200, 0.215, 0.210, 0.190] #[kgCO2eq/kWh]: MAN, MTA, UPM, storage
            
            # Initialisierung des Modells
            self.setup_model()
            return
        
        # Methode zur Initialisierung des Optimierungsmodells
        def setup_model(self):
            # Anlegen eines leeren Array zur Speicherung der Ergebnisse
            self.results = []
            
            # Prüfung für jedes Perisniveau
            for i in range(len(self.price_levels)):
                # Falls Perisniveau < Minimalpreis -> keine Berücksichtigung
                if self.price_levels[i] < self.p_tele_s + self.p_fees:
                    continue
                # Falls Perisniveau > Maximalpreis -> keine Berücksichtigung
                if self.price_levels[i] > self.p_tele_d:
                    continue
                # Sonst: Initialisierung des Modells für das jeweilige Preisniveau
                self.m = gp.Model()
                self.m.Params.OutputFlag = 0 #Output-Parameter werden nicht ausgegeben, wenn 0
                
                # Anlegen der Entscheidungsvariablen
                # m.addVars mit Zeitindex rti -> Die EV wird als Array mit Eintrag für jede Periode angelegt
                # m.addVar -> eine einzelne EV für der Gesamtzeitraum
                self.vol = self.m.addVar(
                    vtype=GRB.CONTINUOUS, name='vol', lb=0, ub=GRB.INFINITY)
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
                
                # Anlegen der Optimierungsparameter
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

                # Anlegen der Zielfunktion
                self.m.setObjective(self.vol*self.p, GRB.MAXIMIZE)
    
                # Anlegen der Nebenbedingungen            
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
                
                # Optimierung für das jeweilige Preisniveau und Speicherung der Ergebnisse
                self.results.append(self.run_model(i))

            # Bestimmung des optimalen Preisniveaus durch absteigende Sortierung der einzelnen Ergebnisse nach Handelsvolumen (Volumen * Preis) und Speicherung des 0. Elements
            self.results = np.array(self.results)
            self.results = self.results[self.results[:, 0].argsort()[::-1]]
            # Optimales Ergebnis in folgender Form als np Array: Handelsvolumen, Index des Preisviveaus, Preisviveau, gehandelte Wärmemenge, gekaufte Wärmemenge MAN, verkaufte Wärmemenge MAN, gekaufte Wärmemenge MTA, verkaufte Wärmemenge MTA, gekaufte Wärmemenge UPM, verkaufte Wärmemenge UPM, gekaufte Wärmemenge Speicher, verkaufte Wärmemenge Speicher
            self.optimales_Ergebnis=self.results[0]
            print(self.optimales_Ergebnis)
            return
        
        # Methode zur Rückgabe der Ergebnisse
        def get_optimales_Ergebnis(self):
            return self.optimales_Ergebnis
        
        # Optimierung zum Lösen des Modells
        def run_model(self, i):
            # Optimierung des Modells ausführen
            self.m.optimize()
            
            # Rückgabe der Ergebnisse, falls Optimium gefunden
            if self.m.Status == GRB.OPTIMAL:
                # Erhalten Sie den Endwert von self.vol
                value_target = self.m.ObjVal
                # Berechnung der durchschnittlichen Emissionen der gehandelten Wärmemenge im Quartier und Speicherung in den results (an Stelle 12)
                self.epsilon_average_q = (self.vol_d_MAN.x * self.epsilon_average[self.t][0] + self.vol_d_MTA.x * self.epsilon_average[self.t][1] + self.vol_d_UPM.x * self.epsilon_average[self.t][2] + self.vol_d_storage.x * self.epsilon_average[self.t][3])/(self.vol_d_MAN.x + self.vol_d_MTA.x + self.vol_d_UPM.x + self.vol_d_storage.x)
                results = [value_target, i, self.p, self.vol.x, self._MAvol_dN.x, self.vol_s_MAN.x, self.vol_d_MTA.x, self.vol_s_MTA.x, self.vol_d_UPM.x, self.vol_s_UPM.x, self.vol_d_storage.x, self.vol_s_storage.x, self.epsilon_average_q]
            # Rückgabe eines Arrays mit 0-Werten, falls kein Optimium gefunden    
            else:
                print("Die Optimierung war nicht erfolgreich.")
                print(f"Gurobi Status: {self.m.Status}")
                results = [0]*13
            return results