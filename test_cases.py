import re
from utility import get_word_compile, check_if_word_exist, separate_on_word


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
        value = lower_booleans(value)
        return (variable + " <- " + value)

    return None


def lower_booleans(text):
    """If text is a bool, lower it."""
    if text == 'True' or text == 'False':
        text = text.lower()

    return text


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
        items = separate_on_word("+", text)

        # Replacing the old text with converted new text
        final_text = transform_identifier(items.pop(0))
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


def replace_operator_in_condition(original, result, condition):
    """Replaces the operator.

    Key arguments:
    -- original: str
    -- result: str
    -- condition: str
    """
    items = separate_on_word(original, condition)

    # Transforms to the identifier to meet conventions
    condition1 = transform_identifier(items[0])
    condition2 = transform_identifier(items[1])

    # If it is a bool, lower it
    condition1 = lower_booleans(condition1)
    condition2 = lower_booleans(condition2)

    condition = condition1 + " " + result + " " + condition2
    return condition


def is_or_is_not(condition):
    """Differentiates between 'is' or 'is not'."""
    if check_if_word_exist("is not", condition):
        return replace_operator_in_condition("is not", "<>", condition)
    elif check_if_word_exist("is", condition):
        return replace_operator_in_condition("is", "=", condition)

    return None


def equal_or_not_equal_to(condition):
    """Differentiates between 'equal' or 'not equal to'."""
    if check_if_word_exist("!=", condition):
        return replace_operator_in_condition("!=", "<>", condition)
    elif check_if_word_exist("==", condition):
        return replace_operator_in_condition("==", "=", condition)

    return None


def not_condition(condition):
    """Checks if there is 'not' in the condition."""
    if check_if_word_exist("not", condition):
        condition = transform_identifier(condition.split(" ", 1)[1].strip())
        condition = lower_booleans(condition)
        condition = "NOT " + condition
        return condition

    return None


def transform_conditions(conditions):
    """Transforms the conditions into accepted standards.

    Returns:
    -- new_conditions: list of str
    """
    new_conditions = []
    for condition in conditions:
        condition = condition.strip()
        if equal_or_not_equal_to(condition) is not None:
            condition = equal_or_not_equal_to(condition)
        elif is_or_is_not(condition) is not None:
            condition = is_or_is_not(condition)
        elif not_condition(condition) is not None:
            condition = not_condition(condition)
        else:
            condition = transform_identifier(condition)

        new_conditions.append(condition)

    return new_conditions


def transform_if_statement(lines, initial_indent=0):
    """Transforms the if-statement.

    Key arguments:
    -- lines: list of dict ([{"content": x, "indents": y}])
    -- initial_indent: int (default: 0)

    Returns:
    -- List of dict ([{"content": x, "indents": y}])
    """
    converted_lines = []

    #  Establish the first line
    first_if_line = lines.pop(0)["content"]
    conditions = first_if_line.split(' ', 1)[1].strip()
    conditions = conditions[:-1]  # Remove the semi-colon

    # Disect conditions, on 'or' and 'and'
    logical_operators = get_word_compile("and|or", conditions)

    operators_order = logical_operators.findall(conditions)
    # Turn into array
    conditions = separate_on_word("and|or", conditions)
    conditions = transform_conditions(conditions)

    # Stack them into what string
    full_conditions = ""
    for i in range(len(operators_order)):
        full_conditions += conditions[i]
        full_conditions += " "
        full_conditions += operators_order[i]
        full_conditions += " "
    full_conditions += conditions[-1]
    conditions = full_conditions

    # Append first line
    converted_first_line = {
        "content": "IF " + conditions,
        "indents": initial_indent
    }
    converted_lines.append(converted_first_line)

    # Before 'ELSE' statement, if that exists
    then_call = {
        "content": "THEN",
        "indents": initial_indent + 4
    }
    converted_lines.append(then_call)

    then_block = []
    while (len(lines) > 0 and
            (re.match(r'^else:', lines[0]["content"]) is None or
             lines[0]["indents"] != initial_indent)):
        new_dict = lines.pop(0)
        new_line = " " * new_dict["indents"] + new_dict["content"]
        then_block.append(new_line)

    converter = PseudocodeConverter(then_block, initial_indent)
    then_statements = converter.get_converted_lines()

    for statement in then_statements:
        statement["indents"] = initial_indent + statement["indents"] + 4
        converted_lines.append(statement)

    # 'ELSE' statement, if it exists
    if (len(lines) > 0 and
            (re.match(r'^else:', lines[0]["content"]) is not None and
             lines[0]["indents"] == initial_indent)):
        lines.pop(0)  # Remove 'else:' line
        else_call = {
            "content": "ELSE",
            "indents": initial_indent + 4
        }
        converted_lines.append(else_call)

        else_block = []
        while len(lines) > 0:
            new_dict = lines.pop(0)
            new_line = (" " * new_dict["indents"]) + new_dict["content"]
            else_block.append(new_line)

        pseudocodeConverter = PseudocodeConverter(else_block, initial_indent)
        else_statements = pseudocodeConverter.get_converted_lines()

        for statement in else_statements:
            statement["indents"] = initial_indent + statement["indents"] + 4
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
    if check_if_word_exist("_", text):
        underscore_separator = re.compile(
            r'''((?:[^\_"']|"[^"]*"|'[^']*')+)'''
        )
        words = underscore_separator.split(text)[1::2]
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
                if_block.append(current_line)

                start_block_indent = current_line["indents"]

                block_check = True
                while block_check and len(lines) > 0:
                    current_line = self.get_current_line(lines)
                    if in_if_block(current_line, start_block_indent):
                        if_block.append(current_line)
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
            "content": current_line.strip(),
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


line = "x_cd is z_ab"
print(is_or_is_not(line))
