# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np

production = np.array([["kwk", 15.0, 0.0], ["wh", 6.0, 1000.0], ["electr", 8.0, 5000.0], ["gas", 5.0, 20000.0], ["tele", 13.0, 10.0]])
d_a_t=30000.0
q_a_t=0.0
for i in range(0, len(production)):
    q_a_t+=float(production[i][2])
    
if q_a_t < d_a_t:
    #Kauf: Transformation der Produktionsmengen aus der der Unternehmensoptimierung in eine Nachfragefunktion für die Gebotsabgabe den Quartiershandel
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
else:
    #Verkauf: Ermittlung der Angebotsmenge (Annahme: zum Minimalpreis, da garantiert bester Vermarktungskanal) für Gebotsabgabe den Quartiershandel
    q=q_a_t-d_a_t
   