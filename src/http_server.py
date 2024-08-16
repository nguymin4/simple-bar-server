from aiohttp import web

from src.constants import WIDGET_ACTIONS, WIDGETS
from src.websocket import send_to_ws_client


async def handle_aerospace(request: web.Request):
    return web.Response(status=200)


async def handle_widget(request: web.Request):
    kind = request.match_info.get("kind")
    if kind not in WIDGETS:
        return web.Response(status=400, text=f"Unknown widget kind {kind}")

    action = request.match_info.get("action")
    if action not in WIDGET_ACTIONS:
        return web.Response(status=400, text=f"Unknown widget action {action}")

    user_widget_index = request.match_info.get("user_widget_index")
    send_to_ws_client(kind, user_widget_index, {"action": action})


http_server = web.Application()
http_server.add_routes(
    [
        web.post("/aerospace/{kind}/{action}", handle_aerospace),
        web.post("/widget/{kind}/{action}/{user_widget_index}", handle_widget),
    ]
)

if __name__ == "__main__":
    web.run_app(http_server)
