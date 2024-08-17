import asyncio
import logging
import subprocess

import coloredlogs
from aiohttp import web
from setproctitle import setproctitle

from src.app_badges import get_app_badges
from src.constants import APP_BADGES_REFRESH_SEC, HTTP_PORT, WS_PORT
from src.http_server import http_server
from src.websocket import send_to_ws_client, simple_bar_ws

setproctitle("simple-bar-server")

coloredlogs.install(level=logging.INFO)


async def schedule_check_badges():
    while True:
        try:
            app_badges = get_app_badges()
            await send_to_ws_client("app-badges", None, {"action": "refresh", "data": app_badges})
        except Exception:
            logging.warning("schedule_check_badges", exc_info=True)
        finally:
            await asyncio.sleep(APP_BADGES_REFRESH_SEC)


def refresh_uebersicht():
    logging.info("Refreshing Uebersicht ...")
    try:
        subprocess.run(["/usr/bin/osascript", "-e", 'tell application id "tracesOf.Uebersicht" to refresh'])
        logging.info("Refreshed Uebersicht")
    except Exception:
        logging.warning("Failed to refresh Uebersicht", exc_info=True)


async def start_app_runner(app: web.Application, name: str, port: int, callback=None):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=port)
    await site.start()
    logging.info(f"Started {name} at :{port}")

    if callback:
        callback()


async def main():
    await asyncio.gather(
        start_app_runner(http_server, name="http_server", port=HTTP_PORT),
        start_app_runner(simple_bar_ws, name="simple_bar_ws", port=WS_PORT, callback=refresh_uebersicht),
        schedule_check_badges(),
    )


if __name__ == "__main__":
    asyncio.run(main())
