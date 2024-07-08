import aiohttp
import aiohttp.web
from aiohttp.web_protocol import RequestPayloadError
from aiohttp.abc import CIMultiDict

from media_type import parse_media_type, normalize_multipart_body, MediaType

# Change me!
_BACKEND: str = "https://127.0.0.1:8000"

async def respond(request) -> aiohttp.web.Response:
    try:
        body = await request.content.read()
    except RequestPayloadError:
        return aiohttp.web.Response(status=400, reason="Bad message body.")

    if "Content-Type" in request.headers:
        orig_ct: str = request.headers["Content-Type"]
        if not orig_ct.isascii():
            return aiohttp.web.Response(status=400, reason="Non-ASCII bytes in Content-Type.")
        try:
            new_ct: str = parse_media_type(orig_ct.encode("ascii")).serialize().decode("ascii")
        except ValueError:
            return aiohttp.web.Response(status=400, reason="Bad Content-Type.")

    headers: CIMultiDict = CIMultiDict()
    headers.extend(request.headers)
    headers["Content-Type"] = new_ct

    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=request.method,
            url=request.url,
            data=body,
            headers=headers,
            cookies=request.cookies,
        ) as response:
            print(response)
            return aiohttp.web.Response(
                body=(await response.read()),
                status=response.status,
                headers=response.headers,
            )
    return aiohttp.web.Response(status=500, reason="This should never happen!")
        

app = aiohttp.web.Application()
app.add_routes([aiohttp.web.route("*", "/{unused_required_name:.*}", respond)])

aiohttp.web.run_app(app, port=8999)
