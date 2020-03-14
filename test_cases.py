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

    Concatenations accepted.
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


def test_if_statement(line):
    """Checks if the first line begins with if (...):

    Key argument:
    -- line: str

    Returns:
    -- True or False: Bool
    """
    if re.match(r'^if (.*?)+:$', line) is not None:
        return True
    else:
        return False


def in_if_block(line, initial_indent):
    """Check if the line is still in the if block.

    Key argument:
    -- line: dict ({"content": x, "indents": y})

    If it is further tabbed or it is on the same line,
    and is the "else:" statement,
    then it is still in the if-block.
    Otherwise, it is not.
    """
    if (line["indents"] > initial_indent or
            (re.match(r'else:', line["content"]) is not None and
             line["indents"] == initial_indent)):
        return True
    else:
        return False


def transform_if_statement(lines, initial_indent=0):
    """Transforms the if-statement.

    Key arguments:
    -- lines: str
    -- initial_indent: int (default: 0)

    Returns:
    -- List of dict ([{"content": x, "indents": y}])

    The indents of the lines are to match the original document,
    and note that the succeeding indents are automatically decided
    by the function. Thus, only the inital_indent is needed.
    """
    print(lines)
    converted_lines = []

    #  Establish the first line
    first_if_line = lines.pop(0)
    condition = first_if_line.split(' ', 1)[1]
    condition = condition[:-1]  # Remove the semi-colon

    # Check if double equal sign is present
    # If so, replace it with a single '=' sign
    rx = re.compile(r'"[^"]+"|([==])')
    sign = [
        match.group(1) for match in rx.finditer(condition) if match.group(1)
    ]
    if sign == ['=', '=']:
        equal_separator = re.compile(r'''((?:[^=="']|"[^"]*"|'[^']*')+)''')
        items = equal_separator.split(condition)[1::2]
        condition = items[0].strip() + " = " + items[1].strip()

    # Append first line
    converted_first_line = {
        "content": "IF " + condition,
        "indents": initial_indent
    }
    converted_lines.append(converted_first_line)

    # Before 'ELSE' statement
    then_call = {
        "content": "THEN",
        "indents": initial_indent + 4
    }
    converted_lines.append(then_call)

    then_block = []
    while re.match(r'^else:', lines[0]) is None:
        then_block.append(lines.pop(0))

    converter = PseudocodeConverter(then_block, initial_indent)
    then_statements = converter.get_converted_lines()

    for statement in then_statements:
        statement["indents"] = initial_indent + (2 * 4)
        converted_lines.append(statement)

    # 'ELSE' statement, if it exists
    if re.match(r'^else:', lines[0]) is not None:
        lines.pop(0)
        else_call = {
            "content": "ELSE",
            "indents": initial_indent + 4
        }
        converted_lines.append(else_call)

        else_block = []
        while len(lines) > 0:
            else_block.append(lines.pop(0))

        pseudocodeConverter = PseudocodeConverter(else_block, initial_indent)
        else_statements = pseudocodeConverter.get_converted_lines()

        for statement in else_statements:
            statement["indents"] = initial_indent + (2 * 4)
            converted_lines.append(statement)

    # Final 'ENDIF' statement
    endif_call = {"content": "ENDIF", "indents": initial_indent}
    converted_lines.append(endif_call)

    return converted_lines


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


class PseudocodeConverter:
    block_lines = []
    converted_lines = []

    def __init__(self, lines, initial_indent=0):
        self.converted_lines = []
        start_block_indent = initial_indent
        while len(lines) > 0:
            current_line = self.get_current_line(lines)

            if test_input(current_line["content"]) is not None:
                for i in test_input(current_line["content"]):
                    line_to_add = {
                        "content": i,
                        "indents": current_line["indents"]
                    }
                    self.converted_lines.append(line_to_add)
            elif test_print(current_line["content"]) is not None:
                current_line["content"] = test_print(
                    current_line["content"]
                )
                self.converted_lines.append(current_line)
            elif test_assignment(current_line["content"]) is not None:
                current_line["content"] = test_assignment(
                    current_line["content"]
                )
                self.converted_lines.append(current_line)
            elif test_if_statement(current_line["content"]):
                # Check if got elif

                # Initialize if_block
                if_block = []
                if_block.append(current_line["content"])

                start_block_indent = current_line["indents"]

                block_check = True
                while block_check and len(lines) > 0:
                    current_line = self.get_current_line(lines)
                    if in_if_block(current_line, start_block_indent):
                        if_block.append(current_line["content"])
                    else:
                        block_check = False

                lines_to_append = transform_if_statement(
                    if_block, start_block_indent
                )
                for line in lines_to_append:
                    self.converted_lines.append(line)

            # print(current_line, self.converted_lines)

    def get_current_line(self, lines):
        """Gets the current line.

        Key arguments:
        -- lines: str

        Returns:
        -- current_line: dict ({"content": x, "indents": y})

        It treats 'lines' as a queue system,
        dequeuing the first element,
        and transforming that into a dict,
        then returning it.
        """
        current_line = lines.pop(0)
        if re.findall(r'^\s+', current_line) == []:
            indents = 0
        else:
            indents = len(re.findall(r'^\s+', current_line)[0])
        current_line = {
            "content": current_line.lstrip(),
            "indents": indents
        }

        return current_line

    def get_converted_lines(self):
        """Gets block lines.

        Returns:
        --block_lines: dict ({"content": x, "indents": y})
        """
        # print("get_converted_lines", self.converted_lines)
        return self.converted_lines
