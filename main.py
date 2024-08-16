import asyncio
import subprocess

from aiohttp import web

from src.app_badges import get_app_badges
from src.constants import APP_BADGES_REFRESH_SEC, HTTP_PORT, WS_PORT
from src.http_server import http_server
from src.websocket import send_to_ws_client, simple_bar_ws


async def schedule_check_badges():
    while True:
        try:
            app_badges = get_app_badges()
            await send_to_ws_client("app-badges", None, {"action": "refresh", "data": app_badges})
        except Exception as err:
            print("Error: schedule_check_badges", err)
        finally:
            await asyncio.sleep(APP_BADGES_REFRESH_SEC)


def refresh_uebersicht():
    print("Refreshing Uebersicht")
    try:
        subprocess.run(["/usr/bin/osascript", "-e", 'tell application id "tracesOf.Uebersicht" to refresh'])
        print("Refreshed Uebersicht")
    except Exception as err:
        print(err)
        print("Failed to refresh Uebersicht")


async def start_app_runner(app: web.Application, name: str, port: int, callback=None):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=port)
    await site.start()
    print(f"Started {name} at :{port}")

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
