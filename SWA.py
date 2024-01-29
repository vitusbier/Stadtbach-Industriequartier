# -*- coding: utf-8 -*-
# Importieren der benötigten Bibliotheken
import mesa
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# Klasse für den SWA-Agenten, die von mesa.Agent erbt
class SWA(mesa.Agent):
        def __init__(self, unique_id, model, Res_pre, tele_demand, tele_supply, results_SWA, t):   
            super().__init__()
            
            # Anlegen der Agentenparameter
            self.model=model
            self.t=t
            self.Res_pre = Res_pre
            self.tele_demand = tele_demand
            self.tele_supply = tele_supply
            self.results_SWA = results_SWA
            self.cap_max_ih = self.model.database.optimization_parameter['cap_max_ih']
            self.e_q_s = self.model.database.optimization_parameter['e_q_s']
            self.e_t_s = self.model.database.optimization_parameter['e_t_s']
            self.c_ih_d = self.model.database.optimization_parameter['c_ih_d']
            self.c_q_d = self.model.database.optimization_parameter['c_q_d']
            self.epsilon_q = self.model.database.optimization_parameter['epsilon_q']
            self.epsilon_ih = self.model.database.optimization_parameter['epsilon_ih']
            self.epsilon_max_kWh = self.model.database.optimization_parameter['epsilon_max_kWh']

            # Anlegen Zeitindex
            ti = self.model.time_index
            rti = list(range(len(ti)))
            
            # Berechunung der Wärme-Residualmengen des Quartiers aus der Vorperiode
            for i in rti:
                if i<=len(self.Res_pre):
                    continue #Falls für Periode i ein Wert für Res_pre existiert -> keine Veränderung
                else:
                    self.Res_pre.append(self.Res_pre[self.Res_pre-1]) #Falls für Periode i kein Wert für Res_pre existiert -> Annahmen: Res_pre für Periode i = Res_pre der Vorperiode
            return
        
        # Methode zur Initialisierung des Optimierungsmodells
        def setup_model(self):
            # Anlegen Zeitindex
            ti = self.model.timepsilon_index
            rti = list(range(len(ti)))
            
            # Initialisierung des Modells
            self.m = gp.Model(f'storage_{self.unique_id}')
            self.m.Params.OutputFlag = 0 #Output-Parameter werden nicht ausgegeben, wenn 0
            
            # Anlegen der Entscheidungsvariablen
            # m.addVars mit Zeitindex rti -> Die EV wird als Array mit Eintrag für jede Periode angelegt
            # m.addVar -> eine einzelne EV für der Gesamtzeitraum
            self.q_ih_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_ih_d', lb=0, ub=self.cap_max_ih)
            self.q_q_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_q_s', lb=0, ub=GRB.INFINITY)
            self.q_q_d = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_q_d', lb=0, ub=GRB.INFINITY)
            self.q_t_s = self.m.addVars(
                rti, vtype=GRB.CONTINUOUS, name='q_t_s', lb=0, ub=GRB.INFINITY)
            self.epsilon_max = self.m.addVar(
                vtype=GRB.CONTINUOUS, name='epsilon_max', lb=0, ub=GRB.INFINITY)
            self.epsilon_total = self.m.addVar(
                vtype=GRB.CONTINUOUS, name='epsilon_total', lb=0, ub=GRB.INFINITY)
            
            # Anlegen der Zielfunktion
            self.m.setObjective(gp.quicksum(self.q_q_s[i]*self.e_q_s[i]- self.q_t_s[i]*self.e_t_s[i]- self.q_ih_d[i]*self.c_ih_d[i] -self.q_q_d[i]*self.c_q_d[i] for i in rti), GRB.MAXIMIZE)
            
            # Anlegen der Variablen für die Emissionsbilanzierung
            self.epsilon_average_t = [0]*rti
            self.epsilon_total_t = [0]*rti

            # Anlegen der Nebenbedingungen              
            for j in rti:
                if j==0:
                    self.m.addConstr(self.q_q_d[j]>=0, name=f'q_q_d_min_1{j}')
                    self.m.addConstr(self.q_q_s[j]>=0, name=f'q_q_s_min_1{j}')
                elif self.Res_pre >=0:
                    self.m.addConstr(self.q_q_d[j] >= self.Res_pre[j], name=f'q_q_d_min_Res>=0{j}')
                elif self.Res_pre <0:
                    self.m.addConstr(self.q_q_s[j] >= self.Res_pre[j], name=f'q_q_s_min_Res<=0{j}')
            self.m.addConstr(self.epsilon_max==self.epsilon_max_kWh*gp.quicksum(self.q_q_d[j]+self.q_ih_d[j] for j in rti), name='calculation_epsilon_max')
            self.m.addConstr(0<=gp.quicksum(self.q_q_d[j]+self.q_ih_d[j]-self.q_t_s-self.q_q_s for j in rti), name='demand>=supply')
            self.m.addConstr(self.epsilon_total == gp.quicksum(self.q_q_d[j]*self.epsilon_q+self.q_ih_d[j]*self.epsilon_ih[j] for j in rti), name='Emissions')
            self.m.addConstr(self.epsilon_max >= self.epsilon_total, name='check_Emissions')
            
            # Fixierung der Werte der EVs aller Vorperioden
            if self.t ==1:
                # Falls zweite Periode (Index = 1): Fixierung der Handelsmengen für Periode 1 (Index = 0)
                self.m.addConstr(self.q_q_d[0]==self.tele_demand[0])
                self.m.addConstr(self.q_q_s[0]==self.tele_supply[0])
            elif self.t>1:
                for i in range(0, self.t-1):
                    # Alle Entscheidungsvariablen der indirekten Vorperioden fixieren
                    self.m.addConstr(self.q_ih_d[i]==self.results_SWA[i][0])
                    self.m.addConstr(self.q_q_d[i]==self.results_SWA[i][1])
                    self.m.addConstr(self.q_q_s[i]==self.results_SWA[i][2])
                    self.m.addConstr(self.q_t_s[i]==self.results_SWA[i][3])
                    self.m.addConstr(self.epsilon_max[i]==self.results_SWA[i][4])
                    self.m.addConstr(self.epsilon_total[i]==self.results_SWA[i][5])
                # Für direkte Vorperiode: Fixierung der Handelsmengen für Vorperiode    
                self.m.addConstr(self.q_q_d[0]==self.tele_demand[self.t-1])
                self.m.addConstr(self.q_q_s[0]==self.tele_supply[self.t-1])
            return
        
        # Berechnung der Emissionen
        def calculate_epsilon(self, epsilon_average_q, i, q_s, q_d):
            # Emissionen = Emissionen Eigenproduktion + CO2-Äquivalent der gekauften Wärmemenge aus dem Quartiershandel - CO2-Äquivalent der verkauften Wärmemenge aus dem Quartiershandel
            self.epsilon_total_t[i] = self.epsilon_ih[i] * self.q_ih_d[i] + epsilon_average_q * q_d - epsilon_average_q *q_s
            self.epsilon_average_t[i] = self.epsilon_total_t[i]/(self.q_ih_d[i]+q_d-q_s)
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
                results = self.q_ih_d.x[self.t], self.q_q_d.x[self.t], self.q_q_s.x[self.t], self.q_t_s.x[self.t], self.epsilon_max.x[self.t], self.epsilon_total.x[self.t]
                #value_target = self.m.ObjVal
                return results
            # Rückgabe von None-Wert, falls kein Optimium gefunden
            else:
                print("Optimization did not converge to an optimal solution.")
                self.m.computeIIS()
                self.m.write("model.ilp")
                return None