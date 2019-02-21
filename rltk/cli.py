import sys


SLIENTLY_ACCEPT_ALL_DEFAULT_VALUES = False


def prompt(text: str, *args, new_line: bool = True, **kwargs):
    """
    Prompt in terminal (stdout).

    Args:
        text (str): Text.
        *args: More text.
        new_line (bool, optional): End with a new line. Defaults to True.
        **kwargs: Other key word arguments used by :py:meth:`print`.
    """
    line_end = '\n' if new_line else ''
    print(text, *args, file=sys.stdout, end=line_end, **kwargs)
    sys.stdout.flush()


def select(text: str, cases: list, default: int = None, case_sensitive: bool = False):
    """
    Let user select one of the cases.

    Args:
        text (str): Text.
        cases (list[tuple]): Cases, should be list of tuples. Each tuple is in form `('display text', 'user's input')`.
                        For example, `[('(Y)es, 'y'), ('(N)o', 'n')]`.
        default (int, optional): Default case index in `cases`. Empty or space is treated as default case.
                            None means no default case. Defaults to None.
        case_sensitive (bool, optional): If user's input is case sensitive, defaults to False.

    Returns:
        str: User's input.
    """
    prompt(text)
    case_text = []
    for idx, c in enumerate(cases):
        if default is not None and idx == default:
            case_text.append('[{}]'.format(c[0]))
        else:
            case_text.append('{}'.format(c[0]))
    prompt(' / '.join(case_text))
    valid_cases = [c[1] for c in cases]
    if default is not None:
        valid_cases.append('')
    if not case_sensitive:
        valid_cases = list(map(lambda x: x.lower(), valid_cases))

    while True:
        user_input = ''
        if not SLIENTLY_ACCEPT_ALL_DEFAULT_VALUES or default is None:
            user_input = input().strip()
            if not case_sensitive:
                user_input = user_input.lower()
            if user_input not in valid_cases:
                prompt('Invalid input, please retry')
                continue

        if user_input == '' and default is not None:
            return cases[default][1]
        return user_input


def confirm(text: str, default: bool = None):
    """
    Let user choose Yes or No.

    Args:
        text (str): Text.
        default (bool, optional): True sets Yes as default case, False sets No. None means no default case.
                                Defaults to None.

    Returns:
        bool: True means Yes, False means No.
    """
    if default is not None:
        default = 0 if default else 1
    return select(text, cases=[('(Y)es', 'y',), ('(N)o', 'n')], default=default, case_sensitive=False) == 'y'


class Progress(object):
    """
    Progress status.

    Args:
        format_ (str, optional): Format of text.
        start (str, optional): Text while starting.
        end (str, optional): Text while ending.

    Note:

        Please use in `with` statement::

            with rltk.cli.progress(format_='{}%') as p:
                for i in range(11):
                    time.sleep(0.5)
                    p.update(i * 10)

    """

    def __init__(self, format_: str = '{}', start: str = 'Starting...', end: str = 'Done!'):
        self._format = format_
        self._prev_len = 0
        self._start = start
        self._end = end

    def update(self, *args):
        """
        Update progress.

        Args:
            *args: Arguments which will be formatted by `format_`.
        """
        text = self._format.format(*args)

        # clean up
        prompt('\r' + ' ' * self._prev_len, new_line=False)

        # overwrite
        prompt('\r' + text, new_line=False)
        self._prev_len = len(text)

    def __enter__(self):
        """
        Start prompt.
        """
        if self._start:
            prompt(self._start, new_line=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        End prompt.
        """
        # clean up
        prompt('\r' + ' ' * self._prev_len, new_line=False)

        if self._end:
            prompt('\r' + self._end, new_line=False)

        # new line
        prompt('')


progress = Progress


def input_(text: str, default: str = None, type_: type = str):
    """
    Input.

    Args:
        text (str): Text.
        default (str, optional): Default value. Defaults to None which means no default value.
        type_ (type, optional): Type of input value, defaults to `str`.

    Returns:
        object: User input in type `type_`.

    Note:
        Make sure default value can be converted by `type_`, otherwise exception will be raised.
    """
    prompt(text)

    while True:
        if not SLIENTLY_ACCEPT_ALL_DEFAULT_VALUES or default is None:
            user_input = input().strip()
            try:
                return type_(user_input)
            except:
                prompt('Invalid input, please retry')
        else:
            return type_(default)

