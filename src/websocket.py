from aiohttp import web

_WS_CLIENTS = {}


async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    target = request.rel_url.query.get("target")
    user_widget_index = request.rel_url.query.get("userWidgetIndex", "")
    print("websocket new connection opened for", target, user_widget_index)

    if not target:
        await ws.close()
        simple_bar_ws.logger.info("websocket connection closed due to missing ?target=")
    else:
        # await ws.send_str(msg.data + "/answer")
        _WS_CLIENTS[f"{target}-{user_widget_index}"] = ws

    return ws


async def get_ws_client(target: str, user_widget_index=""):
    _WS_CLIENTS[f"{target}-{user_widget_index}"]


simple_bar_ws = web.Application()
simple_bar_ws.add_routes([web.get("/", websocket_handler)])
