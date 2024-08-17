import logging

from aiohttp import web

_WS_CLIENTS: dict[str, web.WebSocketResponse] = {}


async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    target = request.rel_url.query.get("target")
    user_widget_index = request.rel_url.query.get("userWidgetIndex", "")
    logging.info("websocket new connection opened for %s %s", target, user_widget_index)

    if not target:
        await ws.close()
        logging.warning("websocket connection not kept due to missing ?target=")
        return

    _WS_CLIENTS[f"{target}-{user_widget_index}"] = ws
    async for msg in ws:
        if msg.type == web.WSMsgType.close:
            break

    return ws


async def send_to_ws_client(target: str, user_widget_index=None, payload=None):
    key = f"{target}-{user_widget_index or ''}"
    try:
        if key in _WS_CLIENTS:
            await _WS_CLIENTS[key].send_json(payload)
        else:
            logging.warning(f"ws client not found for {target} {payload}")
    except Exception as err:
        logging.warning("send_to_ws_client %s", err)


simple_bar_ws = web.Application()
simple_bar_ws.add_routes([web.get("/", websocket_handler)])
