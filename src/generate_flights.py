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

normalized_city_score = [['london', 1.0, 'United Kingdom'],
 ['rome', 1.0, 'Italy'],
 ['naples', 1.0, 'Italy'],
 ['malaga', 1.0, 'Spain'],
 ['alicante', 1.0, 'Spain'],
 ['amsterdam', 1.0, 'Netherlands'],
 ['stockholm', 1.0, 'Sweden'],
 ['barcelona', 1.0, 'Spain'],
 ['berlin', 1.0, 'Germany'],
 ['madrid', 1.0, 'Spain'],
 ['milan', 1.0, 'Italy'],
 ['venice', 1.0, 'Italy'],
 ['brussels', 1.0, 'Belgium'],
 ['manchester', 1.0, 'United Kingdom'],
 ['budapest', 1.0, 'Hungary'],
 ['palma', 1.0, 'Spain'],
 ['copenhagen', 1.0, 'Denmark'],
 ['paris', 1.0, 'France'],
 ['porto', 1.0, 'Portugal'],
 ['dublin', 1.0, 'Ireland'],
 ['sofia', 0.9629629629629629, 'Bulgaria'],
 ['liverpool', 0.9629629629629629, 'United Kingdom'],
 ['wroclaw', 0.9259259259259259, 'Poland'],
 ['prague', 0.9259259259259259, 'Czechia'],
 ['seville', 0.9259259259259259, 'Spain'],
 ['athens', 0.9259259259259259, 'Greece'],
 ['lisbon', 0.9259259259259259, 'Portugal'],
 ['valencia', 0.8888888888888888, 'Spain'],
 ['barcelona', 0.8888888888888888, 'Spain'],
 ['helsinki', 0.8518518518518519, 'Finland'],
 ['ibiza', 0.8148148148148148, 'Spain'],
 ['vilnius', 0.8148148148148148, 'Lithuania'],
 ['marrakech', 0.8148148148148148, 'Morocco'],
 ['oslo', 0.8148148148148148, 'Norway'],
 ['belfast', 0.8148148148148148, 'United Kingdom'],
 ['lanzarote', 0.7777777777777778, 'Spain'],
 ['las-palmas', 0.7777777777777778, 'Spain'],
 ['munich', 0.7777777777777778, 'Germany'],
 ['zurich', 0.7407407407407407, 'Switzerland'],
 ['salzburg', 0.7407407407407407, 'Austria'],
 ['vienna', 0.7037037037037037, 'Austria'],
 ['bratislava', 0.7037037037037037, 'Slovakia'],
 ['riga', 0.7037037037037037, 'Latvia'],
 ['bilbao', 0.7037037037037037, 'Spain'],
 ['mikonos', 0.5925925925925926, 'Greece'],
 ['santander', 0.5925925925925926, 'Spain'],
 ['dubrovnik', 0.5555555555555556, 'Croatia'],
 ['fuerteventura', 0.5555555555555556, 'Spain'],
 ['santiago-de-compostela', 0.5555555555555556, 'Spain'],
 ['mahon', 0.5185185185185185, 'United States'],
 ['asturias', 0.48148148148148145, 'Spain'],
 ['granada', 0.4074074074074074, 'Spain'],
 ['almeria', 0.37037037037037035, 'Spain'],
 ['tenerife', 0.3333333333333333, 'Spain'],
 ['santa-cruz-de-la-palma', 0.2962962962962963, 'Spain'],
 ['murcia', 0.2962962962962963, 'Spain'],
 ['vigo', 0.2962962962962963, 'Spain'],
 ['zaragoza', 0.2962962962962963, 'Spain'],
 ['jerez', 0.25925925925925924, 'Spain']]

df_normalized_city_score = pd.DataFrame(normalized_city_score,columns=["city","score", "country"])

# Función que coge json y lo convierte en list of lists
def add_to_table(result):
  price_matrix = []
  # Le metemos cada valor
  for r in range(len(result["data"])):
    price_row = []
    price_row.append(result["data"][r]["route"][0]["cityFrom"])
    price_row.append(result["data"][r]["route"][0]["cityTo"])
    price_row.append(result["data"][r]["route"][0]["mapIdto"])
    price_row.append(datetime.datetime.fromtimestamp(int(result["data"][r]["route"][0]["aTimeUTC"])).strftime('%H:%M:%S'))
    price_row.append(datetime.datetime.fromtimestamp(int(result["data"][r]["route"][0]["aTimeUTC"])).strftime('%Y-%m-%d'))
    price_row.append(result["data"][r]["price"])
    price_row.append(result["data"][r]["route"][0]["id"])
    price_matrix.append(price_row)
  return price_matrix

# le metes origen, destinos y fecha y te da el list of lists
def precioTrayectos(origen, destinos, fecha, pasajeros):
  # si input es una lista al convertir a string tenemos que quitar los corchetes [ ]
  destinos = str(destinos).replace("'", "").replace(" ", "").replace("[", "").replace("]", "")
  #print("Get prices from {} to {} on {}".format(origen, destinos, fecha))
  if len(destinos) == 0:
    destinos = ""
  if not pasajeros:
    pasajeros = 1
  params = {
            "partner":"picky",
            "locale":"es",
            "curr":"EUR",
            "dateFrom": fecha,
            "dateTo": fecha,
            "directFlights": 1,
            "oneforcity": 1,
            "passengers": pasajeros,
            "flyFrom": origen,
            "to": destinos,
            "limit": 20            
  }
  host = "https://api.skypicker.com/flights"
  resp_code = 0
  req_attempts = 0
  while resp_code != 200:
    response = requests.get(host, params = params)
    resp_code = response.status_code
    req_attempts += 1
    if resp_code != 200:
      print('Response code of attempt {} is: {}'.format(req_attempts, resp_code))
  full_matrix = add_to_table(response.json())
  return full_matrix


# Función que suma días
def addDays(fecha,days):
  fecha = datetime.datetime.strptime(fecha, "%d/%m/%Y")
  fecha2 = fecha + datetime.timedelta(days=int(days))
  return datetime.datetime.strftime(fecha2, "%d/%m/%Y")


# Class que usaremos luego para pasar a json
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)




# Función equivalente a fullMatrix pero sin destinos fijos
def fullMatrixNoDestinos(origen, df_normalized_city_score, fecha_salida, dias_por_ciudad, numero_ciudades, pasajeros):
  # df_normalized_city_score es un df, convertimos la primera columna a list para tenerlo más manejable
  cool_connections = df_normalized_city_score["city"].tolist()
  
  full_matrix = pd.DataFrame(columns=["From","To","CodeTo","Hour","Date","Price","Id","Score"])
  # Ida
  # Creamos una lista, dentro de ella pondremos más listas con los destinos para que hagan de orígenes en la siguiente iteración
  origins = []
  # Buscamos los 20 vuelos más baratos desde el origen y convertimos el resultado a df
  precios_ida = precioTrayectos(origen,"",fecha_salida, pasajeros)
  df_precios_ida = pd.DataFrame(precios_ida,columns=["From","To","CodeTo","Hour","Date","Price","Id"])
  # Sacamos el precio del vuelo más caro
  precio_max = df_precios_ida.loc[df_precios_ida['Price'].idxmax()]["Price"]
  # Filtramos solo los vuelos que acaban en un destino de cool_connections
  filtered_df = df_precios_ida[df_precios_ida["CodeTo"].isin(cool_connections)]
  # Añadimos al df una columna con el score de cada ciudad y ordenamos
  filtered_df.loc[:,"Score"] = 1 - (filtered_df.loc[:,"Price"] / precio_max)
  filtered_df.sort_values("Score",ascending = False)
  # Cogemos los cinco destinos con mayor score y los añadimos a origins para la siguiente iteración
  origins.append(filtered_df.loc[:4,"CodeTo"].tolist())
  # Y guardamos toda la info de los tres viajes en el df full_matrix
  full_matrix = full_matrix.append(filtered_df.loc[:2])

  # Trayectos intermedios
  # Loopeamos en función del número de ciudades que el user quiere ver -1
  for c in range(numero_ciudades - 1):
    # Sumamos días a la fecha de salida
    fecha_salida = addDays(fecha_salida, dias_por_ciudad)
    origins.append([])
    # Buscamos vuelos desde cada uno de los destinos de la fecha anterior
    for o in origins[-2]:
      # print("estamos buscando vuelos desde " + d + "el día " + str(c))
      # Sacamos precios y convertimos a df
      precios_ida = precioTrayectos(o,"",fecha_salida, pasajeros)
      df_precios_ida = pd.DataFrame(precios_ida,columns=["From","To","CodeTo","Hour","Date","Price","Id"])
      #print(df_precios_ida)
      # Sacamos el precio del vuelo más caro
      precio_max = df_precios_ida.loc[df_precios_ida['Price'].idxmax()]["Price"]
      # Filtramos solo los vuelos que acaban en un destino de cool_connections
      filtered_df = df_precios_ida[df_precios_ida["CodeTo"].isin(cool_connections)]
      # Añadimos al df una columna con el score de cada ciudad y ordenamos
      filtered_df.loc[:,"Score"] = 1 - (filtered_df.loc[:,"Price"] / precio_max)
      filtered_df.sort_values("Score",ascending = False)
      # Cogemos los cinco destinos con mayor score y si no están ya, los añadimos a origins para la siguiente iteración
      new_origins = filtered_df.loc[:4,"CodeTo"].tolist()
      for x in new_origins:
        if x not in origins[-1]:
          origins[-1].append(x)
      # print(origins)          
      # Y guardamos toda la info de los tres viajes en el df full_matrix
      full_matrix = full_matrix.append(filtered_df.loc[:2]) 
      full_matrix
              
  # Vuelta
  fecha_salida = addDays(fecha_salida, dias_por_ciudad)
  for o in origins[-1]:
    precio_vuelta = precioTrayectos(o, origen, fecha_salida, pasajeros)
    df_precio_vuelta = pd.DataFrame(precio_vuelta,columns=["From","To","CodeTo","Hour","Date","Price","Id"])
    df_precio_vuelta["Score"] = 1
    # Los añadimos todos al full_matrix
    full_matrix = full_matrix.append(df_precio_vuelta)

  return full_matrix

def generateAllDates(first_date, number_cities, days_city):
  dates_list = [first_date]
  for i in range(number_cities):
    next_date = addDays(dates_list[-1], days_city)
    dates_list.append(next_date)
  return dates_list


def getCoolCities(cool_connections, current_city):
  cool_cities = []
  for city in cool_connections:
    if (city['city'] == current_city):
      cool_cities = city['connections'].copy()
      break
  return cool_cities


# Función para rellenar la info de todos los vuelos a partir de las "cool cities"
def fullFlightsMatrix(flights_info, connections, dates, origin, current_city, n_cities_to_visit, passengers):
  flights_from_city = pd.DataFrame(columns = flights_info.columns)
  current_date = dates[-(n_cities_to_visit + 1)]
  print("Starting iteration with {} cities pending, from {} at {}".format(n_cities_to_visit, current_city, current_date))
  if n_cities_to_visit >= 0:
    # there are still cities to visit
    if n_cities_to_visit <= 0:
      # all cities have been visited, must go back to depature
      print("It's the last fligh, must come back to {}".format(origin))
      destinations = [origin]
    else:
      # we still have to see more combinations
      destinations = connections[connections["City"] == current_city]["Connections"].tolist()
      print("All the cool destinations from {} are: {}".format(current_city, destinations))
    flights_from_city_found = getJourneysPrice(current_city, destinations, current_date, passengers)
    print("{} flights found from {}:\n{}".format(len(flights_from_city_found), current_city,
                                                 flights_from_city_found.loc[:, flights_from_city_found.columns != 'Id']))
    # add the flights found into the existing dataframe
    flights_from_city = pd.concat([flights_from_city, flights_from_city_found], ignore_index=True)
    # for each city where we found a flight, compute recursively
    cities_to_visit = list(flights_from_city['CodeTo'])
    for dest_city in cities_to_visit:
      # check that the same flight (from, to, date) is not already added by another threat
      rows_same_date = (flights_info["Date"] == current_date)
      rows_same_depart = (flights_info["From"] == current_city)
      if ((dest_city not in flights_info[rows_same_date & rows_same_depart]['CodeTo']) and
          (dest_city not in origin) and (n_cities_to_visit > 0)):
        print("Starting recursive call from", current_city, "to", dest_city,"The others are:",cities_to_visit)
        flights_from_city = pd.concat([flights_from_city,
                                  fullFlightsMatrix(flights_info, connections, dates, origin, dest_city, n_cities_to_visit-1, passengers)],
                                  ignore_index=True)
        print("FInished recursive call from", current_city, "to", dest_city)
      else:
        print(dest_city, "has been already considered as destination on", current_date)
    print("Flights from citys after the successive calls:\n", flights_from_city.loc[:, flights_from_city.columns != 'Id'])
  else:
    # no more trips remaining
    print("fullFlightMatrix terminated in", current_city, "at", current_date)
  return flights_from_city


# Esta función hace algo parecido a full matrix, solo que a medida que avanza va mirando añadiendo como
# destino las "cool connections" de cada una de las ciudades encontradas.
origen = "BCN"
fecha = "15/07/2018"
dias_por_ciudad = 2
ciudades_minimas_visitar = 2

dates = generateAllDates(fecha, ciudades_minimas_visitar, dias_por_ciudad)
print(dates)
pasajeros = 1
combinaciones = 10

list_of_tags = ["From",'To','CodeTo','Hour','Date','Price','Id']
cool_flights_matrix = pd.DataFrame(columns = pd.Series(list_of_tags))

cool_flights_matrix = fullFlightsMatrix(cool_flights_matrix, test2, dates, origen, origen, ciudades_minimas_visitar, pasajeros)
cool_flights_matrix.sort_values(["From","Date"], inplace = True)
print(cool_flights_matrix)


def fullMatrixConDestinos(origen, destinos, fecha_salida,dias_por_ciudad, numero_ciudades, pasajeros):
  # De origen a cada destino
  first_flight_options = precioTrayectos(origen, destinos, fecha_salida, pasajeros)
  #print('first_flight_options:\n', first_flight_options)

  # Loop que busca todas las combinaciones entre destinos
  in_between_flights_options = []
  for i in range(numero_ciudades - 1):
    fecha_salida = addDays(fecha_salida,dias_por_ciudad)
    for departure_city in destinos:
      other_cities = [city for city in destinos if city != departure_city]
      
      flights_current_city = precioTrayectos(departure_city, other_cities, fecha_salida, pasajeros)
      in_between_flights_options += flights_current_city
      #print('Starting from {}, checking destinations: {}.\n'.format(departure_city, other_cities), flights_current_city)

  # Loop que busca los viajes de vuelta
  fecha_salida = addDays(fecha_salida,dias_por_ciudad)
  last_flight_options = []
  for d in destinos:
    last_flight_options += precioTrayectos(d, origen, fecha_salida, pasajeros) 
    #print('last_flight_options from {} to {} on {}:\n'.format(d, origen, fecha_salida), [element[1] for element in last_flight_options])

  # Convertimos los tres trozos en Series y los metemos en un dataframe
  columnas = pd.Series(["From", "To", "CodeTo", "Hour", "Date", "Price", "Id"])
  final_matrix1 = pd.DataFrame(first_flight_options, columns=columnas)
  final_matrix2 = pd.DataFrame(in_between_flights_options, columns=columnas)
  final_matrix3 = pd.DataFrame(last_flight_options, columns=columnas)

  full_matrix = pd.concat([final_matrix1, final_matrix2, final_matrix3])
  #print(full_matrix.loc[:, full_matrix.columns != 'Id'])
  return full_matrix

result = precioTrayectos("BCN", "MAD", "11/08/2018", 1) 
result

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
    full_matrix = fullMatrixNoDestinos(origen, df_normalized_city_score, fecha_salida, dias_por_ciudad, numero_ciudades, pasajeros)
  # Si no, seguimos con la fullMatrixConDestinos
  else:
    print("Los destinos son:", destinos)
    full_matrix = fullMatrixConDestinos(origen, destinos, fecha_salida,dias_por_ciudad, numero_ciudades, pasajeros)
  full_matrix.sort_values(["Date","Price"])
  return full_matrix #final_json

origen = "madrid"
destinos_posibles = ['BCN', 'PAR', 'LON', 'BER']
fecha = "11/08/2018"
dias_por_ciudad = 2
numero_ciudades = 3
pasajeros = 1
combinaciones = 5
full_matrix = fullMatrix(origen, destinos_posibles, fecha, dias_por_ciudad, numero_ciudades, pasajeros, combinaciones)

full_matrix

origen = "madrid"
destinos_posibles = []
fecha = "11/08/2018"
dias_por_ciudad = 2
numero_ciudades = 3
pasajeros = 1
combinaciones = 5
full_matrix = fullMatrix(origen, destinos_posibles, fecha, dias_por_ciudad, numero_ciudades, pasajeros, combinaciones)

full_matrix

def getMatrixAndCombinations (origen, destinos, fecha_salida, dias_por_ciudad, numero_ciudades, pasajeros, n_combinaciones):
  """
  Esta funcion tiene como entrada los inputs del usuario. Crea la matriz de vuelos usando fullMatrix, saca los inputs necesarios
  para llamar a "findbestpathloc", y del df de combinacioneshace el return del json.
  """
  # Sacamos el DF con la info de todos los vuelos necesarios
  full_matrix = fullMatrix(origen, destinos, fecha_salida,dias_por_ciudad, numero_ciudades, pasajeros, n_combinaciones)
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
  #best_combinations_dict = convertCombinationDfToDict(all_combinations_flights, pasajeros))
  # Convertimos a json
  #best_combinations_json = json.dumps(best_combinations_dict, cls=MyEncoder)
  
  return best_combinations_df

origen = "madrid"
destinos_posibles = ['BCN', 'PAR', 'LON', 'BER']
fecha = "11/08/2018"
dias_por_ciudad = 2
numero_ciudades = 3
pasajeros = 2
combinaciones = 5
combinations_df = getMatrixAndCombinations (origen, destinos_posibles, fecha, dias_por_ciudad, numero_ciudades, pasajeros, combinaciones)
combinations_df

origen = "madrid"
destinos_posibles = []
fecha = "11/08/2018"
dias_por_ciudad = 2
numero_ciudades = 3
pasajeros = 2
combinaciones = 5
combinations_df = getMatrixAndCombinations (origen, destinos_posibles, fecha, dias_por_ciudad, numero_ciudades, pasajeros, combinaciones)
combinations_df

test_full_matrix = fullMatrixNoDestinos("madrid", df_normalized_city_score, "11/08/2018", 2, 3, 2)

test_full_matrix

origen = "BCN"
destinos_posibles = ["DUB", "VIE", "ATH","TLS"]
fecha = "15/07/2018"
dias_por_ciudad = 2
ciudades_minimas_visitar = 3
pasajeros = 1
combinaciones = 10
full_matrix = fullMatrix(origen, destinos_posibles, fecha, dias_por_ciudad, ciudades_minimas_visitar, pasajeros, combinaciones)
full_matrix
solucion="""
2  Barcelona  [Atenas, Toulouse, Dublín, Barcelona]   
0  Barcelona   [Toulouse, Atenas, Viena, Barcelona]   
3  Barcelona     [Dublín, Viena, Atenas, Barcelona]   
1  Barcelona  [Toulouse, Atenas, Dublín, Barcelona]   
"""

origen = "BCN"
destinos_posibles = ["LPL","DUB", "VIE", "ATH","TLS", "MPL"]
fecha = "15/08/2018"
dias_por_ciudad = 2
ciudades_minimas_visitar = 3
pasajeros = 1
combinaciones = 10
full_matrix = fullMatrix(origen, destinos_posibles, fecha, dias_por_ciudad, ciudades_minimas_visitar, pasajeros, combinaciones)
full_matrix
solucion="""
1  Barcelona  [Liverpool, Dublín, Toulouse, Barcelona]   
4  Barcelona     [Viena, Dublín, Liverpool, Barcelona]   
0  Barcelona    [Liverpool, Dublín, Atenas, Barcelona]   
3  Barcelona     [Liverpool, Dublín, Viena, Barcelona]   
2  Barcelona        [Atenas, Viena, Dublín, Barcelona]   
"""

origen = "BCN"
destinos_posibles = ["BUD","OTP", "SOF", "PRG", "ATH", "KRK", "WAW", "DBK", "BTS"]
fecha = "15/08/2018"
dias_por_ciudad = 3
ciudades_minimas_visitar = 3
pasajeros = 1
combinaciones = 4
full_matrix = fullMatrix(origen, destinos_posibles, fecha, dias_por_ciudad, ciudades_minimas_visitar, pasajeros, combinaciones)
full_matrix
solucion= """
1  Barcelona  [Praga, Varsovia, Bratislava, Gerona]   
2  Barcelona    [Sofía, Budapest, Praga, Barcelona]   
0  Barcelona   [Sofía, Atenas, Bucarest, Barcelona]   
3  Barcelona   [Sofía, Atenas, Budapest, Barcelona]
"""

origen = "BCN"
destinos_posibles = ["BUD","OTP", "SOF", "ATH", "KRK", "WAW", "DBK", "BTS"]
fecha = "15/08/2018"
dias_por_ciudad = 3
ciudades_minimas_visitar = 3
pasajeros = 1
combinaciones = 10
full_matrix = fullMatrix(origen, destinos_posibles, fecha, dias_por_ciudad, ciudades_minimas_visitar, pasajeros, combinaciones)
full_matrix
solucion="""
2  Barcelona     [Sofía, Budapest, Varsovia, Barcelona]   
0  Barcelona       [Sofía, Atenas, Bucarest, Barcelona]   
3  Barcelona       [Sofía, Atenas, Budapest, Barcelona]   
6  Barcelona        [Sofía, Atenas, Bratislava, Gerona]   
8  Barcelona       [Sofía, Atenas, Varsovia, Barcelona]   
4  Barcelona       [Budapest, Sofía, Atenas, Barcelona]   
1  Barcelona  [Varsovia, Bratislava, Atenas, Barcelona]   
7  Barcelona       [Atenas, Sofía, Budapest, Barcelona]   
9  Barcelona       [Bucarest, Atenas, Sofía, Barcelona]   
5  Barcelona      [Sofía, Varsovia, Bratislava, Gerona]   
"""

full_matrix

d = json.loads(full_matrix)
d
