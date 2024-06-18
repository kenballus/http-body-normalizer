import re
from typing import Final, TypeGuard
from dataclasses import dataclass

from mime_type import MIME_TOP_LEVEL_TYPES, MIME_SUBTYPES

#  quoted-string  = DQUOTE *( qdtext / quoted-pair ) DQUOTE
#  qdtext         = HTAB / SP / %x21 / %x23-5B / %x5D-7E / obs-text
#  quoted-pair    = "\" ( HTAB / SP / VCHAR / obs-text )
#  VCHAR          =  %x21-7E
#  obs-text       = %x80-FF
#  parameters      = *( OWS ";" OWS [ parameter ] )
#  parameter       = parameter-name "=" parameter-value
#  parameter-name  = token
#  OWS            = *( SP / HTAB )
#  token          = 1*tchar
#  tchar          = "!" / "#" / "$" / "%" / "&" / "'" / "*"
#                 / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~"
#                 / DIGIT / ALPHA
#  parameter-value = ( token / quoted-string )
#  media-type = type "/" subtype parameters
#  type       = token
#  subtype    = token

_TOKEN_RE: Final[str] = r"[!#$%&'*+\-.^_`|~A-Za-z0-9]+"

_QUOTED_STRING_RE: Final[str] = r'"(?:[\t \x21\x23-\x5b\x5d-\x7e\x80-\xff]|\\[\t \x21-\x7e\x80-\xff])*"'

_PARAMETER_VALUE_RE: Final[str] = rf"(?:{_TOKEN_RE}|{_QUOTED_STRING_RE})"

# These are a little different from the RFC rules, but are functionally equivalent.
_PARAMETER_RE: Final[str] = rf"[ \t]*;[ \t]*(?:({_TOKEN_RE})=({_PARAMETER_VALUE_RE}))?"

_PARAMETERS_RE: Final[str] = rf"(?:{_PARAMETER_RE})*"

_MEDIA_TYPE_RE: Final[str] = (
    rf"(?P<type>{_TOKEN_RE})/(?P<subtype>{_TOKEN_RE})(?P<parameters>{_PARAMETERS_RE})"
)

_PARAMETER_PAT: Final[re.Pattern[bytes]] = re.compile(_PARAMETER_RE.encode("ascii"))
_MEDIA_TYPE_PAT: Final[re.Pattern[bytes]] = re.compile(_MEDIA_TYPE_RE.encode("ascii"))


def is_bytes_list(l: list) -> TypeGuard[list[bytes]]:
    return all(isinstance(thing, bytes) for thing in l)


_MAX_CONTINUATION_INDEX: Final[int] = 100  # Picked arbitrarily. Feel free to increase if necessary.


@dataclass
class MediaType:
    type_: bytes
    subtype: bytes
    parameters: list[tuple[bytes, bytes]]

    def __post_init__(self):
        if self.type_ not in MIME_TOP_LEVEL_TYPES:
            raise ValueError("Unrecognized MIME type.")
        if self.subtype not in MIME_SUBTYPES[self.type_]:
            raise ValueError("Unrecognized MIME subtype.")

def parse_media_type(media_type: bytes) -> MediaType:
    """
    Takes as input the value of a Content-Type header.
    Spits out the type, subtype, and a list of key:value pairs corresponding to the parameters.
    """

    m: re.Match[bytes] | None = re.fullmatch(_MEDIA_TYPE_PAT, media_type)
    if m is None:
        raise ValueError("Media type does not parse!")

    # Case-insensitivity specified in RFC 9110 8.3.1
    type_: bytes = m["type"].lower()
    subtype: bytes = m["subtype"].lower()
    parameter_bytes: bytes = m["parameters"]

    raw_params: list[tuple[bytes, bytes]] = []
    while len(parameter_bytes) > 0:
        m = re.match(_PARAMETER_PAT, parameter_bytes)
        assert m is not None
        raw_params.append((m[1], m[2]))
        parameter_bytes = parameter_bytes[m.end() :]

    # Parse RFC 2231-style continuations in parameters.
    params_with_continuation: dict[bytes, list[bytes | None] | bytes] = {}
    for raw_key, raw_value in raw_params:
        # Note: RFC 2231 requires that the first digit be nonzero. We relax this on the input side, but not on the output side.
        m = re.fullmatch(rb"\A(?P<key>.*)\*(?P<index>\d+)\Z", raw_key)
        if m is not None:
            key: bytes = m["key"]
            index: int = int(m["index"])

            if key not in params_with_continuation:
                params_with_continuation[key] = []

            values: list[bytes | None] | bytes = params_with_continuation[key]
            if isinstance(values, bytes):
                raise ValueError("Duplicate parameter! (once with continuation, once without)")
            if index > _MAX_CONTINUATION_INDEX:
                raise ValueError("Continuation index too large!")
            # Extend the list to match the index, if necessary
            while len(values) < index + 1:
                values.append(None)
            if values[index] is not None:
                raise ValueError("Repeated continuation index!")
            values[index] = raw_value
        else:
            if raw_key in params_with_continuation:
                raise ValueError("Duplicate parameter!")
            params_with_continuation[raw_key] = raw_value

    params: list[tuple[bytes, bytes]] = []
    for k, v in params_with_continuation.items():
        if isinstance(v, bytes):
            params.append((k, v))
        elif isinstance(v, list):
            if not is_bytes_list(v):
                raise ValueError("Missing continuation index!")
            params.append((k, b"".join(v)))

    return MediaType(type_, subtype, params)
