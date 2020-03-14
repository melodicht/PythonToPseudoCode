from test_cases import PseudocodeConverter

# filename = input("What is the name of the file? ")
filename = "test 3"

line_series = [line.rstrip('\n') for line in open(filename + '.py')]

print(line_series)
converter = PseudocodeConverter(line_series)
converted_lines = converter.get_converted_lines()

with open(filename + " pseudocode.txt", 'w') as f:
    for line in converted_lines:
        print(line)
        text = (" " * line["indents"]) + line["content"]
        f.write(text)
        f.write("\n")  # Create new lines
