# -*- coding: utf-8 -*-
# Importieren der benötigten Bibliotheken
import mesa
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# Klasse für den Storage-Agenten, die von mesa.Agent erbt
class Storage(mesa.Agent):
        def __init__(self, unique_id, model, level_t, storage_results, t):   
            super().__init__()
            
            # Anlegen der Agentenparameter
            self.model = model
            self.unique_id = unique_id
            self.cap_max = self.model.database.optimization_parameter['cap_max']
            self.cap_min = self.model.database.optimization_parameter['cap_min']
            self.efficiency = self.model.database.optimization_parameter['efficiency']
            self.level_t = level_t
            self.t = t
            self.storage_results = storage_results
            self.level_t0 = 0.5*self.cap_max
            self.level_T = 0.5*self.cap_max
            return
        
        # Methode zur Initialisierung des Optimierungsmodells
        def setup_model(self):
            # Anlegen Zeitindex
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # Initialisierung des Modells
            self.m = gp.Model(f'storage_{self.unique_id}')
            self.m.Params.OutputFlag = 0 #Output-Parameter werden nicht ausgegeben, wenn 0
            
            # Anlegen der Entscheidungsvariablen
            # m.addVars mit Zeitindex rti -> Die EV wird als Array mit Eintrag für jede Periode angelegt
            # m.addVar -> eine einzelne EV für der Gesamtzeitraum
            self.q_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_d', lb=0, ub=self.cap_max-self.level_t[self.t])
            self.q_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_s', lb=0, ub=self.level_t[self.t]-self.cap_min)
            self.level_t_post = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='level_t_post')
            
            # Anlegen der Zielfunktion
            self.m.setObjective(gp.quicksum(self.q_d[i] + self.q_s[i] for i in rti), GRB.MAXIMIZE)
            
            # Anlegen der Variablen für die Emissionsbilanzierung
            self.epsilon_average_t = [0]*rti
            self.epsilon_total_t = [0]*rti

            # Anlegen der Nebenbedingungen
            for j in rti:
                self.m.addConstr(self.level_t_post[j] == (self.level_t[j] * self.efficiency + self.q_d[j] - self.q_s[j]), name=f'set_level_next_period_{j}')
                self.m.addConstr(self.q_s[j] <= (self.level_t[j] - self.cap_min), name=f'max_quantity_selling_{j}') 
                self.m.addConstr(self.q_d[j] <= (self.cap_max - self.level_t[j]), name=f'max_quantity_buying_{j}')
            self.m.addConstr(self.level_t_post[len(ti)-1]==self.level_T, name='set_level_last_periode')
            
            # Fixierung der Werte der EVs aller Vorperioden
            if self.t>0:
                for i in range(0, self.t):
                    self.m.addConstr(self.q_d[i-1]==self.storage_results[i][0])
                    self.m.addConstr(self.q_s[i-1]==self.storage_results[i][1])
                    self.m.addConstr(self.level_t_post[i-1]==self.storage_results[i][2])
            return
        # Berechnung der Emissionen
        def calculate_epsilon(self, epsilon_average_q, i, q_s, q_d):
            # Für Anfangsperiode, Annahme: imaginäres Füllen des Speichers durch SWA --> Emissionsparameter des Wärmespeichers = Emissionsparameter der Fermwärme
            if i==0:
                self.epsilon_total[i] = self.model.database.optimization_parameter['e_ih'] * self.level_t0 
                self.epsilon_average[i] = self.model.database.optimization_parameter['e_ih']
            # Für jede weitere Periode: Emissionsmenge am Ende der Periode = Emissionsmenge der Vorperiode + CO2-Äquivalent der gekauften Wärmemenge aus dem Quartiershandel - CO2-Äquivalent der verkauften Wärmemenge aus dem Quartiershandel
            else:    
                self.epsilon_total_t[i] = self.epsilon_average[i-1] * self.level_t[i-1] + epsilon_average_q * q_d - epsilon_average_q * q_s
                self.epsilon_average_t[i] = self.epsilon_total[i]/(self.level_t[i-1] + q_d - q_s)
            return self.epsilon_average_t[i]
        
        # Schritt-Funktion zur Durchführung eines Zeitschritts
        def step(self):
            self.setup_model()
            self.results = self.run_model()
            return
        
        # Methode zur Rückgabe der Ergebnisse
        def get_results(self):
            return self.results
        
        # Optimierung zum Lösen des Modells
        def run_model(self):
            # Optimierung des Modells ausführen
            self.m.optimize()
            
            # Rückgabe der Ergebnisse, falls Optimium gefunden
            if self.m.status == GRB.OPTIMAL:
                print("Optimal solution found.")
                # Get values of decision variables
                #results = np.array([var.X for var in self.m.getVars()])
                demand = self.q_d.x[self.t]
                supply = self.q_s.x[self.t]
                results = demand, supply, self.level_t[self.t] * self.efficiency
                #value_target = self.m.ObjVal
                return results
            # Rückgabe von None-Wert, falls kein Optimium gefunden
            else:
                print("Optimization did not converge to an optimal solution.")
                self.m.computeIIS()
                self.m.write("model.ilp")
                return None