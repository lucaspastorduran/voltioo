# -*- coding: utf-8 -*-
"""Listo para Flask

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JxPoUxVKBCa-Io60W6GEDs22vWUpoWbk
"""

import math
import requests
import json
import pandas as pd
import datetime
import numpy as np

from simulated_functions_find_combinations import *

# Función que suma días
def addDays(fecha,days):
  fecha = datetime.datetime.strptime(fecha, "%d/%m/%Y")
  fecha2 = fecha + datetime.timedelta(days=int(days))
  return datetime.datetime.strftime(fecha2, "%d/%m/%Y")


# Convertir todos los vuelos del DF de una combinación a una única fila
def compressFlightsToCombination(combinations_flights):
  #one_combination_flights = pd.DataFrame([],  columns = full_matrix.columns.values)
  compressed_combination = combinations_flights.loc[0].copy()
  string_columns = ["To", "Hour", "Date", "Id"]
  for column in string_columns:
    compressed_combination[column] = combinations_flights[column].tolist()
  compressed_combination["Id"] = str(compressed_combination["Id"])[1:-1].replace("'","").replace(", ","%7C")
  compressed_combination["Price"] = np.sum(combinations_flights['Price'].values)
  route_columns = ['From', 'To', 'Date', 'Hour', 'Price']
  compressed_combination["Route"] = (combinations_flights[route_columns].
                                     values.tolist())
  return compressed_combination


# Convertir un DF te combinaciones al formato diccionario
def convertCombinationDfToDict(combinations_df, passengers):
  combination_dict = {}
  for index, combination in combinations_df.iterrows():
    price_by_person = round(float(combination['Price'])/passengers,2)
    combination_dict["combination{}".format(index)] = {
        'passengers': passengers,
        'departure': combination['From'], 
        'destinations': combination['To'],
        'dates': combination['Date'],
        'price': price_by_person,
        'url': ("https://www.kiwi.com/deep?flightsId={}&price={}&passengers={}&affilid=picky&lang=es&currency=EUR".
                format(combination['Id'],combination['Price'],passengers)),
        'route': combination['Route']
    }
  return combination_dict

 
# Función para encontrar el mejor trayecto utilizando el algoritmo meta-heurístico
def findBestPathGlobMulti(full_matrix, departure_cities, ciudades_deseadas, n_ciudades_a_visitar, fechas, pasajeros, n_combinaciones):
  n_viajes = n_ciudades_a_visitar + 1
  n_ciudades_a_elegir = len(ciudades_deseadas) #conjunto ciudades entre las que elegir
  
  # comprobar que sea posible elegir n combinaciones con tantas ciudades y tantos viajes
  possible_combinations = int(math.factorial(n_ciudades_a_elegir)/math.factorial(n_ciudades_a_elegir - n_ciudades_a_visitar))
  if (n_combinaciones > possible_combinations):
    # it is not posible to find all the combinations in these conditions
    print("Not possible to create {} combinations by choosing {} of {} desired cities! Only {} are possible"
                     .format(n_combinaciones, n_ciudades_a_visitar, n_ciudades_a_elegir, possible_combinations))
    n_combinaciones = possible_combinations
  
  # buscamos el mejor recorrido para cada una de las combinaciones
  print("Show {} combinations from all the {}: choose {} cities from {} choices ({} flights)"
        .format(n_combinaciones, possible_combinations, n_ciudades_a_visitar, n_ciudades_a_elegir, n_viajes))
  all_combinations_flights = pd.DataFrame([], columns =  np.append(full_matrix.columns.values, "Route"))
  all_paths = {}
  combination = 0
  comb_found = 0
  print("Departure and arrival unique cities: ", departure_cities)
  while (comb_found < n_combinaciones) and (combination < possible_combinations):
    print("*****************************************************************")
    one_combination_flights = pd.DataFrame([], columns = full_matrix.columns.values)
    visited_cities = departure_cities.copy()
    current_city = departure_cities.copy()

    # calcula el idx_viaje para el que habrá que hacer excepcion y no elegir el viaje mas barato para generar combinaciones
    flight_to_except = (combination - 1)%(n_ciudades_a_visitar)
    index_if_except = math.ceil(float(combination)/(n_ciudades_a_visitar))
    print('In combination {} we must choose the {} cheaper price for flight {}'
          .format(combination + 1, index_if_except + 1, flight_to_except + 1))

    # calcula los precios desde la ciudad actual hasta las siguientes
    discard_comb = False
    for idx_viaje in range(n_viajes):
      current_date = fechas[idx_viaje]
      print('Starting flight {}/{}: from {} on date {}'.format(idx_viaje + 1,n_viajes,current_city, current_date))
      
      # Mira si el viaje actual es el último o no
      if (idx_viaje + 1) < n_viajes:
        # Si no es el último viaje, además hay que evitar que el destino sea una ciudad ya visitada
        accepted_cities = [element not in visited_cities for element in full_matrix['To']]     
      else:
        # Si es el último viaje, destino tiene que ser un de las ciudades de origen
        accepted_cities = [element in departure_cities for element in full_matrix['To']]
      
      # Mirar destinos posibles teniendo en cuenta lo anterior, la fecha y la ciudad actual
      filas_viajes_posibles = ([element in current_city for element in full_matrix['From']] & 
                               (full_matrix['Date'] == current_date) & accepted_cities)
      
      # Saca el df con todos los posibles destinos encontrados
      n_viajes_posibles = np.sum(filas_viajes_posibles)
      if n_viajes_posibles > 0:
        viajes_posibles = full_matrix.loc[filas_viajes_posibles].sort_values('Price')
      else:
        viajes_posibles = pd.DataFrame([], columns = full_matrix.columns.values)
        discard_comb = True
        print("No flights found from {} on {}!".format(current_city, current_date))
      print("All the flights found:\n", viajes_posibles)
      
      # Decide si este vuelo es la excepción para generar varias combinaciones y mira si hay suficientes
      if idx_viaje == flight_to_except:
        # Comprueba que se hayan encontrado encontrado alternativas suficientes
        index_lower_price = index_if_except
        if (index_if_except >= n_viajes_posibles):
          discard_comb = True
          print("Not enough flights in combination {} from {} on {} to find another combination!"
                            .format(combination + 1, current_city, current_date))
      else:
        # No es la excepcion o es el vuelo de vuelta
        index_lower_price = 0
      print('Choosen flight {} of {} possible trips:\n {}'.
            format(index_lower_price + 1, n_viajes_posibles, viajes_posibles))

      # Actualiza los datos del mejor vuelo encontrado si la comb es valida
      if not discard_comb:
        one_combination_flights.loc[idx_viaje] = viajes_posibles.iloc[index_lower_price].copy()
        current_city = one_combination_flights['To'].loc[idx_viaje]
        visited_cities.append(current_city)
      else:
        print("Combination {} was discarded".format(combination + 1))
        break
      #print("visited cities: ", visited_cities)
    # comprime la info de todos los vuelos de la combinación encontrada en una única fila
    print("For combination {} there are the following flights:\n{}".format(combination+1, one_combination_flights))
    if not discard_comb:
      all_combinations_flights.loc[comb_found] = compressFlightsToCombination(one_combination_flights)
      comb_found += 1
      print("For combination {} there are the following flights:\n{}".format(comb_found, one_combination_flights))
    combination += 1
  all_combinations_flights.drop('CodeTo', axis=1, inplace=True)
  all_combinations_flights.sort_values(["Price"], inplace=True)
  return all_combinations_flights


def findBestPathLocMulti(full_matrix, departure_cities, ciudades_deseadas, n_ciudades_a_visitar, fechas, pasajeros, n_combinaciones):
  n_viajes = n_ciudades_a_visitar + 1
  n_ciudades_a_elegir = len(ciudades_deseadas) #conjunto ciudades entre las que elegir
  
  # comprobar que sea posible elegir n combinaciones con tantas ciudades y tantos viajes
  possible_combinations = int(math.factorial(n_ciudades_a_elegir)/math.factorial(n_ciudades_a_elegir - n_ciudades_a_visitar))
  if (n_combinaciones > possible_combinations):
    # it is not posible to find all the combinations in these conditions
    print("Not possible to create {} combinations by choosing {} of {} desired cities! Only {} are possible"
                     .format(n_combinaciones, n_ciudades_a_visitar, n_ciudades_a_elegir, possible_combinations))
    n_combinaciones = possible_combinations
  
  # buscamos el mejor recorrido para cada una de las combinaciones
  print("Show {} combinations from all the {}: choose {} cities from {} choices ({} flights)"
        .format(n_combinaciones, possible_combinations, n_ciudades_a_visitar, n_ciudades_a_elegir, n_viajes))
  all_combinations_flights = pd.DataFrame([], columns =  np.append(full_matrix.columns.values, "Route"))
  all_paths = {}
  combination = 0
  comb_found = 0
  print("Departure and arrival unique cities: ", departure_cities)
  while (comb_found < n_combinaciones) and (combination < possible_combinations):
    print("*****************************************************************")
    one_combination_flights = pd.DataFrame([], columns = full_matrix.columns.values)
    visited_cities = departure_cities.copy()
    current_city = departure_cities.copy()

    # calcula el idx_viaje para el que habrá que hacer excepcion y no elegir el viaje mas barato para generar combinaciones
    flight_to_except = (combination - 1)%(n_ciudades_a_visitar)
    index_if_except = math.ceil(float(combination)/(n_ciudades_a_visitar))
    print('In combination {} we must choose the {} cheaper price for flight {}'
          .format(combination + 1, index_if_except + 1, flight_to_except + 1))

    # calcula los precios desde la ciudad actual hasta las siguientes
    discard_comb = False
    for idx_viaje in range(n_viajes):
      current_date = fechas[idx_viaje]
      print('Starting flight {}/{}: from {} on date {}'.format(idx_viaje + 1,n_viajes,current_city, current_date))
      
      # Mira si el viaje actual es el último o no
      if (idx_viaje + 1) < n_viajes:
        # Si no es el último viaje, además hay que evitar que el destino sea una ciudad ya visitada
        accepted_cities = [element not in visited_cities for element in full_matrix['To']]     
      else:
        # Si es el último viaje, destino tiene que ser un de las ciudades de origen
        accepted_cities = [element in departure_cities for element in full_matrix['To']]
      
      # Mirar destinos posibles teniendo en cuenta lo anterior, la fecha y la ciudad actual
      filas_viajes_posibles = ([element in current_city for element in full_matrix['From']] & 
                               (full_matrix['Date'] == current_date) & accepted_cities)
      
      # Saca el df con todos los posibles destinos encontrados
      n_viajes_posibles = np.sum(filas_viajes_posibles)
      if n_viajes_posibles > 0:
        viajes_posibles = full_matrix.loc[filas_viajes_posibles].sort_values('Price')
      else:
        viajes_posibles = pd.DataFrame([], columns = full_matrix.columns.values)
        discard_comb = True
        print("No flights found from {} on {}!".format(current_city, current_date))
      print("All the flights found:\n", viajes_posibles)
      
      # Decide si este vuelo es la excepción para generar varias combinaciones y mira si hay suficientes
      if idx_viaje == flight_to_except:
        # Comprueba que se hayan encontrado encontrado alternativas suficientes
        index_lower_price = index_if_except
        if (index_if_except >= n_viajes_posibles):
          discard_comb = True
          print("Not enough flights in combination {} from {} on {} to find another combination!"
                            .format(combination + 1, current_city, current_date))
      else:
        # No es la excepcion o es el vuelo de vuelta
        index_lower_price = 0
      print('Choosen flight {} of {} possible trips:\n {}'.
            format(index_lower_price + 1, n_viajes_posibles, viajes_posibles))

      # Actualiza los datos del mejor vuelo encontrado si la comb es valida
      if not discard_comb:
        one_combination_flights.loc[idx_viaje] = viajes_posibles.iloc[index_lower_price].copy()
        current_city = one_combination_flights['To'].loc[idx_viaje]
        visited_cities.append(current_city)
      else:
        print("Combination {} was discarded".format(combination + 1))
        break
      #print("visited cities: ", visited_cities)
    # comprime la info de todos los vuelos de la combinación encontrada en una única fila
    print("For combination {} there are the following flights:\n{}".format(combination+1, one_combination_flights))
    if not discard_comb:
      all_combinations_flights.loc[comb_found] = compressFlightsToCombination(one_combination_flights)
      comb_found += 1
      print("For combination {} there are the following flights:\n{}".format(comb_found, one_combination_flights))
    combination += 1
  all_combinations_flights.drop('CodeTo', axis=1, inplace=True)
  all_combinations_flights.sort_values(["Price"], inplace=True)
  return all_combinations_flights



def getMatrixAndCombinations (origen, destinos, fecha_salida, dias_por_ciudad, numero_ciudades, pasajeros, n_combinaciones):
  """
  Esta funcion tiene como entrada los inputs del usuario. Crea la matriz de vuelos usando fullMatrix, saca los inputs necesarios
  para llamar a "findbestpathloc", y del df de combinacioneshace el return del json.
  """
  # Sacamos el DF con la info de todos los vuelos necesarios
  full_matrix = pd.read_csv("flights_with_destinations.csv")
  print("La matriz de vuelos queda:\n", full_matrix.loc[:, full_matrix.columns != 'Id'])
  
  # Sacamos origen, destinos, fechas y número de ciudades
  fechas = sorted(full_matrix["Date"].unique().tolist())
  print("fechas:", fechas)
  origen = list(full_matrix.loc[(full_matrix["Date"] == fechas[0]), "From"].unique())
  print("origen:", origen)
  ciudades_vuelta = list(full_matrix.loc[(full_matrix["Date"] == fechas[-1]), "To"].unique())
  print("ciudades vuelta:", ciudades_vuelta)
  origen.extend(city for city in ciudades_vuelta if city not in origen)
  print("ciudades origen/vuelta", ciudades_vuelta)
  destinos = [city for city in full_matrix["To"].unique() if city != origen]
  full_matrix['Price'] = full_matrix['Price'].apply(pd.to_numeric)
  
  # De todos los vuelos encontramos las mejores combinaciones
  best_combinations_df = findBestPathLocMulti(full_matrix, origen, destinos, numero_ciudades, fechas, pasajeros, n_combinaciones)
  # Convertimos a diccionario
  #best_combinations_dict = convertCombinationDfToDict(all_combinations_flights, pasajeros)
  # Convertimos a json
  #best_combinations_json = json.dumps(best_combinations_dict, cls=MyEncoder)
  return best_combinations_df

if __name__ == "__main__":
    # run all the tests
    