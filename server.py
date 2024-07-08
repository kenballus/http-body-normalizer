import aiohttp
import aiohttp.web
from aiohttp.web_protocol import RequestPayloadError
from aiohttp.abc import CIMultiDict
from yarl import URL

from media_type import parse_media_type, normalize_multipart_body, MediaType

# Change this:
_HOST: str = "localhost"
# And this:
_PORT: int = 8000

async def respond(request) -> aiohttp.web.Response:
    try:
        body = await request.content.read()
    except RequestPayloadError:
        return aiohttp.web.Response(status=400, reason="Bad message body.")

    headers: CIMultiDict = CIMultiDict()
    headers.extend(request.headers)

    if "Content-Type" in request.headers:
        orig_ct: str = request.headers["Content-Type"]
        if not orig_ct.isascii():
            return aiohttp.web.Response(status=400, reason="Non-ASCII bytes in Content-Type.")
        try:
            headers["Content-Type"] = parse_media_type(orig_ct.encode("ascii")).serialize().decode("ascii")
        except ValueError:
            return aiohttp.web.Response(status=400, reason="Bad Content-Type.")

    try:
        url: URL = request.url.with_host(_HOST).with_port(_PORT)
    except ValueError:
        return aiohttp.web.Response(status=400, reason="Invalid URL.")

    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=request.method,
            url=url,
            headers=headers,
            data=body,
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
