import re
import itertools
from utility import get_word_compile, check_if_word_exist, separate_on_word


def test_assignment(line):
    """Checks to see if there is an assignment.

    Key argument:
    -- line: str

    This works for all types of variables.
    If it is a boolean, it will lowered case.
    Functions, except for input,
    have not been taken into consideration as of now.
    """
    output = []

    match_object = re.search(r'^\w+ = (.*?)$', line)
    if match_object is not None:
        words = line.split('=', 1)  # Split on first occurence
        variable = transform_identifier(words[0]).strip()
        value = transform_identifier(match_object.group(1).strip())

        if test_type_conversion(value, variable) is not None:
            conversion_str = test_type_conversion(value, variable)
            output.append([variable + " <- " + conversion_str])
            value = re.search(r'^[a-z]+\((.*?)\)$', value).group(1)

        if test_input(value, variable) is not None:
            output.append(test_input(value, variable))
        else:
            value = lower_booleans(value)  # If bool
            output.append([variable + " <- " + value])

        # Reverse and flatten the list
        output.reverse()
        output = list(itertools.chain.from_iterable(output))

        return output

    return None


def test_input(line, var_name):
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
    if re.match(r'^input', line) is None:
        return None
    elif re.search(r'^input(.*?)\(', line).group(1) != "":
        return None

    output = []  # Array needed since it return two lines
    quotation = re.search(r'input\((.*?)\)$', line).group(1)

    if quotation != "":
        output.append("OUTPUT " + quotation)

    output.append("INPUT " + var_name)

    return output


def test_type_conversion(text, var_name):
    if (re.match(r'^str', text) is not None and
            re.search(r'^str(.*?)\(', text).group(1) == ""):
        enclosed_str = re.search(r'^str\((.*?)\)$', text).group(1)
        text = text.replace("str", "NUM_TO_STRING", 1)
        text = text.replace(enclosed_str, var_name)
        return text
    elif (re.match(r'^int', text) is not None and
            re.search(r'^int(.*?)\(', text).group(1) == ""):
        enclosed_str = re.search(r'^int\((.*?)\)$', text).group(1)
        text = text.replace("int", "STRING_TO_NUM", 1)
        text = text.replace(enclosed_str, var_name)
        return text

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

    # Deals with concatenations as well
    items = separate_on_word("+", text)
    converted_text = transform_identifier(items.pop(0))
    for item in items:
        converted_text += (", " + transform_identifier(item))

    return("OUTPUT " + converted_text)


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
    -- initial_indent: int

    If it is further tabbed, or it is on the same line
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

    Returns:
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


def convert_conditions(conditions):
    """Transforms the conditions into accepted standards.

    Key argument:
    -- conditions: list of str

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


def transform_all_conditions(conditions):
    """Transforms all the conditions.

    Key argument:
    -- conditions: list of str

    The logical operators and the conditions are first separated.
    Then, each conditions are converted.
    They are then put back together in their respective order.
    """
    # Saving the order of the logical operators
    logical_operators = get_word_compile("and|or", conditions)
    operators_order = logical_operators.findall(conditions)

    # Turn conditions into an array, ignoring the operators
    conditions = separate_on_word("and|or", conditions)
    conditions = convert_conditions(conditions)

    # Stack them into a string
    full_conditions = ""
    for i in range(len(operators_order)):
        full_conditions += conditions[i]
        full_conditions += " "
        full_conditions += operators_order[i]
        full_conditions += " "
    full_conditions += conditions[-1]

    return full_conditions


def transform_if_statement(lines):
    """Transforms the if-statement.

    Key arguments:
    -- lines: list of dict ([{"content": x, "indents": y}])

    Returns:
    -- List of dict ([{"content": x, "indents": y}])
    """
    converted_lines = []

    #  Establish the first line
    first_if_line = lines.pop(0)
    initial_indent = first_if_line["indents"]
    line_str = first_if_line["content"]
    conditions = line_str.split(' ', 1)[1].strip()
    conditions = conditions[:-1]  # Remove the semi-colon

    conditions = transform_all_conditions(conditions)

    # Append first line
    converted_first_line = {
        "content": "IF " + conditions,
        "indents": initial_indent
    }
    converted_lines.append(converted_first_line)

    # 'THEN' statement
    then_call = {
        "content": "THEN",
        "indents": initial_indent + 4
    }
    converted_lines.append(then_call)

    # The lines that go in the 'THEN' block
    then_block = []
    while (len(lines) > 0 and
            (re.match(r'^else:', lines[0]["content"]) is None or
             lines[0]["indents"] != initial_indent)):
        current_line = lines.pop(0)
        line_str = " " * current_line["indents"] + current_line["content"]
        then_block.append(line_str)

    converter = PseudocodeConverter(then_block)
    then_statements = converter.get_converted_lines()

    for statement in then_statements:
        # Add an indent for conventions
        statement["indents"] = statement["indents"] + 4
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

        pseudocodeConverter = PseudocodeConverter(else_block)
        else_statements = pseudocodeConverter.get_converted_lines()

        for statement in else_statements:
            # Add an indent for conventions
            statement["indents"] = statement["indents"] + 4
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
        words = separate_on_word("_", text)
        new_text = words.pop(0)
        for word in words:
            new_text += word.capitalize()

        return new_text

    return text


class PseudocodeConverter:
    converted_lines = []

    def __init__(self, lines):
        self.converted_lines = []
        while len(lines) > 0:
            # Split indent information and content
            current_line = self.get_current_line(lines)

            if test_print(current_line["content"]) is not None:
                current_line["content"] = test_print(
                    current_line["content"]
                )
                self.converted_lines.append(current_line)
            elif test_assignment(current_line["content"]) is not None:
                for i in test_assignment(current_line["content"]):
                    converted_line = {
                        "content": i,
                        "indents": current_line["indents"]
                    }
                    self.converted_lines.append(converted_line)
            elif test_if_statement(current_line["content"]):
                # Check if got elif

                # Initialize if_block
                if_block = []
                if_block.append(current_line)

                start_block_indent = current_line["indents"]

                # Populate the if_block
                block_check = True
                while block_check and len(lines) > 0:
                    current_line = self.get_current_line(lines)
                    if in_if_block(current_line, start_block_indent):
                        if_block.append(current_line)
                    else:
                        block_check = False

                # Convert the if_block into pseudocode
                converted_lines = transform_if_statement(
                    if_block
                )

                for line in converted_lines:
                    self.converted_lines.append(line)

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
        --converted_lines: dict ({"content": x, "indents": y})
        """
        # print("get_converted_lines", self.converted_lines)
        return self.converted_lines
