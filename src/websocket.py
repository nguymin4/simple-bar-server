import logging
import weakref

import aiohttp
from aiohttp import web

from src.constants import DEFAULT_USER_WIDGET_INDEX

logger = logging.getLogger(__name__)

simple_bar_ws = web.Application()
websockets = web.AppKey("websockets", weakref.WeakValueDictionary[str, web.WebSocketResponse])
simple_bar_ws[websockets] = weakref.WeakValueDictionary()


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
    logger.info(f"websocket new connection opened for {key}")

    request.app[websockets][key] = ws
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == "close":
                    await ws.close()
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.info(f"ws connection closed with exception {ws.exception()}")
    finally:
        del request.app[websockets][key]

    logger.info(f"websocket connection closed for {key}")
    return ws


async def send_to_ws_client(target: str, user_widget_index=None, payload=None):
    try:
        ws_clients = simple_bar_ws[websockets]
        key = f"{target}-{user_widget_index or DEFAULT_USER_WIDGET_INDEX}"
        if key in ws_clients:
            await ws_clients[key].send_json(payload)
        else:
            logger.warning(f"ws client not found for {key} {payload}")
    except Exception as err:
        logger.warning("send_to_ws_client %s", err)


async def on_shutdown(app: web.Application):
    logger.info("simple_bar_ws shutting down...")
    for ws in app[websockets].values():
        await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY, message="Server shutdown")
    logger.info("simple_bar_ws shut down.")


simple_bar_ws.on_shutdown.append(on_shutdown)
simple_bar_ws.add_routes([web.get("/", websocket_handler)])
