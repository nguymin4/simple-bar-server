from aiohttp import web

from src.constants import AEROSPACE, AEROSPACE_ACTIONS, WIDGET_ACTIONS, WIDGETS
from src.websocket import send_to_ws_client


async def handle_aerospace(request: web.Request):
    kind = request.match_info.get("kind")
    if kind not in AEROSPACE:
        return web.Response(status=400, text=f"Unknown aerospace kind {kind}")

    action = request.match_info.get("action")
    if action not in AEROSPACE_ACTIONS:
        return web.Response(status=400, text=f"Unknown widget action {action}")

    body = {}
    if request.has_body:
        body = await request.json()

    await send_to_ws_client(kind, None, {"action": action, "data": body})
    return web.Response(status=200)


async def handle_widget(request: web.Request):
    kind = request.match_info.get("kind")
    if kind not in WIDGETS:
        return web.Response(status=400, text=f"Unknown widget kind {kind}")

    action = request.match_info.get("action")
    if action not in WIDGET_ACTIONS:
        return web.Response(status=400, text=f"Unknown widget action {action}")

    user_widget_index = request.match_info.get("user_widget_index")
    await send_to_ws_client(kind, user_widget_index, {"action": action})
    return web.Response(status=200)


http_server = web.Application()
http_server.add_routes(
    [
        web.post("/aerospace/{kind}/{action}", handle_aerospace),
        web.post("/widget/{kind}/{action}/{user_widget_index}", handle_widget),
    ]
)
