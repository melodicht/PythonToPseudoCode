import re


def get_word_compile(word, line):
    """Finds word in a line if not between single or double quotes.

    Key arguments:
    -- word: str
    -- line: str

    Returns:
    -- word_compile: re.compile type

    If searching for multiple words, put the OR operator '|' between them.
    For example "and|or".

    This function works for symbol-mixed-with-words strings.
    """
    # If words (or space) only
    if all(c.isalpha() or c.isspace() for c in word):
        word_compile = re.compile(
            rf'''\b(?:{word})\b(?=(?:[^"]*"[^"]*")*[^"]*$)(?=(?:[^']*'[^']*')*[^']*$)''',
            re.IGNORECASE
        )
        return word_compile
    else:
        symbol_compile = re.compile(
            rf'''({word})(?=(?:[^"]*"[^"]*")*[^"]*$)(?=(?:[^']*'[^']*')*[^']*$)'''
        )
        return symbol_compile


def check_if_word_exist(word, line):
    """Checks if a word/symbol exists in a line.

    Key arguments:
    -- word: str
    -- line: str

    Returns:
    -- bool
    """
    word_compile = get_word_compile(word, line)
    if word_compile.search(line) is not None:
        return True
    else:
        return False


line = "bananasplit"
print(check_if_word_exist("_", line))
