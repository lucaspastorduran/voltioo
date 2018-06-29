#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 08:27:43 2018

@author: lucas
"""

import pandas as pd

# Inputs: origen, destinos, fecha_salida días por ciudad
def fullMatrix(origen, destinos, fecha_salida,dias_por_ciudad, numero_ciudades, pasajeros, n_combinaciones):
  #print("Get the prices from {} to {}. {} days per city, {} cities to visit, {} passengers"
  #     .format(origen, destinos, dias_por_ciudad, numero_ciudades, pasajeros))
  
  # Comprobamos si origen es string y que no haya más de 9 destinos
  if not isinstance(origen, str):
    raise ValueError("Error! Origen must be string")
  elif (len(destinos) > 9) or (numero_ciudades > 9):
    raise ValueError("Error! Not more than 9 destinos")

  # Si destinos está vacío, tiramos de fullMatrixNoDestinos
  if len(destinos) == 0:
    print("No hay destinos, se sacan con fullMatrixNoDestinos")
    full_matrix = pd.read_csv("flights_no_destinations.csv")
  # Si no, seguimos con la fullMatrixConDestinos
  else:
    print("Los destinos son:", destinos)
    full_matrix = pd.read_csv("flights_with_destinations.csv")
  full_matrix.sort_values(["Date","Price"])
  return full_matrix
