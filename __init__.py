from test_cases import test_cases

filename = input("What is the name of the file? ")

line_series = [line.rstrip('\n') for line in open(filename + '.py')]

print(line_series)
new_doc = test_cases(line_series)

with open(filename + " pseudocode.txt", 'w') as f:
    for line in new_doc:
        f.write(line)
        f.write("\n")  # Create new lines
