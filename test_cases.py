import re


def test_assignment(line):
    """Checks to see if there is an assignment.

    Key argument:
    -- line: str

    This works for all types of variables.
    If it is a boolean, it will lowered case.
    Functions have not been taken into consideration as of now.
    """
    match_object = re.search(r'^\w+ = (.*?)$', line)
    if match_object is not None:
        words = line.split('=', 1)  # Split on first occurence
        variable = transform_identifier(words[0]).strip()
        value = match_object.group(1).strip()
        if value == 'True' or value == 'False':
            value = value.lower()  # As per pseudocode conventions
        return (variable + " <- " + value)

    return None


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

    If there is string concatenation with the '+' sign,
    the '+' sign is replaced with a comma.
    """
    # If conditions are unmet, return None
    if re.match(r'^print', line) is None:
        return None
    elif re.search(r'^print(.*?)\(', line).group(1) != "":
        return None

    text = re.search(r'\((.*?)\)$', line).group(1)

    if re.search(r'\+', text) is not None:
        # Plus signs inside quotes are not counted
        plus_separator = re.compile(r'''((?:[^\+"']|"[^"]*"|'[^']*')+)''')
        items = plus_separator.split(text)[1::2]
        final_text = transform_identifier(items.pop(0).strip())
        for item in items:
            final_text += (", " + transform_identifier(item.strip()))

        text = final_text
    else:
        text = transform_identifier(text)

    return("OUTPUT " + text)


def test_input(line):
    """Checks to see if there is the input() function.

    Key argument:
    -- line: str

    If there is a parameter in the input function,
    then it will be displayed as 'OUTPUT X',
    where X is the parameter, as per the conventions.
    Ultimately, it will lead to 'INPUT var',
    where var is the variable to store
    the return value of the input() function.
    """
    # If conditions are unmet, return None
    if re.match(r'^[a-zA-Z0-9\_]+ = input', line) is None:
        return None
    elif re.search(r'^[a-zA-Z0-9\_]+ = input(.*?)\(', line).group(1) != "":
        return None

    output = []
    quotation = re.search(r'input\((.*?)\)$', line).group(1)

    words = line.split('=', 1)  # Split on first occurence
    # Since the first word is the variable
    variable = transform_identifier(words[0].strip())

    if quotation != "":
        output.append("OUTPUT " + quotation)

    output.append("INPUT " + variable)

    return output


def transform_identifier(text):
    """Transforms the identifier to meet conventions.

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
        new_text = words.pop(0)
        for word in words:
            new_text += word.capitalize()

        return new_text

    return text


def test_cases(lines):
    new_line = []
    for index, line in enumerate(lines):
        if test_input(line) is not None:
            for i in test_input(line):
                new_line.append(i)
        elif test_print(line) is not None:
            new_line.append(test_print(line))
        elif test_assignment is not None:
            new_line.append(test_assignment(line))

    return new_line
