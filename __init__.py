from test_cases import test_cases

filename = input("What is the name of the file? ")

line_series = [line.rstrip('\n') for line in open(filename + '.py')]

test_cases(line_series)
