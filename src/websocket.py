import logging
from collections import defaultdict

import aiohttp
from aiohttp import web

from src.constants import DEFAULT_USER_WIDGET_INDEX

logger = logging.getLogger(__name__)

simple_bar_ws = web.Application()
websockets = web.AppKey("websockets", dict[str, list[web.WebSocketResponse]])
simple_bar_ws[websockets] = defaultdict(list)


async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    target = request.rel_url.query.get("target")
    user_widget_index = request.rel_url.query.get("userWidgetIndex", DEFAULT_USER_WIDGET_INDEX)

    if not target:
        await ws.close()
        logger.warning("ws connection closed due to missing ?target=")
        return

    key = f"{target}-{user_widget_index}"
    request.app[websockets][key].append(ws)
    logger.info(f"new ws connection opened for {key}")

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == "close":
                    await ws.close()
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.info(f"ws connection closed with exception {ws.exception()}")
    finally:
        request.app[websockets][key].remove(ws)

    logger.info(f"ws connection closed for {key}")
    return ws


async def send_to_ws_client(target: str, user_widget_index=None, payload=None):
    key = f"{target}-{user_widget_index or DEFAULT_USER_WIDGET_INDEX}"
    ws_connections = simple_bar_ws[websockets][key]

    if not ws_connections:
        logger.warning(f"no ws connection found for {key} {payload}")
        return

    for ws in ws_connections:
        try:
            await ws.send_json(payload)
        except Exception as err:
            logger.warning("send_to_ws_client %s", err)


async def on_shutdown(app: web.Application):
    logger.info("simple_bar_ws shutting down...")
    for ws_connections in app[websockets].values():
        for ws in ws_connections:
            await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY, message="Server shutdown")
    logger.info("simple_bar_ws shut down.")


simple_bar_ws.on_shutdown.append(on_shutdown)
simple_bar_ws.add_routes([web.get("/", websocket_handler)])
