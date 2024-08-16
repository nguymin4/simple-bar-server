import asyncio
import subprocess

from aiohttp import web

from src.dock_badges import get_badges
from src.http_server import http_server
from src.websocket import simple_bar_ws

HTTP_PORT = 7776
WS_PORT = 7777
BADGES_REFRESH_SEC = 10


async def schedule_check_badges():
    while True:
        app_badges = get_badges()
        print(app_badges)
        await asyncio.sleep(BADGES_REFRESH_SEC)


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
