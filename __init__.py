import re

# filename = input("What is the name of the file? ")

# text = [line.rstrip('\n') for line in open(filename + '.py')]

# print(text)


# def test_cases(line):
#     test_print(line)


def test_print(line):
    """Check to see if it is a print statement.

    Key argument:
    -- line: str

    Returns:
    -- "OUTPUT X": str
    -- None (if match is invalid)

    If the line starts with 'print' and there is nothing between that and
    the opening rounded bracket, then,
    the text between the rounded brackets are identified,
    and returned along with 'OUTPUT'.
    """
    if re.match(r'^print', line) is None:
        return None
    elif re.search(r'^print(.*?)\(', line).group(1) != "":
        return None

    text = re.search(r'\((.*?)\)$', line).group(1)
    return("OUTPUT " + text)


def test_input(line):
    if re.match(r'input\(\)', line):  # If it is just input()
        words = line.split('=')
        # Since the first word is the variable
        variable = transform_identifier(words[0])

        return("INPUT " + variable)


def transform_identifier(text):
    """Transforms the identifier to meet convetions.

    Key arguments:
    -- text: str

    Since the '_' is the only character that contradicts pseudocode
    conventions in the python programming language,
    it first checks to see if there are any.
    If none, it will return the very same text.
    Otherwise, it will transform the identifier into camel case format.
    """
    if re.search(r'\_', text):
        words = text.split("_")
        new_text = words[0]
        words.pop(0)
        for word in words:
            new_text += word.capitalize()

        return new_text

    return text