import sys

SEPARATOR_LEN = 20


def prompt(text: str, *args, new_line: bool = True, **kwargs):
    line_end = '\n' if new_line else ''
    print(text, *args, file=sys.stdout, end=line_end, **kwargs)
    sys.stdout.flush()


def select(text: str, cases: list, default: int = None, case_sensitive: bool = False):
    """
    cases = [('(Y)es, 'y'), ('(N)o', 'n')]
    """
    prompt('=' * SEPARATOR_LEN)
    prompt(text)
    case_text = []
    for idx, c in enumerate(cases):
        if default is not None and idx == default:
            case_text.append('[{}]'.format(c[0]))
        else:
            case_text.append('{}'.format(c[0]))
    prompt(' / '.join(case_text) + '\n')
    valid_cases = [c[1] for c in cases]
    if default is not None:
        valid_cases.append('')
    if not case_sensitive:
        valid_cases = list(map(lambda x: x.lower(), valid_cases))

    while True:
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
    if default is not None:
        default = 1 if default else 0
    return select(text, cases=[('(Y)es', 'y',), ('(N)o', 'n')], default=default, case_sensitive=False) == 'y'


class Progress(object):

    def __init__(self, format_: str = '{}', start: str = 'Starting...', end: str = 'Done!'):
        self._format = format_
        self._prev_len = 0
        self._start = start
        self._end = end

    def update(self, *args):
        text = self._format.format(*args)

        # clean up
        prompt('\r' + ' ' * self._prev_len, new_line=False)

        # overwrite
        prompt('\r' + text, new_line=False)
        self._prev_len = len(text)

    def __enter__(self):
        if self._start:
            prompt(self._start, new_line=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._end:
            prompt('\r' + self._end, new_line=False)


def progress(*args, **kwargs):
    return Progress(*args, **kwargs)
