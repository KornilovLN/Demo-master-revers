from pathlib import Path
import six

def create_dir(path, parent=True):
    p = Path(path)
    p = p.parent if parent else p
    if not p.exists():
        p.mkdir(mode=0o777, parents=True)


def is_ascii(text):
    if isinstance(text, six.string_types):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    else:
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    return True


def is_letter(text):
    return len(text) == 1


def if_cyrillic(text):
    return 0x0400 <= ord(text[0]) <= 0x04ff

def like_cyrillic(text):
    ABC = 'ETOPAHKXCBM. '
    return all(map(lambda a: a in ABC, text))

def need_tr(text):
    return (not is_ascii(text) or like_cyrillic(text)) and not (is_letter(text) and not if_cyrillic(text))