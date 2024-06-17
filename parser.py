from enum import Enum
import re
from typing import Final

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

_MEDIA_TYPE_RE: Final[str] = rf"(?P<type>{_TOKEN_RE})/(?P<subtype>{_TOKEN_RE})(?P<parameters>{_PARAMETERS_RE})"

_PARAMETER_PAT: Final[re.Pattern[bytes]] = re.compile(_PARAMETER_RE.encode("ascii"))
_MEDIA_TYPE_PAT: Final[re.Pattern[bytes]] = re.compile(_MEDIA_TYPE_RE.encode("ascii"))

def parse_media_type(media_type: bytes) -> tuple[bytes, bytes, list[tuple[bytes, bytes]]]:
    """
    Takes as input the value of a Content-Type header.
    Spits out the type, subtype, and a list of key:value pairs corresponding to the parameters.
    """
    
    m: re.Match[bytes] | None = re.fullmatch(_MEDIA_TYPE_PAT, media_type)
    if m is None:
        raise ValueError

    parameter_bytes: bytes = m["parameters"]

    params: list[tuple[bytes, bytes]] = []
    while len(parameter_bytes) > 0:
        param: re.Match[bytes] | None = re.match(_PARAMETER_PAT, parameter_bytes)
        if param is None:
            raise ValueError
        params.append((param[1], param[2]))
        parameter_bytes = parameter_bytes[param.end():]

    return m["type"], m["subtype"], params
