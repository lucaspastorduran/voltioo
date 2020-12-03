#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 08:24:44 2018

@author: lucas
"""

import unittest

from find_combinations import *

class TestFindCombinations(unittest.TestCase):

    def test_empty_destinations(self):
        origen = "madrid"
        destinos_posibles = []
        fecha = "11/08/2018"
        dias_por_ciudad = 2
        numero_ciudades = 3
        pasajeros = 2
        combinaciones = 5
        combinations_df = getMatrixAndCombinations (origen, destinos_posibles, fecha, dias_por_ciudad, numero_ciudades, pasajeros, combinaciones)
        print(combinations_df)
        self.assertTrue(True, "No errors returned")

    def test_4destinations_3cities_2days(self):
        origen = "madrid"
        destinos_posibles = ['BCN', 'PAR', 'LON', 'BER']
        fecha = "11/08/2018"
        dias_por_ciudad = 2
        numero_ciudades = 3
        pasajeros = 2
        combinaciones = 5
        combinations_df = getMatrixAndCombinations (origen, destinos_posibles, fecha, dias_por_ciudad, numero_ciudades, pasajeros, combinaciones)
        print(combinations_df)
        self.assertTrue(True, "No errors returned")

    def test_fullMatrixNoDestinos_normScoreInput(self):
        #test_full_matrix = fullMatrixNoDestinos("madrid", df_normalized_city_score, "11/08/2018", 2, 3, 2)
        #print(test_full_matrix)
        self.assertTrue(True, "No errors returned")

    def test_get_combinations_4dest_3cities_2days(self):
        origen = "BCN"
        destinos_posibles = ["DUB", "VIE", "ATH","TLS"]
        fecha = "15/07/2018"
        dias_por_ciudad = 2
        ciudades_minimas_visitar = 3
        pasajeros = 1
        combinaciones = 10
        full_matrix = getMatrixAndCombinations(origen, destinos_posibles, fecha, dias_por_ciudad, ciudades_minimas_visitar, pasajeros, combinaciones)
        print(full_matrix)
        solucion="""
        2  Barcelona  [Atenas, Toulouse, Dublín, Barcelona]   
        0  Barcelona   [Toulouse, Atenas, Viena, Barcelona]   
        3  Barcelona     [Dublín, Viena, Atenas, Barcelona]   
        1  Barcelona  [Toulouse, Atenas, Dublín, Barcelona]   
        """
        self.assertEqual(full_matrix, solucion)

    def test_get_combinations_6dest_3cities_2days(self):
        origen = "BCN"
        destinos_posibles = ["LPL","DUB", "VIE", "ATH","TLS", "MPL"]
        fecha = "15/08/2018"
        dias_por_ciudad = 2
        ciudades_minimas_visitar = 3
        pasajeros = 1
        combinaciones = 10
        full_matrix = getMatrixAndCombinations(origen, destinos_posibles, fecha, dias_por_ciudad, ciudades_minimas_visitar, pasajeros, combinaciones)
        full_matrix
        solucion="""
        1  Barcelona  [Liverpool, Dublín, Toulouse, Barcelona]   
        4  Barcelona     [Viena, Dublín, Liverpool, Barcelona]   
        0  Barcelona    [Liverpool, Dublín, Atenas, Barcelona]   
        3  Barcelona     [Liverpool, Dublín, Viena, Barcelona]   
        2  Barcelona        [Atenas, Viena, Dublín, Barcelona]   
        """
        self.assertEqual(full_matrix, solucion)

    def test_get_combinations_9dest_3cities_2days(self):
        origen = "BCN"
        destinos_posibles = ["BUD","OTP", "SOF", "PRG", "ATH", "KRK", "WAW", "DBK", "BTS"]
        fecha = "15/08/2018"
        dias_por_ciudad = 3
        ciudades_minimas_visitar = 3
        pasajeros = 1
        combinaciones = 4
        full_matrix = getMatrixAndCombinations(origen, destinos_posibles, fecha, dias_por_ciudad, ciudades_minimas_visitar, pasajeros, combinaciones)
        full_matrix
        solucion= """
        1  Barcelona  [Praga, Varsovia, Bratislava, Gerona]   
        2  Barcelona    [Sofía, Budapest, Praga, Barcelona]   
        0  Barcelona   [Sofía, Atenas, Bucarest, Barcelona]   
        3  Barcelona   [Sofía, Atenas, Budapest, Barcelona]
        """
        self.assertEqual(full_matrix, solucion)

    def test_get_combinations_8dest_3cities_3days(self):
        origen = "BCN"
        destinos_posibles = ["BUD","OTP", "SOF", "ATH", "KRK", "WAW", "DBK", "BTS"]
        fecha = "15/08/2018"
        dias_por_ciudad = 3
        ciudades_minimas_visitar = 3
        pasajeros = 1
        combinaciones = 10
        full_matrix = getMatrixAndCombinations(origen, destinos_posibles, fecha, dias_por_ciudad, ciudades_minimas_visitar, pasajeros, combinaciones)
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
        self.assertEqual(full_matrix, solucion)

if __name__ == '__main__':
    unittest.main()