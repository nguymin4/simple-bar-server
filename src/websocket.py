from aiohttp import web

_WS_CLIENTS: dict[str, web.WebSocketResponse] = {}


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
        _WS_CLIENTS[f"{target}-{user_widget_index}"] = ws

    return ws


def send_to_ws_client(target: str, user_widget_index="", payload=None):
    key = f"{target}-{user_widget_index}"
    if key in _WS_CLIENTS:
        _WS_CLIENTS[key].send_json(payload)


simple_bar_ws = web.Application()
simple_bar_ws.add_routes([web.get("/", websocket_handler)])
