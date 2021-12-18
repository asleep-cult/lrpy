from __future__ import annotations

import builtins
import codecs
from typing import Optional

from .parser.exceptions import InvalidEncodingDeclarationError
from .stringreader import StringReader


def normalize_encoding(endocing):
    # https://github.com/python/cpython/blob/main/Lib/tokenize.py#L286

    sanitized = endocing[:12].lower().replace('_', '-')
    if sanitized == 'utf-8' or sanitized.startswith('utf-8-'):
        return 'utf-8'
    else:
        encodings = ('latin-1', 'iso-8859-1', 'iso-latin-1')
        if sanitized in encodings or sanitized.startswith(encodings):
            return 'iso-8859-1'

    return endocing


def parse_encoding_declaration(line: bytes, *, bom: bool = False) -> Optional[str]:
    try:
        reader = StringReader(line.decode('utf-8'))
    except UnicodeDecodeError:
        raise InvalidEncodingDeclarationError(
            'The encoding declaration is not a valid UTF-8 sequence'
        )

    reader.skip_whitespace()
    if (
        not reader.expect('#')
        or not reader.skip_expect('coding')
        or not reader.expect((':', '='))
    ):
        return None

    reader.skip_whitespace()

    encoding = normalize_encoding(reader.accumulate(
        lambda char: char.isalnum() or char == '_' or char == '-' or char == '.'
    ))

    try:
        codec = codecs.lookup(encoding)
    except LookupError:
        raise InvalidEncodingDeclarationError(
            f'The encoding declaration refers to an unknown encoding: {encoding!r}'
        )
    else:
        if not getattr(codec, '_is_text_encoding', True):
            raise InvalidEncodingDeclarationError(
                f'The encoding declaration refers to a non-text encoding: {encoding!r}'
            )

    if bom:
        if encoding != 'utf-8':
            raise InvalidEncodingDeclarationError(
                f'Encoding mismatch for file with UTF-8 BOM: {encoding!r}'
            )
        encoding = 'utf-8-sig'

    return encoding


def open(file, mode, encoding='utf-8', *args, **kwargs):
    fp = builtins.open(file, mode, *args, **kwargs)

    line = fp.readline()
    if not isinstance(line, bytes):
        raise TypeError(f'readline() should return bytes, not {line.__class__.__name__!r}')

    if line.startswith(codecs.BOM_UTF8):
        line = line[len(codecs.BOM_UTF8):]
        default = 'utf-8-sig'
    else:
        default = encoding

    if not line:
        return default

    if line.strip() == b'#':
        line = fp.readline()
        if not isinstance(line, bytes):
            raise TypeError(f'readline() should return bytes, not {line.__class__.__name__!r}')

    encoding = parse_encoding_declaration(line)
    if encoding is not None:
        return encoding

    return default
