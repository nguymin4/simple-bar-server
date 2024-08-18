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
logger = logging.getLogger(__name__)


async def schedule_check_badges():
    try:
        while True:
            try:
                app_badges = get_app_badges()
                await send_to_ws_client("app-badges", None, {"action": "refresh", "data": app_badges})
            except Exception:
                logger.warning("schedule_check_badges", exc_info=True)
            finally:
                await asyncio.sleep(APP_BADGES_REFRESH_SEC)
    except asyncio.CancelledError:
        logger.info("schedule_check_badges() cancelled")
    except Exception as e:
        logger.info(f"schedule_check_badges() got: {e}")

    logger.info("schedule_check_badges() exited")


def refresh_uebersicht():
    logger.info("Refreshing Uebersicht ...")
    try:
        subprocess.run(["/usr/bin/osascript", "-e", 'tell application id "tracesOf.Uebersicht" to refresh'])
        logger.info("Refreshed Uebersicht")
    except Exception:
        logger.warning("Failed to refresh Uebersicht", exc_info=True)


async def start_app_runner(app: web.Application, name: str, port: int, callback=None):
    runner = web.AppRunner(app, handle_signals=True)
    await runner.setup()
    site = web.TCPSite(runner, shutdown_timeout=2, port=port)
    await site.start()
    logger.info(f"Started {name} at :{port}")

    if callback:
        callback()


async def main():
    try:
        await asyncio.gather(
            start_app_runner(http_server, name="http_server", port=HTTP_PORT),
            start_app_runner(simple_bar_ws, name="simple_bar_ws", port=WS_PORT, callback=refresh_uebersicht),
            schedule_check_badges(),
        )
    except asyncio.CancelledError:
        logger.info("main() cancelled")
    except Exception as e:
        logger.error(f"main() got: {e}")
    logger.info("main() exited")


if __name__ == "__main__":
    asyncio.run(main())
