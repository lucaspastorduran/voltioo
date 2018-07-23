def sumDigits(number):
    return sum(int(digit)**2 for digit in str(number))

number_flights = 5
combinations = sorted([i for i in range(10**number_flights)],key = sumDigits)
print(combinations[:30])

"""
have a list of numbers
Generate all the possible permutations with N spaces with M numbers
Add one number to M numbersa
Generate all the possible permutations with N spaces: choose all the spaces where to put the new muber

_ _ _ _
0 0 0 0
nuevo número: el 1
combinaciones binarias de añadirlo en cada uno de los números anteriores
1 0 0 0
0 1 0 0
0 0 1 0
0 0 0 1
1 1 0 0
1 0 1 0
1 0 0 1
1 1 0 0
1 1 1 0
1 1 0 1
1 1 1 1
Añado el número 2, se lo añado en todas las posiciones a los números anteriores
0 0 0 2
0 0 2 0
0 2 0 0
2 0 0 0


"""