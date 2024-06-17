from aiohttp import web
from aiohttp.web_protocol import RequestPayloadError
from base64 import b64encode

async def respond(request):
    try:
        body = await request.content.read()
    except RequestPayloadError:
        return web.Response(status=400, reason="Bad message body.")
    content_type = request.headers.get("Content-Type")
    if content_type is None:
        content_type = "application/octet-stream"
    return web.Response(text=f"CT: {content_type}\nBody: {body}\n")


app = web.Application()
app.add_routes([web.route("*", "/{unused_required_name:.*}", respond)])

web.run_app(app, port=8000)
