1. Write a validator for the Content-Type header. (See RFC 9110, section 8.3)
    Take into account RFC 2231
    Disallow missing boundary parameter
    Disallow empty string boundary parameter

2. Content-Types we need to support (at least):
    (Source: https://www.iana.org/assignments/media-types/media-types.xhtml)
    multipart
        form-data
        mixed
        related
    application
        xml
        json
        x-www-form-urlencoded

3. Character sets
    Probably a whitelist
    Need to find a standard that lays out what the valid charsets are
in Content-Type.

4. Need to figure out how to handle quoted boundaries.
    Some WAFs fail on them
    But RFC 2046 recommends quoting boundaries.
(https://www.rfc-editor.org/rfc/rfc2046.html#section-5.1.1)
