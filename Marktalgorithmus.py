# -*- coding: utf-8 -*-
# Importieren der benötigten Bibliotheken und Klassen
import mesa
import numpy as np
from Optimierung_Marketalgorithmus import Optimierung_Marketalgorithmus
from SWA import SWA
from Unternehmen import Unternehmen
from Storage import Storage
from DataBase import DataBase

# Die Hauptklasse für den Marktalgorithmus, die von mesa.Model erbt        
class Marktalgorithmus(mesa.Model):
    def __init__(self, simulation_data, level_t_0):
        super().__init__()
        # Initialisierung der Datenbank mit externen Simulationseinstellungen
        self.database = DataBase(self, simulation_data) #Die Datei muss noch erstellt werden
        
        # Anlegen Zeitindex
        ti = self.model.time_index
        rti = list(range(len(ti)))
        
        # Anlegen der Variablen, die später benötigt werden
        self.results_MAN = []
        self.results_MTA = []
        self.results_UPM = []
        self.results_SWA = []
        self.results_storage = []
        self.results_P2P_trading = []
        self.tele_demand = []
        self.tele_supply = []
        self.Res_pre = []
        self.level_t = []
        
        self.MAN_agent = None
        self.MTA_agent = None
        self.UPM_agent = None
        self.storage_agent = None
        self.SWA_agent = None
        
        self.epsilon_average = []
        self.epsilon_MAN = []
        self.epsilon_MTA = []
        self.epsilon_UPM = []
        self.epsilon_storage = []
        self.epsilon_SWA = []
        
        # Initialisierung der Agenten und Aktivierungsplan für jeden Zeitschritt
        for i in rti:
            self.agents = []
            self.schedule = mesa.time.RandomActivation(self)
            
            # Initialisierung der Unternehmen (Agents) für MAN, MTA und UPM für den aktuellen Zeitschritt 
            self.MAN_agent = Unternehmen("MAN_agent", self, i, self.results_MAN, self.results_P2P_trading)
            self.agents.append(self.MAN_agent)
            self.schedule.add(self.MAN_agent)
            self.MTA_agent = Unternehmen("MTA_agent", self, i, self.results_MTA, self.results_P2P_trading)
            self.agents.append(self.MTA_agent)
            self.schedule.add(self.MTA_agent)
            self.UPM_agent = Unternehmen("UPM_agent", self, i, self.results_UPM, self.results_P2P_trading)
            self.agents.append(self.UPM_agent)
            self.schedule.add(self.UPM_agent)
            
            # (Neu-)Berechnung der Parameter für den aktuellen Zeitschritt
            if i==0:
                self.level_t.append(level_t_0)
                self.Res_pre.append(0)
            else:
                self.level_t.append(self.results_storage[i-1][2]+self.results_P2P_trading[i-1][10]-self.results_P2P_trading[i-1][11])
                self.tele_demand.append(self.results_MAN[i-1][9] + self.results_MAN[i-1][9] + self.results_MAN[i-1][9]) # demand
                self.tele_supply.append(self.results_MAN[i-1][10] + self.results_MAN[i-1][10] + self.results_MAN[i-1][10])
                self.Res_pre.append(self.tele_demand-self.tele_supply)
                
            # Initialisierung der Storage- und SWA-Agenten für den aktuellen Zeitschritt    
            self.storage_agent = Storage("storage_agent", self, self.level_t, self.tele_demand, self.tele_supply, self.results_storage, i)
            self.agents.append(self.storage_agent)
            self.schedule.add(self.storage_agent)
            self.SWA_agent = SWA("SWA_agent", self, self.Res_prei, self.tele_demand, self.tele_supply, self.results_SWA, i)
            self.agents.append(self.SWA_agent)
            self.schedule.add(self.SWA_agent)
            
            # Schritt-Funktion wird aufgerufen
            self.step(i)
        return
    
    # Schritt-Funktion für jeden Zeitschritt    
    def step(self, i):
        # Ausführen des Zeitschritts
        self.schedule.step()
        
        # Sammeln der Ergebnisse von jedem Agenten
        self.results_MAN.append(self.MAN_agent.get_opt())
        self.results_MTA.append(self.MTA_agentget_opt())
        self.results_UPM.append(self.UPM_agent.get_opt())
        self.results_SWA.append(self.SWA_agent.get_results())
        self.results_storage.append(self.storage_agent.get_results())
        
        # Berechnung der Produktion und Nachfrage für jedes Unternehmen
        self.production_MAN = np.array([["wh", self.MAN_agent.get_c_w()[i], self.results_MAN[i][1]], ["electr", self.MAN_agent.get_c_E_el_d()[i]*self.MAN_agent.get_const_E_el_to_h(), self.results_MAN[i][11]], ["gas", self.MAN_agent.get_c_E_g_grid()[i]*self.MAN_agent.get_const_E_g_to_h(), self.results_MAN[12]], ["tele", self.MAN_agent.get_c_t_d()[i], self.results_MAN[i][9]], ["quarter", self.MAN_agent.get_c_q_d()[i], self.results_MAN[i][7]]])
        self.d_MAN = sum(self.production_MAN[:5])
        self.q_MAN = self.production_MAN[5]
        
        self.production_MTA = np.array([["wh", self.MTA_agent.get_c_w()[i], self.results_MTA[i][1]], ["electr", self.MTA_agent.get_c_E_el_d()[i]*self.MTA_agent.get_const_E_el_to_h(), self.results_MTA[i][11]], ["gas", self.MTA_agent.get_c_E_g_grid()[i]*self.MTA_agent.get_const_E_g_to_h(), self.results_MTA[12]], ["tele", self.MTA_agent.get_c_t_d()[i], self.results_MTA[i][9]], ["quarter", self.MTA_agent.get_c_q_d()[i], self.results_MTA[i][7]]])
        self.d_MTA = sum(self.production_MTA[:5])
        self.q_MTA = self.production_MTA[5]
        
        self.production_UPM = np.array([["wh", self.UPM_agent.get_c_w()[i], self.results_UPM[i][1]], ["electr", self.UPM_agent.get_c_E_el_d()[i]*self.UPM_agent.get_const_E_el_to_h(), self.results_UPM[i][11]], ["gas", self.UPM_agent.get_c_E_g_grid()[i]*self.UPM_agent.get_const_E_g_to_h(), self.results_UPM[12]], ["tele", self.UPM_agent.get_c_t_d()[i], self.results_UPM[i][9]], ["quarter", self.UPM_agent.get_c_q_d()[i], self.results_UPM[i][7]]])
        self.d_UPM = sum(self.production_UPM[:5])
        self.q_UPM = self.production_UPM[5]
        
        # Berechnung von Angebot und Nachfrage des Speichers
        self.demand_storage = self.results_storage[i][0]
        self.supply_storage = self.results_storage[i][1]
        
        if i==0:
            epsilon_q = self.model.database.optimization_parameter['epsilon_ih']
            self.epsilon_MAN_t_0 = (self.MAN_agent.calculate_epsilon(epsilon_q, i, self.results_MAN[i][8], self.results_MAN[i][7]))
            self.epsilon_MTA_t_0 = (self.MTA_agent.calculate_epsilon(epsilon_q, i, self.results_MTA[i][8], self.results_MTA[i][7]))
            self.epsilon_UPM_t_0 = (self.UPM_agent.calculate_epsilon(epsilon_q, i, self.results_UPM[i][8], self.results_UPM[i][7]))
            self.epsilon_storage_t_0 = (self.storage_agent.calculate_epsilon(epsilon_q, i, self.results_storage[i][1], self.results_storage[i][0]))
            self.epsilon_average_t_0 = [self.epsilon_MAN_t_0, self.epsilon_MTA_t_0, self.epsilon_UPM_t_0, self.epsilon_storage_t_0]
        
        # Initialisierung und Aufruf der Optimierungsfunktion für den Marktalgorithmus & Speicherung Ergebnis
        if i==0:
            self.optimierung_Marketalgorithmus = Optimierung_Marketalgorithmus(self.demand_storage, self.supply_storage, self.production_MAN, self.d_MAN, self.q_MAN, self.production_MTA, self.d_MTA, self.q_MTA, self.production_UPM, self.d_UPM, self.q_UPM, self.epsilon_average_t_0)
            self.results_P2P_trading.append(self.optimierung_Marketalgorithmus.get_optimales_Ergebnis())    
        else:    
            self.optimierung_Marketalgorithmus = Optimierung_Marketalgorithmus(self.demand_storage, self.supply_storage, self.production_MAN, self.d_MAN, self.q_MAN, self.production_MTA, self.d_MTA, self.q_MTA, self.production_UPM, self.d_UPM, self.q_UPM,  self.epsilon_average[i-1])
            self.results_P2P_trading.append(self.optimierung_Marketalgorithmus.get_optimales_Ergebnis())
        
        # Durchführung der Emissionsbilanzierung
        self.epsilon_MAN.append(self.MAN_agent.calculate_epsilon(self.results_P2P_trading[i][len(self.results_P2P_trading)-1], i, self.results_MAN[i][8], self.results_MAN[i][7]))
        self.epsilon_MTA.append(self.MTA_agent.calculate_epsilon(self.results_P2P_trading[i][len(self.results_P2P_trading)-1], i, self.results_MTA[i][8], self.results_MTA[i][7]))
        self.epsilon_UPM.append(self.UPM_agent.calculate_epsilon(self.results_P2P_trading[i][len(self.results_P2P_trading)-1], i, self.results_UPM[i][8], self.results_UPM[i][7]))
        self.epsilon_storage.append(self.storage_agent.calculate_epsilon(self.results_P2P_trading[i][len(self.results_P2P_trading)-1], i, self.results_storage[i][1], self.results_storage[i][0]))
        self.epsilon_average.append([self.epsilon_MAN[i], self.epsilon_MTA[i], self.epsilon_UPM[i], self.epsilon_storage[i]])
        q_t_d = self.results_MAN[i][9] + self.results_MTA[i][9] + self.results_UPM[i][9]
        q_t_s = self.results_MAN[i][10] + self.results_MTA[i][10] + self.results_UPM[i][10]
        self.epsilon_SWA.append(self.SWA_agent(self.results_P2P_trading[i][len(self.results_P2P_trading)-1], i, q_t_s, q_t_d))
        return
    
marktalgorithmus = Marktalgorithmus(simulation_data, level_t_0) # Methodenaufruf aus der main-Datei mit simulation_data, level_t_0