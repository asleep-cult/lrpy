from __future__ import annotations

import builtins
import codecs
import io
from typing import Optional

from .parser.exceptions import InvalidEncodingDeclarationError
from .stringreader import StringReader


class EncodingDetector:
    def __init__(self, source: io.IOBase, default: str = 'utf-8') -> None:
        self.source = source
        self.default = default

    @property
    def comment(self) -> str:
        return '#'

    def is_encoding(self, char: str) -> bool:
        return char.isalnum() or char in '.-_'

    @staticmethod
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

    def readline(self) -> bytes:
        line = self.source.readline()
        if not isinstance(line, bytes):
            raise TypeError(f'readline() should return bytes, not {line.__class__.__name__}')

        return line

    def parse_declaration(self, line: bytes, *, bom: bool = False) -> Optional[str]:
        try:
            reader = StringReader(line.decode('utf-8'))
        except UnicodeDecodeError:
            raise InvalidEncodingDeclarationError(
                'The encoding declaration is not a valid UTF-8 sequence'
            )

        reader.skip_whitespace()

        for char in self.comment:
            if not reader.lookahead(lambda c: c == char):
                return None

        if (
            not reader.goto('coding')
            or not reader.lookahead(lambda c: c == ':' or c == '=')
        ):
            return None

        reader.skip_whitespace()
        encoding = reader.accumulate(self.is_encoding)

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

    def detect(self) -> str:
        line = self.readline()

        if line.startswith(codecs.BOM_UTF8):
            line = line[len(codecs.BOM_UTF8):]
            default = 'utf-8-sig'
            bom = True
        else:
            default = self.default
            bom = False

        if not line:
            return default

        if line.strip() == self.comment.encode():
            line = self.readline()

        encoding = self.parse_declaration(line, bom=bom)
        if encoding is not None:
            return encoding

        return default

    @classmethod
    def open(cls, file, mode='rb', encoding: str = 'utf-8', *args, **kwargs):
        fp = builtins.open(file, mode, *args, **kwargs)

        detector = cls(fp, default=encoding)
        return io.TextIOWrapper(fp, encoding=detector.detect())
