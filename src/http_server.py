from aiohttp import web


async def handle(request: web.Request):
    name = request.match_info.get("name", "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


http_server = web.Application()
http_server.add_routes([web.get("/{name}", handle)])

if __name__ == "__main__":
    web.run_app(http_server)
