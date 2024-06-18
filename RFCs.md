### `Field` Syntax and Parsing
#### Field Syntax - (RFC9112#section-5):

`field-line   = field-name ":" OWS field-value OWS`

#### Field Line Parsing - (RFC9110#section-5.5):

- Multiple (duplicate) Field Names 
The get concatinated together.
The proxy should not change the order unless multiple definitions are allowed, sender MUST NOT do this if not allowed - (RFC9110#section-5.2 and RFC9110#section-5.3)

#### field-value (RFC#9110#section-5.5):
- must be ASCII
- CR,LF,NUL are invalid!
- singleton fields -> only support one value
- list-based fields -> allow multiple field values

#### Parameters (rfc9110#section-5.6.6)
- parameter name is case insensitive!
- whitespace is not allowed around "="

### `Content-Type` Header
- Content-Type header SHOULD always be used. - (RFC9110)
- If not used, the server tries to guess based on body or treat it like octet-stream - (RFC2046#section-4.5.1 - RFC9110#section-8.3)
- No Whitespace between fieldname and colon e.g. `Content-Type :` - (RFC9112)
- is a singleton field BUT (RFC9110#section-8.3)
- it is sometimes incorrectly generated multiple times, resulting in a combined field value that appears to be a list. Recipients often attempt to handle this error by using the last syntactically valid member of the list, leading to potential interoperability and security issues if different implementations have different error handling behaviors.
- If the Content-Type value is any of the multipart/*, boundary parameter is required. - (RFC7578#section-8)

### Media-Type (RFC9110#section-8.3):
- type/subtype
- both case insensitive!
- charset is case insensitive
```
All these are allowed:
  Text/HTML;Charset="utf-8"
  text/html; charset="utf-8"
  text/html;charset=UTF-8
```
#### Multipart Media-Type (RFC2046#section5-1)
- No header field is required in the body part
- header names only that begin with "Content-" have meaning. All other header fields MAY be ignored. Although they SHOULD generally be retained
- In Content-Transfer-Encoding field [RFC 2045], no encoding other than "7bit", "8bit", or "binary" is valid

#### Boundary:
- value between 1 to 70 chars (no space)
- in the header after content type. if boundary value has ":" or ";" or any weird character you should wrap it in double quotes
- Boundary delimiters must not appear within the encapsulated material, and must be no longer than 70 characters, not counting the two leading hyphens e.g. `--gc0pJq0M:08jU534c0p`

### Parameter Value Continuation (RFC2231#section-3)
- definition: asterisk character (*) character followed by a decimal count
- numbers start from 0 and increment by 1 (decimal values only)
- leading zeroes nor gaps are allowed
