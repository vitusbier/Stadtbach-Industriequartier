# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np

class Transformation ():
    def __init__(self):
        # Input: Kosten je Einheit und Menge an Einheiten der geplanten Wärme-Produktionsmengen aus der Unternehmensoptimierung
        # Output: aggregierte Angebots- (nur Menge) bzw. Nachfragefunktion (Preis und Menge) der Unternehmen und alle für den Marktalgorithmus relevanten Preisniveaus 
        self.price_levels = [] #Platzhalter zur Speicherung der Preisniveaus
        # Handelsmengen des Wärmesepeichers
        self.demand_storage =2000
        self.supply_storage =7000
        # Produktions-, Bedarfs- und geplanten Quartiershandelsdaten der Industrieunternehmen (hier: MAN) -> ergeben sich aus der jeweiligen Unternehmensoptimierung
        self.production_MAN = np.array([["kwk", 15.0, 0.0], ["wh", 6.0, 1000.0], ["electr", 8.0, 5000.0], ["gas", 5.0, 20000.0], ["tele", 13.0, 10.0]])
        self.d_MAN_t=25000.0 #26010
        self.q_MAN_t=0.0
        self.bids_MAN = self.transformation(self.production_MAN, self.d_MAN_t, self.q_MAN_t) #Errechnung der Angebots-/ Nachfragefunktion
        self.bool_MAN = str(type(self.bids_MAN))=="<class 'numpy.ndarray'>" #Angebot -> Datentyp float oder Nachfrage -> Datentyp npArray
        if self.bool_MAN: #Falls Nachfrage -> Hinzufügen der Preisniveaus des Unternehmens zu der Gesamtmenge an Preisniveaus
            self.set_price_levels(self.production_MAN)
            
        # Analog für MTA
        self.production_MTA = np.array([["kwk", 13.5, 0], ["wh", 7.0, 100.0], ["electr", 6.5, 1500.0], ["gas", 5.5, 4000.0], ["tele", 13.0, 500.0]])
        self.d_MTA_t=7500.0 #6100
        self.q_MTA_t=0.0
        self.bids_MTA = self.transformation(self.production_MTA, self.d_MTA_t, self.q_MTA_t)
        self.bool_MTA = str(type(self.bids_MTA))=="<class 'numpy.ndarray'>"
        if self.bool_MTA:
            self.set_price_levels(self.production_MTA)
        
        # Analog für UPM        
        self.production_UPM = np.array([["kwk", 14.0, 0], ["wh", 6.0, 150.0], ["electr", 7.5, 1500.0], ["gas", 4.8, 12500.0], ["tele", 13.0, 250.0]])
        self.d_UPM_t=15000 #14400
        self.q_UPM_t=0.0
        self.bids_UPM = self.transformation(self.production_UPM, self.d_UPM_t, self.q_UPM_t)
        self.bool_UPM = str(type(self.bids_UPM))=="<class 'numpy.ndarray'>"
        if self.bool_UPM:
            self.set_price_levels(self.production_UPM)
        
        # Aufsteigende Sortierung der Preisniveaus in Form einer Liste ohne doppelte Einträge
        self.price_levels = set(self.price_levels)
        self.price_levels = sorted(map(float, self.price_levels))
        print(self.price_levels)
        # Berechnung der maximalen Handelsvolumina je Preisniveau
        self.handelsvolumina()
        return
        
    def transformation(self, production, d_a_t, q_a_t):
        # Transformation der Produktionsmengen in Nachfrage- oder Angebotsfunktion
        for i in range(0, len(production)): #Errechnung der gesamten zur Verfügug stehenden Wärmemenge
            q_a_t+=float(production[i][2])
            
        # Muss eine Angebots- oder Nachfragefunktion erstellt werden?    
        if q_a_t < d_a_t:
            # Kauf -> Nachgfragefunktion: Transformation der Produktionsmengen aus der der Unternehmensoptimierung in eine Nachfragefunktion für die Gebotsabgabe den Quartiershandel
            bids = np.empty((len(production),3), dtype=object)
            ind = np.argsort(production[:, 1].astype(float))[::-1]
            production = production[ind]
            
            for i in range(0,len(production)):
                q=d_a_t-q_a_t
                for l in range(0, i+1):
                    q+=float(production[l][2])
                bids[i][2]=q
                bids[i][0]=production[i][0]
                bids[i][1]=float(production[i][1])
                
            ind = np.argsort(bids[:, 1].astype(float))
            bids=bids[ind]
            return bids
        else:
            # Verkauf -> Angebotsfunktion: Ermittlung der Angebotsmenge (Annahme: zum Minimalpreis, da garantiert bester Vermarktungskanal) für Gebotsabgabe den Quartiershandel
            q=q_a_t-d_a_t
            return q
            
    def set_price_levels(self, bids):
        # Hinzufügen der Preisniveaus der einzelnen Nachfrager zu der geasamten Menge an Preisniveaus
        for i in range(len(bids)):
            if float(bids[i][2])>0:
                self.price_levels.append(bids[i][1])
        return

    def handelsvolumina(self):
        self.demand_vol=[] 
        ind_MAN=0
        self.demand_MAN=[]
        ind_MTA=0
        self.demand_MTA=[]
        ind_UPM=0
        self.demand_UPM=[]
        # Bestimmung der expliziten Nachfragemengen der einzelnen Nachfrager und Summierung zu einer aggregierten Nachfragemenge für jedes Preisniveau
        # Speicherung der individuellen Nachfragemengen der Unternehmen und der aggregierten Gesamtnachfragemenge in je einer Liste sortiert nach aufsteigendem Preisniveau
        # Die Liste ist leer,falls das Unternehmen über keine Nachfrage verfügt
        for i in range(len(self.price_levels)):
            vol =self.demand_storage
            if self.bool_MAN:
                if self.bids_MAN[ind_MAN][1]>=self.price_levels[i]:
                    self.demand_MAN.append(self.bids_MAN[ind_MAN][2])
                    vol+=self.bids_MAN[ind_MAN][2]
                else: 
                    while self.bids_MAN[ind_MAN][1]<self.price_levels[i]:
                        ind_MAN+=1
                    vol+=self.bids_MAN[ind_MAN][2]
                    self.demand_MAN.append(self.bids_MAN[ind_MAN][2])
            if self.bool_MTA:
                if self.bids_MTA[ind_MTA][1]>=self.price_levels[i]:
                    self.demand_MTA.append(self.bids_MTA[ind_MTA][2])
                    vol+=self.bids_MTA[ind_MTA][2]
                else: 
                    while ind_MTA < len(self.bids_MTA) and self.bids_MTA[ind_MTA][1] < self.price_levels[i]:
                        ind_MTA+=1
                    vol += self.bids_MTA[ind_MTA][2]
                    self.demand_MTA.append(self.bids_MTA[ind_MTA][2])
            if self.bool_UPM:    
                if self.bids_UPM[ind_UPM][1]>=self.price_levels[i]:
                    self.demand_UPM.append(self.bids_UPM[ind_UPM][2])
                    vol+=self.bids_UPM[ind_UPM][2]
                else: 
                    while ind_UPM < len(self.bids_UPM) and self.bids_UPM[ind_UPM][1]<self.price_levels[i]:
                        ind_UPM+=1
                    vol+=self.bids_UPM[ind_UPM][2]
                    self.demand_UPM.append(self.bids_UPM[ind_UPM][2])
            self.demand_vol.append(vol)
        print(self.demand_vol)
        
        # Brechnung der gesamten Angebotsmenge des Quartiershandels (anbietende Unternehmen + Speichermeng)
        # Die Angebotsmengen der einzelnen Unternehmen sind bereits in der entsprechenden Variable self.bids_NAME gespeichert
        # Diese Mengen werden für alle Preisniveaus als konstant angenommen, da der Quartiershandel immer eine bessere Vremarktungsalternative als eine Vermarktung an das Fernwärmenetz darstellt und eine zusätzliche Produktion von Wärme zur Vermarktung über die Unternehmensoptimierung hinaus nicht vorgesehen ist
        self.supply_vol = self.supply_storage
        if self.bool_MAN==False:
            self.supply_vol+=self.bids_MAN
            self.supply_MAN=[self.bids_MAN]*len(self.price_levels)
        if self.bool_MTA==False:
            self.supply_vol+=self.bids_MTA
            self.supply_MTA=[self.bids_MTA]*len(self.price_levels)
        if self.bool_UPM==False:
                self.supply_vol+=self.bids_UPM
                self.supply_MTA=[self.bids_MTA]*len(self.price_levels)
        print(self.supply_vol)
        
        # Berechnung der maximalen Handelsvolumina des Quartiershandels für alle Preisniveaus und Speicherung in einer Liste aufsteigend sortiert nach Preisniveau 
        self.vol_max=[]
        for i in range(len(self.price_levels)):
            self.vol_max.append(min(self.demand_vol[i], self.supply_vol))
        print(self.vol_max)
        self.supply_vol = [self.supply_vol]*len(self.price_levels)
        return
        
transformation = Transformation()