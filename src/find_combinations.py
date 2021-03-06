# -*- coding: utf-8 -*-
"""Listo para Flask

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JxPoUxVKBCa-Io60W6GEDs22vWUpoWbk
"""

import math
import requests
import sys
import json
import pandas as pd
import datetime
import numpy as np

#sys.path.insert(0, "/home/lucas/Documentos/voltioo")
#from simulated_functions_find_combinations import *
#from listo_para_flask import *
#/home/lucas/Documentos/voltioo/
#addDays, compressFlightsToCombination, convertCombinationDfToDict

# Función que suma días
def addDays(fecha,days):
  fecha = datetime.datetime.strptime(fecha, "%d/%m/%Y")
  fecha2 = fecha + datetime.timedelta(days=int(days))
  return datetime.datetime.strftime(fecha2, "%d/%m/%Y")

def insertFlightInCombination(combinations_flights, flight):
    #print("Combination:\n{}\nFlight:\n{}".format(combinations_flights, flight))
    combinations_flights.at["Price"] = combinations_flights["Price"] + flight["Price"]
    #print("Added {} to 'Price' colum. Result is: {}".format(flight['Price'], combinations_flights['Price']))
    #print("Changing 'From' colum from '{}' to '{}'".format(combinations_flights["From"], flight["From"]))
    combinations_flights.at["From"] = flight["From"]
    for column in ["To", "Hour", "Date"]:
        combinations_flights.at[column].insert(0, flight[column])
        #print("Inserted '{}' into colum '{}'. Result is: {}".format(flight[column], column, combinations_flights[column]))
    if combinations_flights["Id"] == "":
        combinations_flights.at["Id"] = flight["Id"].replace("'","")
    else:
        combinations_flights.at["Id"] = flight["Id"].replace("'","") + "%7C" + combinations_flights["Id"]
    route_columns = ['From', 'To', 'Date', 'Hour', 'Price']
    combinations_flights.at["Route"].insert(0, flight[route_columns].values.tolist())
    #print("Combination after inserting all the flight info:\n", combinations_flights)
    return combinations_flights
    
# Convertir todos los vuelos del DF de una combinación a una única fila
def compressFlightsToCombination(combinations_flights):
  """
  Combination tiene:
    - From: Origen del trip
    - To: Lista de todos los destinos
    - Hour: Lista con todas las horas de los vuelos
    - Date: Lista con todas las fechas
    - Id: Lista con todos los Ids convertida a string cambiando "'" por "" y ", " por "%7C"
    - Price: suma de todos los vuelos
    - Route: Lista de listas donde cada nested list tiene ['From', 'To', 'Date', 'Hour', 'Price'] de cada vuelo
  """
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


def getInfoFromMatrix(full_matrix, print_allowed = False):
    """
    Funcion para deducir los origen, destinos y fechas de una fullMatrix
    Con ella nos ahorramos tener que volver a declarar estos parámetros que están
    dentro de la matriz.
    """
    fechas = sorted(full_matrix["Date"].unique().tolist())
    origen = list(full_matrix.loc[(full_matrix["Date"] == fechas[0]), "From"].unique())
    ciudades_vuelta = list(full_matrix.loc[(full_matrix["Date"] == fechas[-1]), "To"].unique())
    origen.extend(city for city in ciudades_vuelta if city not in origen)
    destinos = [city for city in full_matrix["To"].unique() if city not in origen]
    if print_allowed:
        print("Fechas:", fechas, "\nOrigen:", origen, "\nCiudades vuelta:", ciudades_vuelta)
        print("Ciudades origen/vuelta", ciudades_vuelta, "\nDestinos:", destinos)
    return origen, destinos, len(fechas), fechas

 
# Función para encontrar el mejor trayecto utilizando el algoritmo recursivo-exhaustivo
def findBestPathGlobMulti(full_matrix, departure_cities, ciudades_deseadas, n_ciudades_a_visitar, fechas, n_combinaciones):
    assert n_ciudades_a_visitar >= 1, "No has elegido ninguna ciudad"
    print("\nWe start adventure from {} on {}, flying {} times between {} cities. Return the {} cheapest combinations".
          format(departure_cities, fechas[0], n_ciudades_a_visitar, ciudades_deseadas, n_combinaciones))
    combination_columns = ['From', 'To', 'Date', 'Hour', 'Price', 'Id', 'Route']
    def findBestPathGlobMultiHandler(full_matrix, departure_cities, current_city, ciudades_deseadas, n_ciudades_a_visitar, fechas):
        current_date = fechas[0]
        #print("\nStarting from {} on {}. We can do {} flihts to desired cities and 1 to come back to departure.".
        #      format(current_city, current_date, n_ciudades_a_visitar-1))
        if n_ciudades_a_visitar <= 0: 
            # Si ya no quedan viajes, se acaba
            #print("Flight from {} terminated as we have seen all the cities".format(current_city))
            raise ValueError('You cannot request less than one city in FindBestPathGlob')
        elif n_ciudades_a_visitar == 1: 
            # Si es el último viaje volvemos al origen
            #print("It's the last flight. Must come back to {}".format(departure_cities))
            accepted_cities = [element in departure_cities for element in full_matrix['To']]
        else: 
            # Si no, exploramos todos los posibles viajes
            accepted_cities = [element in ciudades_deseadas for element in full_matrix['To']] 
        # Mirar destinos posibles teniendo en cuenta lo anterior, la fecha y la ciudad actual
        filas_viajes_posibles = ([city_from in current_city for city_from in full_matrix['From']] & \
                                   (full_matrix['Date'] == current_date) & accepted_cities)
        # Saca el df con todos los posibles destinos encontrados
        if np.sum(filas_viajes_posibles) <= 0:
            # Si no hay viajes posibles, devuelve DF vació y avis a anteriores llamadas que no guarden la combinación
            #print("No flights found from {} on {}!".format(current_city, current_date))
            return pd.DataFrame([], columns = combination_columns)
        else:
            # Si hay viajes posibles, haz la llamad recursiva de los siguientes
            viajes_posibles = full_matrix.loc[filas_viajes_posibles].sort_values('Price')
            #print("Flights found from {} on {}:\n{}".format(current_city, current_date, viajes_posibles))
            combinations = pd.DataFrame([], columns = combination_columns)
            for index_row_tuple in viajes_posibles.iterrows():
                possible_flight = index_row_tuple[1]
                if n_ciudades_a_visitar > 1: #and possible_flight['To'] not in departure_cities:
                    # si todavía nos quedan viajes por hacer, hacer llamadas recursivas
                    #print("Checking successive combinations from {} to {} on {}".format(current_city, possible_flight['To'], current_date))
                    # devuelve un DF con todas las combinaciones desde current_city
                    next_combinations = findBestPathGlobMultiHandler(full_matrix, departure_cities, possible_flight['To'], \
                                                                    [c for c in ciudades_deseadas if c not in current_city], \
                                                                    n_ciudades_a_visitar - 1, fechas[1:])
                    #print("{} combinations found from {} on {}:\n{}".format(len(next_combinations), current_city,current_date, next_combinations))
                    # Merge next_combinations DF/Series with combinations
                    for row_index in range(len(next_combinations)):
                        combinations = combinations.append(insertFlightInCombination(next_combinations.iloc[row_index], possible_flight))
                        #combinations.iloc[row_index] = insertFlightInCombination(next_combinations.iloc[row_index], possible_flight)
                    #combinations = combinations.append(insertFlightInCombination(next_combinations, possible_flight), ignore_index=True)
                elif len(viajes_posibles) > 0:
                    # si es el último viaje (volver origen) no hacer más llamadas recursivas
                    #print("Comming back from {} to {} on {} because it's last flight".format(current_city, possible_flight['To'], current_date))
                    combinations = combinations.append(insertFlightInCombination(pd.Series(data = ["", [], [], [], 0, "", []], index = combination_columns), possible_flight), ignore_index=True)
                else:
                    print("Something strange happened at line 157.")
            #print("All the next combinations found from {} on {} are:\n{}".format(current_city, current_date, combinations))
            return combinations
        #print("All the flights found:\n", viajes_posibles)
    #initial_flights = pd.DataFrame([], columns = full_matrix.columns.values)
    return findBestPathGlobMultiHandler(full_matrix, departure_cities, departure_cities, ciudades_deseadas, n_ciudades_a_visitar, fechas).sort_values('Price')


# Función para encontrar el mejor trayecto utilizando el algoritmo meta-heurístico
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
    print("find_combinations.py executed")
    
